class MessageParser:
    def __init__(self, msg_type: str):
        self.msg_type = msg_type
        
    def parse(self, code: str) -> dict:
        """
        Read message code and parse it with message format
        :return: field -> raw value
        """
        code = code.strip()
        result = {}
        index = 0
        format_list = self.get_format()

        def parse_rule(rule_list, current_index, depth = 0):
            local_result = {}
            i = 0
            while i < len(rule_list):
                # print(f"dealing layer {depth}, {i}/{len(rule_list)}...")
                rule = rule_list[i]
                if isinstance(rule, list):
                    strict_match_str = rule[0]
                    if current_index + len(strict_match_str) <= len(code) and code[current_index:current_index + len(strict_match_str)] == strict_match_str:
                        sub_result, current_index = parse_rule(rule[1:], current_index, depth=depth + 1)
                        local_result.update(sub_result)
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
                        raise ValueError("未找到换行符")
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
                    local_result[field] = value
                    print(f"{field}: {value}")
                i += 1
            return local_result, current_index

        result, index = parse_rule(format_list, index)

        if index < len(code):
            print(f"Format cannot cover all message. Remaining message:#{code[index:]}#")
        return result
    
    def explain(self, msg: dict) -> dict:
        """
        Explain every field.
        :return: field -> explanation
        """
        raise NotImplementedError
    
    def translate(self, msg: dict) -> str:
        """
        Translate message to human readable string
        :return: a translated paragraph
        """
        raise NotImplementedError
    
    def get_format(self) -> list:
        """
        A message format text to help parsing
        Format is a list of strings, allowing the following elements:
        - 'field:length': field name and it's length. 
            - When length is S, it means parsing until a whitespace.
            - When length is $, it means parsing until line break.
        - [' 30KTS', ...]: optional, only process when prefix matches the first token of the list.
        - 'ws': whitespace
        - 'br': line break
        """
        raise NotImplementedError
    
    def get_type(self):
        return self.msg_type