import argparse
from collections import defaultdict
import json
import logging 

from parsers.TCPQ_BABJ import TCPQ_BABJ
from parsers.WTPQ_BABJ import WTPQ_BABJ
from parsers.WSCI_BABJ import WSCI_BABJ
from parsers.WHCI_BABJ import WHCI_BABJ
from parsers.TPPN1x_PGTW import TPPN1x_PGTW
from parsers.WDPN3x_PGTW import WDPN3x_PGTW
from parsers.WTPQ3x_RJTD import WTPQ3x_RJTD
from parsers.TXPQ2x_KNES import TXPQ2x_KNES
from parsers.WTPN2x_PGTW import WTPN2x_PGTW
from parsers.ABPW10_PGTW import ABPW10_PGTW
from parsers.message_parser import MessageParser
from parsers.default_parser import DefaultParser

class MessageParserManager:
    def __init__(self):
        self.parser_map = {}
        self.add_parser(TCPQ_BABJ())
        self.add_parser(WTPQ_BABJ())
        self.add_parser(WSCI_BABJ())
        self.add_parser(WHCI_BABJ())
        self.add_parser(TPPN1x_PGTW())
        self.add_parser(WDPN3x_PGTW())
        self.add_parser(WTPQ3x_RJTD())
        self.add_parser(TXPQ2x_KNES())
        self.add_parser(WTPN2x_PGTW())
        self.add_parser(ABPW10_PGTW())

    def add_parser(self, parser: MessageParser):
        for header in parser.get_supported_headers():
            self.parser_map[header] = parser
        
    def get_parser_from_code(self, code: str) -> MessageParser:
        msg_type = code[:11]
        parser = self.parser_map.get(msg_type, DefaultParser())
        return parser

    def get_parser_from_msg(self, msg: dict) -> MessageParser:
        if "msg_text" in msg:  # Only field of default
            return DefaultParser()
        header = f"{msg['type']}{msg['area']}{msg['ii']} {msg['msg_center']}"
        return self.get_parser_from_code(header)

    def parse(self, code: str) -> dict:
        try:
            res = self.get_parser_from_code(code).parse(code)
        except Exception as e:
            logging.error(f"Cannot parse: {code}")
            logging.error(e)
            res = DefaultParser().parse(code)
        return res
    
    def parse_from_raw(self, raw_msg: list) -> dict:
        """
        :param raw_msg: a tuple of (time_str, raw_code, source)
        :return: dict
        - time_str, source
        - has_zczc, has_nnnn: bool, whether the message contains ZCZC or NNNN
        - striped_msg: str, the stripped message with no extra characters
        - parsed_msg: dict, the parsed message by parser
        """
        time_str, raw_code, source = raw_msg
        # NMC contains ZCZC and NNNN
        msg_meta = {}
        real_content = ''
        if source == "NMC":
            real_content = raw_code.replace('ZCZC', '').replace('NNNN', '').strip()
            msg_meta['has_zczc'] = True
            msg_meta['has_nnnn'] = True
        elif source == "NOAA":
            real_content = raw_code.strip()
            if 'NNNN' in raw_code:
                real_content = raw_code.replace('NNNN', '').strip()
                msg_meta['has_nnnn'] = True
        
        if real_content[-1] == '=':
            real_content = real_content[:-1]
            msg_meta['has_eq'] = True
        msg_meta['striped_msg'] = real_content
        msg_meta['parsed_msg'] = self.parse(real_content)
        msg_meta['time_str'] = time_str
        msg_meta['source'] = source
            
        return msg_meta
    
    def explain(self, msg: dict) -> str:
        return self.get_parser_from_msg(msg).explain(msg)
    
    def translate(self, msg: dict, field: str, content: str) -> str:
        return self.get_parser_from_msg(msg).translate(field, content)
    
    def get_format(self, msg: dict) -> list:
        return self.get_parser_from_msg(msg).get_format()
    
    def reconstruct_message(self, msg: dict) -> list:
        expl = self.explain(msg)
        fmt = self.get_format(msg)
        
        field_counter = defaultdict(int)
        raw_msg = []

        def process_rule(rule_list, raw_msg):
            for rule in rule_list:
                if isinstance(rule, list):
                    # 处理可选规则
                    process_rule(rule[1:], raw_msg)
                elif rule == 'ws':
                    # 添加空格
                    raw_msg.append((" ",))
                elif rule == 'br':
                    # 添加换行符
                    raw_msg.append(("<br>",))
                else:
                    field, length_str = rule.split(':')
                    # 处理重复字段
                    if field_counter[field] > 0:
                        actual_field = f"{field}/{field_counter[field]}"
                    else:
                        actual_field = field
                    if actual_field in msg:
                        # 将头尾的\n替换为<br>

                        # 处理头部换行符
                        leading_n = len(msg[actual_field]) - len(msg[actual_field].lstrip('\n'))
                        for _ in range(leading_n):
                            raw_msg.append(("<br>",))

                        # 处理中间内容(去除头尾换行符)
                        field_value = msg[actual_field].strip('\n').replace('\n', '<br>')
                        translation = self.translate(msg, actual_field, field_value)
                        if translation:
                            raw_msg.append((field_value, translation))
                        else:
                            raw_msg.append((field_value,))

                        # 处理尾部换行符
                        trailing_n = len(msg[actual_field]) - len(msg[actual_field].rstrip('\n'))
                        for _ in range(trailing_n):
                            raw_msg.append(("<br>",))
                        field_counter[field] += 1
                    else:
                        return

        process_rule(fmt, raw_msg)
        return raw_msg
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', help='code file to be parsed')
    parser.add_argument('--output', choices=['json', 'txt', 'print'], help='output format', default='json')
    args = parser.parse_args()
    
    # adding parsers
    manager = MessageParserManager()
    
    # parsing codes
    with open(args.code, 'r') as f:
        code = f.read()
    msg = manager.parse(code)
    
    # output type is determined by args.output
    file_prefix = '.'.join(args.code.split('.')[:-1])
    if args.output == 'json':
        with open(f'{file_prefix}.json', 'w') as f:
            json.dump(msg, f, indent=4)
    elif args.output == 'txt':
        with open(f'{file_prefix}.txt', 'w') as f:
            f.write(manager.explain(msg))
    else:
        print(manager.explain(msg))
