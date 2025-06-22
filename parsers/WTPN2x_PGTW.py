import re

from .message_parser import MessageParser
from .deepseek_client import send_request


class WTPN2x_PGTW(MessageParser):
    def __init__(self):
        headers = [f"WTPN2{x} PGTW" for x in range(1, 7)]
        super().__init__(headers)

    def explain(self, msg: dict) -> str:
        # SUBJ/TROPICAL CYCLONE FORMATION ALERT (INVEST 95W)//
        if msg.get('subj'):
            target = re.search(r'\((.*?)\)', msg['subj']).group(1)
            target = target.replace('INVEST', '扰动')
            subj = f"针对{target} 的热带气旋形成警告" if 'CANCEL' not in msg['subj'] else f"取消{target} 的热带气旋形成警告"
        else:
            subj = ""
        expl = [
            f"联合台风警报中心于世界协调时{msg['msg_dd']}日{msg['msg_hh']}时{msg['msg_mm']}分发布热带气旋形成警告",
            '...',
            subj,
            send_request(msg['rmks'])
        ]
        return '\n'.join(expl)

    def get_translation(self) -> dict:
        return {
            'type': '报文格式，表示热带气旋形成警告',
            'area': '报文涉及的区域，PN=北太平洋',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，PGTW=联合台风警报中心',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'source': '综合行政报文，由联合台风警报中心签发',
            'subj': '报文主题，包含发布TCFA的对象',
            'ref': '参考报文，一般是扰动的首个报文',
            'ampn': '补充说明，在此具体指明参考报文的发报标题',
            'rmks': '报文内容，包含TCFA的具体内容',
            'addition': '附加信息，如果有，通常是过往定位与定强信息'
        }

    def get_format(self) -> list:
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', 'br',
            ['MSGID/', 'source:$', 'br'],
            ['SUBJ/', 'subj:$', 'br'],
            ['REF/', 'ref:$', 'br'],
            ['AMPN/', 'ampn:$', 'br'],
            'rmks:-//',
            'addition:$$'
        ]
        return msg_format
