from textual import on, work
from textual.app import Screen, ComposeResult
from textual.containers import Container
from textual.widgets import Header, DataTable, Button, Label, LoadingIndicator
from textual.css.query import NoMatches
from src.cos_client import COSClient
from .message_screen import MessageScreen
from .download_screen import DownloadScreen
from asyncio import sleep
import asyncio
from textual.worker import Worker
from .file_details_screen import FileDetailsScreen


class FileBrowserScreen(Screen):
    def __init__(self, config_name):
        super().__init__()
        self.config_name = config_name
        self.cos_client = COSClient(config_name)
        self.current_prefix = self.cos_client.prefix.rstrip('/')

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="file-container"):
            yield Label(f"当前路径：{self.current_prefix or '/'}", id="current-path")
            self.table = DataTable(id="file-table")
            self.table.add_columns("名称", "类型", "大小", "修改时间", "ETag")
            yield self.table
            with Container(id="download-button-container"):
                yield Button("上一级", id="parent")
                yield Button("进入", id="enter")
                yield Button("刷新", id="refresh")
                yield Button("详情", id="details")
                yield Button("下载", id="download")
                yield Button("删除", id="delete")
                yield Button("返回", id="back")

    def on_mount(self):
        self.load_files()

    @work
    async def load_files(self):
        self.table.clear()
        self.table.loading = True
        try:
            files = self.cos_client.list_objects()
            # 如果不在根目录，添加返回上级目录的选项
            if self.current_prefix != self.cos_client.prefix.rstrip('/'):
                parent_prefix = '/'.join(self.current_prefix.split('/')[:-1])
                self.table.add_row(
                    "..",
                    "目录",
                    "",
                    "",
                    ""
                )

            # 收集当前目录下的所有文件和子目录
            current_level_items = {}
            for file in files:
                if not file['Key'].startswith(self.current_prefix + '/'):
                    continue

                relative_path = file['Key'][len(
                    self.current_prefix):].lstrip('/')
                if not relative_path:
                    continue

                parts = relative_path.split('/')
                if len(parts) == 1 or (len(parts) > 1 and parts[0] not in current_level_items):
                    name = parts[0]
                    is_dir = len(parts) > 1 or int(file['Size']) == 0

                    if is_dir:
                        current_level_items[name] = {
                            'name': name,
                            'type': '目录',
                            'size': '',
                            'modified': '',
                            'etag': ''
                        }
                    else:
                        size = int(file['Size'])
                        if size < 1024:
                            size_str = f"{size} B"
                        elif size < 1024 * 1024:
                            size_str = f"{size/1024:.1f} KB"
                        elif size < 1024 * 1024 * 1024:
                            size_str = f"{size/1024/1024:.1f} MB"
                        else:
                            size_str = f"{size/1024/1024/1024:.1f} GB"

                        current_level_items[name] = {
                            'name': name,
                            'type': '文件',
                            'size': size_str,
                            'modified': file['LastModified'],
                            'etag': file['ETag'].strip('"')
                        }

            # 添加所有项目到表格
            for item in sorted(current_level_items.values(), key=lambda x: (x['type'] == '文件', x['name'])):
                self.table.add_row(
                    item['name'],
                    item['type'],
                    item['size'],
                    item['modified'],
                    item['etag']
                )

            self.table.loading = False

        except Exception as e:
            self.app.push_screen(MessageScreen(str(e)))
            raise

    @on(Button.Pressed, "#refresh")
    def refresh_files(self):
        self.load_files()

    @on(Button.Pressed, "#parent")
    def go_to_parent(self):
        if self.current_prefix != self.cos_client.prefix.rstrip('/'):
            self.current_prefix = '/'.join(self.current_prefix.split('/')[:-1])
            self.query_one("#current-path",
                           Label).update(f"当前路径：{self.current_prefix or '/'}")
            self.load_files()

    @on(Button.Pressed, "#enter")
    def enter_directory(self):
        selected = self.table.cursor_row
        if selected is None or selected >= len(self.row_keys):
            self.title = "No item selected"
            self.sub_title = "Please select an item to enter"
            return

        item_name = self.table.get_row_at(selected)[0]
        item_type = self.table.get_row_at(selected)[1]

        if item_type == "目录":
            if item_name == "..":
                self.go_to_parent()
            else:
                self.current_prefix = f"{self.current_prefix}/{item_name}".lstrip(
                    '/')
                self.query_one(
                    "#current-path", Label).update(f"当前路径：{self.current_prefix or '/'}")
                self.load_files()

    @on(Button.Pressed, "#delete")
    async def delete(self):
        self.delete_file()

    @work
    async def delete_file(self):

        selected = self.table.cursor_row
        if selected is None or selected >= len(self.row_keys):
            self.title = "No item selected"
            self.sub_title = "Please select an item to enter"
            return

        item_name = self.table.get_row_at(selected)[0]
        item_type = self.table.get_row_at(selected)[1]

        # 如果是返回上级目录的选项，不允许删除
        if item_name == "..":
            return

        key = f"{self.current_prefix}/{item_name}".lstrip('/')

        # 如果是目录，需要在末尾添加斜杠
        if item_type == "目录":
            key = f"{key}/"

        # 显示加载状态并禁用所有按钮
        self.table.loading = True
        for button in self.query("Button"):
            button.disabled = True

        self.query_one("#delete", Button).label = "删除中..."

        try:
            # 异步等待删除操作完成
            await asyncio.to_thread(self.cos_client.delete_object, key)
            # 删除完成后刷新文件列表
            self.load_files()

        except Exception as e:
            # 捕获异常并显示错误消息
            raise
            # self.app.push_screen(MessageScreen(str(e)))

        finally:
            # 隐藏加载状态并重新启用所有按钮

            for button in self.query("Button"):
                button.disabled = False
            self.query_one("#delete", Button).label = "删除"

            self.table.loading = False

    @on(Button.Pressed, "#download")
    def download_file(self):
        selected = self.table.cursor_row
        if selected is None:
            self.title = "No item selected"
            self.sub_title = "Please select an item to enter"
            return

        item_name = self.table.get_row_at(selected)[0]
        item_type = self.table.get_row_at(selected)[1]

        key = f"{self.current_prefix}/{item_name}".lstrip('/')

        if item_type == "目录":
            # 下载目录
            self.download_progress = 0
            self.download_cancelled = False

            self.app.push_screen(DownloadScreen(
                filename=key,
                on_cancel=self.download_cancelled,
                prefix=self.current_prefix,
                config_name=self.config_name,
                is_directory=True
            ))
        else:
            # 下载文件
            self.download_progress = 0
            self.download_cancelled = False

            self.app.push_screen(DownloadScreen(
                filename=key,
                on_cancel=self.download_cancelled,
                prefix=self.current_prefix,
                config_name=self.config_name
            ))

    @on(Button.Pressed, "#back")
    def back(self):
        self.app.pop_screen()

    @on(Button.Pressed, "#details")
    def show_details(self):
        selected = self.table.cursor_row
        if selected is None:
            self.title = "No item selected"
            self.sub_title = "Please select an item to enter"
            return

        item_name = self.table.get_row_at(selected)[0]
        key = f"{self.current_prefix}/{item_name}".lstrip('/')

        try:
            file_info = self.cos_client.get_object(key)
            self.app.push_screen(FileDetailsScreen(file_info, self.config_name))
        except Exception as e:
            self.app.push_screen(MessageScreen(str(e)))