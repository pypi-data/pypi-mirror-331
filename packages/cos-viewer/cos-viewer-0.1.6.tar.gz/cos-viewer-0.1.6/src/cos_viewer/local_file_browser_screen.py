from pathlib import Path
from textual import on
from textual.app import Screen, ComposeResult
from textual.containers import Container, Center
from textual.widgets import Header, DataTable, Button, Label
from src.config_manager import ConfigManager
from src.cos_client import COSClient
from .message_screen import MessageScreen
from datetime import datetime
from .upload_screen import UploadScreen

class LocalFileBrowserScreen(Screen):
    def __init__(self, config_name: str):
        super().__init__()
        self.config_name = config_name
        self.current_path = Path.cwd()
        self.row_keys = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="local-browser-container"):
            self.table = DataTable(id="local-file-table")
            self.table.add_columns("名称", "类型", "大小", "修改时间")
            yield self.table
            with Container(id="local-browser-buttons"):
                yield Button("上传", id="upload")
                yield Button("返回上级", id="back")
                yield Button("进入下一级", id="forward")
                yield Button("返回", id="cancel")

    def on_mount(self):
        self.refresh_files()

    def refresh_files(self):
        self.table.clear()
        self.row_keys = []

        # 添加目录
        try:
            for item in sorted(self.current_path.iterdir()):
                stats = item.stat()
                self.row_keys.append(item)
                self.table.add_row(
                    item.name,
                    "目录" if item.is_dir() else "文件",
                    "" if item.is_dir() else f"{stats.st_size:,} bytes",
                    datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    key=str(item)
                )
        except (PermissionError):
            self.app.push_screen(MessageScreen("无权限访问该目录"))
            
        except Exception as e:
            self.app.push_screen(MessageScreen(str(e)))
            

    @on(Button.Pressed, "#back")
    def go_back(self):
        if self.current_path != Path.home():
            self.current_path = self.current_path.parent
            self.refresh_files()

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.app.pop_screen()
    

    @on(Button.Pressed, "#forward")
    def handle_row_double_clicked(self):
        selected = self.table.cursor_row
        if selected is None or selected >= len(self.row_keys):
            return

        path = self.row_keys[selected]
        if path.is_dir():
            self.current_path = path
            self.refresh_files()

    @on(Button.Pressed, "#upload")
    def upload_selected(self):
        selected = self.table.cursor_row
        if selected is None or selected >= len(self.row_keys):
            return

        selected_path = self.row_keys[selected]
        upload_screen = UploadScreen(selected_path, self.config_name)
        self.app.push_screen(upload_screen)
        
        

    

    