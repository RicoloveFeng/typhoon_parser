from .message_parser import MessageParser
from .deepseek_client import send_request


class ABPW10_PGTW(MessageParser):
    def __init__(self):
        headers = ["ABPW10 PGTW"]
        super().__init__(headers)

    def explain(self, msg: dict) -> str:
        wnpac_text = [
            (msg['wnpac_cyclone'], 'A. 热带气旋摘要'),
            (msg['wnpac_invest'], 'B. 热带扰动摘要'),
            (msg['wnpac_subtropical'], 'C. 副热带气旋摘要'),
        ]
        translated_text = []
        for text, name in wnpac_text:
            if ': NONE.' in text:
                translated_text.append(f'   {name}: 无。')
            else:
                translated_text.append(f'   {send_request(text)}')

        expl = [
            self.gen_header_expl(msg, "西太平洋重要热带天气公报"),
            '...',
            '1. 西太平洋区域（180度经线至马来半岛）：',
            '\n'.join(translated_text),
            '...',
        ]
        return '\n'.join(expl)

    def get_translation(self) -> dict:
        return {
            'type': '报文格式，A=分析，B无约定含义，AB可理解为热带系统分析',
            'area': '报文涉及的区域，PW=西太平洋',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，PGTW=联合台风警报中心',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'source': '综合行政报文，由联合台风警报中心签发',
            'subj': '报文主题，即西太平洋与南太平洋的重要天气公报',
            'ref': '参考报文，用于指明下文中的某个报文',
            'ampn': '补充说明，在此具体指明参考报文的发报标题',
            'wnpac': '西太平洋的摘要，包含180度经线到马来半岛的太平洋区域',
            'wnpac_cyclone': '西太平洋的热带气旋摘要',
            'wnpac_invest': '西太平洋的热带扰动摘要',
            'wnpac_subtropical': '西太平洋的副热带气旋摘要',
            'spac': '南太平洋的摘要，包含南美洲西海岸到东经135度的区域',
            'spac_cyclone': '南太平洋的热带气旋摘要',
            'spac_invest': '南太平洋的热带风暴摘要',
            'spac_subtropical': '南太平洋的副热带气旋摘要',
        }

    def get_format(self) -> list:
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', 'br',
            'source:-SUBJ/',
            'subject:-//', 'ending:2', 'br',
            ['REF/', 'ref:$', 'br'],
            ['AMPN/', 'ampn:$', 'br'],
            'rmks:-1. WESTERN NORTH PACIFIC',
            'wnpac:-   A. TRO',
            'wnpac_cyclone:-   B. TRO',
            'wnpac_invest:-   C. SUBTRO',
            'wnpac_subtropical:-2. SOUTH PACIFIC',
            'spac:-   A. TRO',
            'spac_cyclone:-   B. TRO',
            'spac_invest:-   C. SUBTRO',
            'spac_subtropical:-//',
            'ending:$$'
        ]
        return msg_format

