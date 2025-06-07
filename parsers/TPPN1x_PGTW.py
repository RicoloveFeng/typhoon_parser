from .message_parser import MessageParser
from .deepseek_client import send_request
class TPPN1x_PGTW(MessageParser):
    def __init__(self):
        headers = [f"TPPN1{x} PGTW" for x in range(10)]
        super().__init__(headers)

    def explain(self, msg: dict) -> str:
        # H.[]REMARKS: ...
        # 把前面的H.[]删除
        expl = [
            f"联合台风警报中心于世界协调时{msg['msg_dd']}日{msg['msg_hh']}时{msg['msg_mm']}分发布台风发展报文",
            "...",
            "H. " + send_request(msg['H'][3:]),
            "..."
        ]
        return '\n'.join(expl)
    
    def get_translation(self) -> dict:
        return {
            'type': '报文格式，表示基于卫星的德法分析',
            'area': '报文涉及的区域，PN=北太平洋',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，PGTW=联合台风警报中心',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'A': '台风等级、名称与编号',
            'B': '观测时间',
            'C': '中心纬度',
            'D': '中心经度',
            'E': '定位精度及使用的卫星，ONE到SIX精度逐渐降低',
            'F': ('德法分析结果', (
                ('TX.X', 'FT'),
                ('X.X', 'CI'),
                ('DX.X', '增强指数'),
                ('SX.X', '强度维持'),
                ('WX.X', '减弱指数'),
                ('HRS', '计算强度的时间间隔'),
                ('STT', '短期趋势'),
                ('XT', '后热带气旋'))),
            'G': ('使用的卫星图像', (
                ('IR', '红外'),
                ('EIR', '增强红外'),
                ('VIS', '可见光'),
                ('MSI', '多光谱'))),
            'H': '分析理由',
            'I': '额外定位信息',
            'issuer': '预报员'
        }
    
    def get_format(self) -> list:
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', 'br',
            'A:-B.',
            'B:-C.',
            'C:-D.',
            'D:-E.',
            'E:-F.',
            'F:-G.',
            'G:-H.',
            'H:-I.',
            'I:-\n\n\n',
            'issuer:$$'
        ]
        return msg_format
        