from .message_parser import MessageParser
from .deepseek_client import send_request
class WTPQ3x_RJTD(MessageParser):
    def __init__(self):
        headers = [f"WTPQ3{x} RJTD" for x in range(5)]
        super().__init__(headers)

    def explain(self, msg: dict) -> str:
        # H.[]REMARKS: ...
        # 把前面的H.[]删除
        before_translate = msg["general_comment"] + msg["synoptic_situation"] + msg["track_forecast"] + msg["intensity_forecast"] + msg["remarks"]
        after_translate = send_request(before_translate)
        expl = [
            self.gen_header_expl(msg, "热带气旋预测推理公告"),
            after_translate
        ]
        return '\n'.join(expl)
    
    def get_translation(self) -> dict:
        return {
            'type': '报文格式，表示台风警告报文',
            'area': '报文涉及的区域，PQ=西北太平洋',
            'ii': '报文类型编号，在当前报文类型对应JMA的TD临时顺序',
            'msg_center': '报文发布单位，RJTD=日本气象厅',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'title': '区域专业气象中心热带气旋预测推理',
            'subtitle': '报文序号、编报对象与目标经纬度',
            'general_comment': '总体说明',
            'synoptic_situation': '天气形势',
            'track_forecast': '路径预报',
            'intensity_forecast': '强度预报',
            'remarks': '备注',
        }
    
    def get_format(self) -> list:
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', [' CC', 'ws', 'ccx:3'], 'br',
            'title:$', 'br',
            'subtitle:$', 'br',
            'general_comment:-2.SYNOPTIC SITUATION',
            'synoptic_situation:-3.TRACK FORECAST',
            'track_forecast:-4.INTENSITY FORECAST',
            'intensity_forecast:-5.',
            'remarks:$$',
        ]
        return msg_format
        
