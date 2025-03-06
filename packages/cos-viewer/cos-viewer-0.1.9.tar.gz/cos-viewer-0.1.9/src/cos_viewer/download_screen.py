from textual import on, work
from textual.app import Screen, ComposeResult
from textual.widgets import Header, Label, ProgressBar, Button
from textual.containers import Center, VerticalScroll
from src.cos_client import COSClient
from .message_screen import MessageScreen


class DownloadScreen(Screen):
    def __init__(self, filename, on_cancel, prefix, config_name, is_directory=False):
        super().__init__()
        self.filename = filename
        self.on_cancel = on_cancel
        self.prefix = prefix
        self.cos_client = COSClient(config_name)
        self.complate = False
        self.is_directory = is_directory

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            yield Label(f"等待下载：{self.filename}", id="download-label")
            yield ProgressBar(id="download-progress", total=100, show_eta=False)
        with Center():
            yield Button("取消", id="cancel-download")
            yield Button("开始下载", id="start")

    def update_progress(self, total, value):
        progress = (value / total) * 100
        self.query_one("#download-progress", ProgressBar).update(progress=progress)

    @on(Button.Pressed, "#cancel-download")
    def cancel(self):
        self.app.pop_screen()

    @work(thread=True)
    def start_download(self):
        """后台下载任务"""
        self.query_one("#download-label", Label).update(f"正在下载: {self.filename}")
        self.query_one("#start", Button).disabled = True
        try:
            if self.is_directory:
                self.cos_client.download_directory(
                    prefix=self.filename,
                    download_path=f"./downloads/{self.filename}",
                    progress_callback=self.update_progress
                )
            else:
                self.cos_client.download_object(
                    key=self.filename,
                    download_path="./downloads/",
                    progress_callback=self.update_progress
                )
            self.query_one("#download-label", Label).update(f"下载完成: {self.filename}")
            self.query_one("#start", Button).label = "完成"
            self.query_one("#cancel-download", Button).disabled = True
            self.complate = True

        except Exception as e:
            # raise
            # self.app.push_screen(MessageScreen(f"下载失败: {str(e)}"))
            self.app.call_from_thread(self.app.push_screen,
                                      MessageScreen(f"下载失败: {str(e)}"))

    @on(Button.Pressed, "#start")
    def start(self):
        if self.complate:
            self.app.pop_screen()
        else:
            self.start_download()
