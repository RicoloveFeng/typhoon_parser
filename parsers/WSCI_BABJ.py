from .message_parser import MessageParser
import json
import re
import os


def parse_telecode(code: str) -> str:
    """
    4-digit chinese telecode parser
    """
    with open(f'{os.path.dirname(os.path.abspath(__file__))}/../telecode/code.json', 'r') as f:
        telecode_table = json.load(f)
        
    def decode_one(four_digit: str) -> str:
        if not four_digit:
            return ''
        if four_digit[0:2] in ['97', '98', '99']:
            decode_subset = {
                '75': '。',
                '76': '，',
                '87': 'N',
                '78': 'E',
                '99': 'Z',
            }
            if four_digit[2:] in decode_subset:
                return decode_subset[four_digit[2:]]
            return four_digit[2:]
        
        return telecode_table.get(four_digit, f'[{four_digit}]')
            
    result = []
    for token in re.split(' |\n', code):
        if len(token) == 4:          
            result.append(decode_one(token))
        elif len(token) > 4:
            left, mid_right = token.split('(')
            mid, right = mid_right.split(')')
            result.append(decode_one(left) + mid + decode_one(right))
        else:
            # may get a null str
            pass
    return ''.join(result)

class WSCI_BABJ(MessageParser):
    def __init__(self):
        super().__init__(['WSCI40 BABJ'])
    
    def explain(self, msg: dict) -> str:
        begin_date_str = ""
        if 'telecode2' in msg:
            MM, dd, hh = [int(digits[2:]) for digits in msg['telecode2'].strip().split(' ')]
            begin_date_str = f"，{MM}月{dd}日{hh:2}时"
        return '\n'.join([
            self.gen_header_expl(msg, "台风编号报文"),
            f"发往沈阳/武汉/上海/成都/广州/太原/西安/天津/深圳/济南/郑州/北京",
            parse_telecode(msg['telecode']),
            "发自中央气象台" +  
            begin_date_str
        ])
    
    def get_translation(self) -> dict:
        return {
            'type': '报文格式，表示基于台风起编/停编报文',
            'area': '报文涉及的区域，CI=中国',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，BABJ=中央气象台',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'to': '发往',
            'bcsy': '沈阳台',
            'bchk': '武汉台',
            'bcsh': '上海台',
            'bccd': '成都台',
            'bcgz': '广州台',
            'bety': '太原台',
            'bexa': '西安台',
            'betj': '天津台',
            'besz': '深圳台',
            'bejn': '济南台',
            'bezz': '郑州台',
            'bebj': '北京台',
            'telecode': '中文电码',
            'babj-3049': '中央气象台发 （3049=气）',
            'telecode2': '中文电码，表示发报时间'
        }
    
    def get_format(self) -> list:
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', 'br',
            'to:2', 'ws', 'bcsy:4', 'ws', 'bchk:4', 'ws', 'bcsh:4', 'ws', 'bccd:4', 'ws', 'bcgz:4', 'br',
            'bety:4', 'ws', 'bexa:4', 'ws', 'betj:4', 'ws', 'besz:4', 'ws', 'bejn:4', 'ws', 'bezz:4', 'ws', 'bebj:4', 'br',
            'telecode:-BABJ', 
            'babj-3049:9', 'ws', ['97', 'telecode2:$']
        ]
        return msg_format
        