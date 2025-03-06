from textual import events

class ConfigSelected(events.Event):
    def __init__(self, config_name: str):
        super().__init__()
        self.config_name = config_name
