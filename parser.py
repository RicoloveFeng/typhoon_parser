import argparse
import json 

from parsers.TCPQ_BABJ import TCPQ_BABJ
from parsers.message_parser import MessageParser

class MessageParserManager:
    def __init__(self, code):
        self.code = code 
        self.parser_map = {}

    def add_parser(self, parser: MessageParser):
        self.parser_map[parser.get_type()] = parser

    def parse(self, code: str) -> dict:
        msg_type = f"{code[:4]}_{code[7:11]}"
        parser = self.parser_map.get(msg_type, None)
        if not parser:
            raise ValueError(f'Message type {msg_type} not supported')
        return parser.parse(code)
    
    def explain(self, msg: dict) -> str:
        msg_type = f"{msg['type']}{msg['area']}_{msg['msg_center']}"
        parser = self.parser_map.get(msg_type, None)
        if not parser:
            raise ValueError(f'Message type {msg_type} not supported')
        return parser.explain(msg)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--code', help='code file to be parsed')
    parser.add_argument('--output', choices=['json', 'txt', 'print'], help='output format', default='json')
    args = parser.parse_args()
    
    # adding parsers
    manager = MessageParserManager(args.code)
    manager.add_parser(TCPQ_BABJ())
    
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