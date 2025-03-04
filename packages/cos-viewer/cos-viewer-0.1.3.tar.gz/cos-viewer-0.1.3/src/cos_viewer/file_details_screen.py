from textual import on
from textual.app import Screen, ComposeResult
from textual.containers import Container
from textual.widgets import Header, DataTable, Button


class FileDetailsScreen(Screen):
    def __init__(self, file_info, config_name):
        super().__init__()
        self.file_info = file_info
        self.config_name = config_name

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="file-details-container"):
            self.table = DataTable(id="file-details-table", zebra_stripes=True)
            self.table.add_columns("属性", "值")
            self.table.add_row("对象名称", self.file_info['Key'])
            if self.file_info.get('Metadata'):
                for k, v in self.file_info.get('Metadata', {}).items():
                    self.table.add_row(k, v)
            self.table.add_row("对象地址", self.file_info.get('Location', 'N/A'))
            yield self.table

            # 子表格：对象标签
            if self.file_info.get('Tags'):
                tag_table = DataTable(id="tag-table", )
                tag_table.add_columns("标签", "值")
                for k, v in self.file_info.get('Tags', {}).items():
                    tag_table.add_row(k, v)
                yield tag_table
            with Container(id="file-details-buttons"):
                yield Button("返回", id="back")

    @on(Button.Pressed, "#back")
    def go_back(self):
        self.app.pop_screen()
