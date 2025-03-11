class MessageParser:
    def __init__(self, msg_type: str):
        self.msg_type = msg_type
        self.area_table = {
            'PQ': '西北太平洋'
        }
        self.msg_center_table = {
            'BABJ': '中央气象台'
        }
        
    def parse(self, code: str) -> dict:
        """
        Read message code and parse it with message format
        :return: field -> raw value
        """
        code = code.strip()
        result = {}
        index = 0
        format_list = self.get_format()
        for rule in format_list:
            if rule == 'ws':
                while index < len(code) and code[index].isspace():
                    index += 1
            elif rule == 'br':
                if index < len(code) and code[index] == '\n':
                    index += 1
            else:
                field, length_str = rule.split(':')
                if length_str == 'S':
                    start = index
                    while index < len(code) and not code[index].isspace():
                        index += 1
                    value = code[start:index]
                else:
                    length = int(length_str)
                    if index + length > len(code):
                        raise ValueError(f"Message is too short to resolve {field}")
                    value = code[index:index + length]
                    index += length
                result[field] = value
                # debug
                # print(f"{field}: {value}")
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