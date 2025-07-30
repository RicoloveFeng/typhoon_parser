from .message_parser import MessageParser
import json
import re
import os

class WHCI_BABJ(MessageParser):
    def __init__(self):
        super().__init__(['WHCI40 BABJ'])
    
    def explain(self, msg: dict) -> str:
        cat_expl = {
            'TD': '热带低压',
            'TS': '热带风暴',
            'STS': '强热带风暴',
            'TY': '台风',
            'STY': '强台风',
            'SuperTY': '超强台风',
        }
        landing_spd = msg['spd'][1:-1]
        return '\n'.join([
            self.gen_header_expl(msg, "台风登陆报文"),
            f"{cat_expl[msg['cat']]}{msg['name']}（编号{msg['dom_num']}，国际编号{msg['inter_num']}）已登陆{msg['place']}",
            f"登陆时间为世界协调时{msg['land_dd']}日{msg['land_hh']}时{msg['land_mm']}分，登陆风速{landing_spd}",
        ])
    
    def get_translation(self) -> dict:
        return {
            'type': '报文格式，类型为风暴潮警告，本报文专指台风登陆报文',
            'area': '报文涉及的区域，CI=中国',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，BABJ=中央气象台',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'cat': '热带气旋等级',
            'name': '热带气旋名称',
            'dom_num': '热带气旋国内编号',
            'inter_num': '热带气旋国际编号',
            'place': '登陆地点',
            'land_dd': '登陆日期',
            'land_hh': '登陆小时',
            'land_mm': '登陆分钟',
            'gmt': '时区，即世界协调时',
            'spd': '风速',
        }
    
    def get_format(self) -> list:
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', 'br',
            'cat:S', 'ws', 'dom_num:S', 'ws', 'inter_num:S', 'ws', 'name:S', 'ws', 'landed_on:9', 'ws', 'place:$', 'br',
            'land_dd:2', 'land_hh:2', 'land_mm:2', 'gmt:3', 'ws', 'spd:S', 'br',
        ]
        return msg_format
        