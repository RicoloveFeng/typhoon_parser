import argparse
from collections import defaultdict
import json 

from parsers.TCPQ_BABJ import TCPQ_BABJ
from parsers.WTPQ_BABJ import WTPQ_BABJ
from parsers.WSCI_BABJ import WSCI_BABJ
from parsers.message_parser import MessageParser

class MessageParserManager:
    def __init__(self):
        self.parser_map = {}
        self.add_parser(TCPQ_BABJ())
        self.add_parser(WTPQ_BABJ())
        self.add_parser(WSCI_BABJ())

    def add_parser(self, parser: MessageParser):
        self.parser_map[parser.get_type()] = parser
        
    def get_parser_from_msg(self, msg: dict) -> MessageParser:
        msg_type = f"{msg['type']}{msg['area']}_{msg['msg_center']}"
        parser = self.parser_map.get(msg_type, None)
        if not parser:
            raise ValueError(f'Message type {msg_type} not supported')
        return parser

    def parse(self, code: str) -> dict:
        msg_type = f"{code[:4]}_{code[7:11]}"
        parser = self.parser_map.get(msg_type, None)
        if not parser:
            raise ValueError(f'Message type {msg_type} not supported')
        return parser.parse(code)
    
    def explain(self, msg: dict) -> str:
        return self.get_parser_from_msg(msg).explain(msg)
    
    def translate(self, msg: dict, field: str) -> str:
        return self.get_parser_from_msg(msg).translate(field)
    
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
                        field_value = msg[actual_field]
                        translation = self.translate(msg, actual_field)
                        if translation:
                            raw_msg.append((field_value, translation))
                        else:
                            raw_msg.append((field_value,))
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
