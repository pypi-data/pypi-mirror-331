from textual import on
from textual.app import Screen, ComposeResult
from textual.containers import Container, Center
from textual.widgets import Header, Button
from .file_browser_screen import FileBrowserScreen
from .local_file_browser_screen import LocalFileBrowserScreen

class FeatureSelectScreen(Screen):
    def __init__(self, config_name: str):
        super().__init__()
        self.config_name = config_name

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="feature-select-container"):
            with Center():
                yield Button("浏览线上文件", id="online", tooltip="选择线上文件进行下载或查看")
                yield Button("浏览本地文件", id="local", tooltip="选择本地文件或目录进行上传")
                yield Button("返回", id="back")

    @on(Button.Pressed, "#online")
    def browse_online(self):
        self.app.push_screen(FileBrowserScreen(self.config_name))

    @on(Button.Pressed, "#local")
    def browse_local(self):
        self.app.push_screen(LocalFileBrowserScreen(self.config_name))

    @on(Button.Pressed, "#back")
    def go_back(self):
        self.app.pop_screen()