from collections import defaultdict
import re


class MessageParser:
    def __init__(self, supported_headers: list):
        self.headers = supported_headers

    def get_supported_headers(self) -> list:
        """
        Get supported headers for this parser, i.e. TTAAii CCCC
        Shall init headers in __init__
        """
        return self.headers

    def parse(self, code: str) -> dict:
        """
        Read message code and parse it with message format
        
        Duplication rule:
        - To handle optional variable length fields, a field could show up more than once in format.
        - if a field is duplicated, then it will be recorded as 'field/n',
          where n is the number of times it is presented, counting from 0
        
          example: 'name' shows up 2 times, then first one is 'name', second one is 'name/1'

        Format explanation: check docstring in get_format()

        :return: field -> raw value
        """
        code = code.strip()
        result = {}
        index = 0
        format_list = self.get_format()
        field_counter = defaultdict(int)

        def parse_rule(rule_list, current_index, depth=0):
            nonlocal result
            i = 0
            while i < len(rule_list):
                # print(f"dealing layer {depth}, {i}/{len(rule_list)}...")
                rule = rule_list[i]
                if isinstance(rule, list):
                    strict_match_str = rf'^{rule[0]}'
                    if re.match(strict_match_str, code[current_index:]):
                        current_index = parse_rule(rule[1:], current_index, depth=depth + 1)
                        # print('match optional')
                    else:
                        # print('unmatched optional')
                        pass
                elif rule == 'ws':
                    while current_index < len(code) and code[current_index].isspace():
                        current_index += 1
                    # print('ws')
                elif rule == 'br':
                    if current_index < len(code) and code[current_index] == '\n':
                        current_index += 1
                    elif current_index == len(code):
                        # 全文最后，忽略换行
                        pass
                    else:
                        raise ValueError(f"未找到换行符:{rule_list}, {current_index}, {code}")
                    # print('br')
                else:
                    field, length_str = rule.split(':')
                    if length_str.startswith('-'):
                        target_word = length_str[1:]
                        start = current_index
                        while current_index < len(code):
                            if code[current_index:current_index + len(target_word)] == target_word:
                                break
                            current_index += 1
                        if current_index == start:
                            raise ValueError(f"字段 {field} 未匹配到内容直到 {target_word}")
                        value = code[start:current_index]
                    elif length_str == '$$':
                        assert i == len(rule_list) - 1
                        value = code[current_index:]
                        current_index += len(value)
                    elif length_str == 'S':
                        start = current_index
                        while current_index < len(code) and not code[current_index].isspace():
                            current_index += 1
                        if current_index == start:
                            raise ValueError(f"字段 {field} 未匹配到非空字符")
                        value = code[start:current_index]
                    elif length_str == '$':
                        start = current_index
                        while current_index < len(code) and code[current_index] != '\n':
                            current_index += 1
                        value = code[start:current_index]
                    else:
                        length = int(length_str)
                        if current_index + length > len(code):
                            raise ValueError(f"报文长度不足，无法解析字段 {field}")
                        value = code[current_index:current_index + length]
                        current_index += length
                    if field in result:
                        field_counter[field] += 1
                        field += f'/{field_counter[field]}'
                    result[field] = value
                i += 1
            return current_index

        index = parse_rule(format_list, index)

        if index < len(code):
            print(f"Format cannot cover all message. Remaining message:#{code[index:]}#")
        return result

    def explain(self, msg: dict) -> str:
        """
        Explain every field.
        :return: field -> explanation
        """
        raise NotImplementedError

    def get_translation(self) -> dict:
        """
        A translation dictionary to help translating message
        :return: field -> translation
        """
        raise NotImplementedError

    def translate(self, field: str, content: str='') -> str:
        """
        Translate field to it's meaning
        Translation could be:
        - 'field': 'meaning'
        - 'field': ('basic meaning', (('kw1', 'kw1 meaning'), ...))

        for the second case, the result would be:
        'basic meaning, kw1=kw1 meaning, kw2=kw2 meaning...'
        """
        field = field.split('/')[0]
        translation = self.get_translation().get(field, '')
        # case 1
        if type(translation) == str:
            return translation
        # case 2
        basic = translation[0]
        kws = translation[1]
        showed_kws = []
        for kw, kw_m in kws:
            if 'X' in kw:
                pattern = kw.replace('X', '[X0-9]')
                if re.search(pattern, content):
                    showed_kws.append((kw, kw_m))
            elif kw in content:
                showed_kws.append((kw, kw_m))
        return f"{basic}, " + ", ".join(f"{kw}={kw_m}" for kw, kw_m in showed_kws)

    def get_format(self) -> list:
        """
        A message format text to help parsing
        Format is a list of strings, allowing the following elements:
        - 'field:length': field name and it's length. 
            - When length is S, it means parsing until a whitespace.
            - When length is $, it means parsing until line break.
            - When length is $$, it means parsing until end of message.
            - When length is -WORD, it means parsing until WORD.
        - [' 30KTS', ...]: optional, only process when message prefix matches the first token of the list.
            - It is actually a regex matching, but wrapped as rf'^{tokens[0]}'.
        - 'ws': whitespace
        - 'br': line break
        """
        raise NotImplementedError

    def gen_header_expl(self, msg: dict, message_cat: str) -> str:
        """
        Generate header explanation
        :param msg: message dict
        :param message_cat: expl of TTAAii
        """
        CCCC_list = {
            "BABJ": "中央气象台",
            "PGTW": "联合台风警报中心",
            "RJTD": "日本气象厅",
            "KNES": "NOAA卫星服务部"
        }
        TTAAii = f"{msg['type']}{msg['area']}{msg['ii']}"
        CCCC = msg['msg_center']
        return f"{CCCC_list[CCCC]}({CCCC})于世界协调时{msg['msg_dd']}日{msg['msg_hh']}时{msg['msg_mm']}分发布{message_cat}({TTAAii})"
    
    def translate_common_terms(self, text: str) -> str:
        terms = {
            'SUBTROPICAL DEPRESSION': '副热带低压',
            'REMNANTS OF TROPICAL DEPRESSION': '热带低压残余',
            'TROPICAL DISTURBANCE': '热带扰动',
            'TROPICAL DEPRESSION': '热带低压',
            'TROPICAL STORM': '热带风暴',
            'TYPHOON': '台风',
            'EXTRATROPICAL CYCLONE': '温带气旋'
        }
        for term, translation in terms.items():
            text = text.replace(term, translation)
        return text
    
