from textual import on, work
from textual.app import Screen, ComposeResult
from textual.widgets import Header, Label, ProgressBar, Button
from textual.containers import Center
from src.cos_client import COSClient
from src.config_manager import ConfigManager
from .message_screen import MessageScreen
from pathlib import Path


class UploadScreen(Screen):
    def __init__(self, file_path, config_name):
        super().__init__()
        self.file_path = file_path
        self.config_name = config_name
        self.cos_client = COSClient(config_name)
        self.complete = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            yield Label(f"正在上传：{self.file_path.name}", id="upload-label")
            yield ProgressBar(id="upload-progress", total=100, show_eta=False)
        with Center():
            yield Button("取消", id="cancel-upload")
            yield Button("开始上传", id="start")

    def update_progress(self, total, value):
        progress = (value / total) * 100
        self.query_one("#upload-progress", ProgressBar).update(progress=progress)

    @on(Button.Pressed, "#cancel-upload")
    def cancel(self):
        self.app.pop_screen()

    @work(thread=True)
    def start_upload(self):
        self.query_one("#start", Button).disabled = True
        try:
            self.cos_client.upload_file(
                str(self.file_path),
                self.file_path.name,
                progress_callback=self.update_progress
            )
            self.query_one("#upload-label", Label).update(f"上传完成: {self.file_path.name}")
            self.query_one("#start", Button).label = "完成"
            self.query_one("#start", Button).disabled = False
            self.query_one("#cancel-upload", Button).disabled = True
            self.complete = True

        except Exception as e:
            self.app.call_from_thread(self.app.push_screen,
                                    MessageScreen(f"上传失败: {str(e)}"))

    @on(Button.Pressed, "#start")
    async def start(self):
        if self.complete:
            self.app.pop_screen()
        else:
            if self.file_path.is_dir():
                self.upload_directory(self.file_path)
            else:
                self.start_upload()

    @work(thread=True)
    def upload_directory(self, dir_path: Path):
        try:
            self.query_one("#start", Button).disabled = True
            config = ConfigManager().get_config(self.config_name)
            cos_client = COSClient(self.config_name)
            
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(dir_path))
                    cos_key = f"{config['prefix']}/{relative_path}".lstrip('/')
                    cos_client.upload_file(
                        str(file_path),
                        cos_key,
                        progress_callback=self.update_progress
                    )
                    self.query_one("#upload-label", Label).update(f"正在上传：{file_path.name}")
            
            self.query_one("#upload-label", Label).update("目录上传完成")
            self.query_one("#start", Button).label = "完成"
            self.query_one("#start", Button).disabled = False
            self.query_one("#cancel-upload", Button).disabled = True
            self.complete = True
        except Exception as e:
            self.app.call_from_thread(self.app.push_screen,
                                    MessageScreen(f"目录上传失败: {str(e)}"))