from .message_parser import MessageParser

class DefaultParser(MessageParser):
    def __init__(self):
        super().__init__([])

    def explain(self, msg: dict) -> str:
        return ""

    def get_translation(self) -> dict:
        return {}

    def get_format(self) -> list:
        return ['type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', 'br',
                'msg_text:$$']
