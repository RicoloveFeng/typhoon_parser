from .message_parser import MessageParser
from .deepseek_client import send_request
class TXPQ2x_KNES(MessageParser):
    def __init__(self):
        headers = [f"TXPQ2{x} KNES" for x in range(10)]
        super().__init__(headers)

    def explain(self, msg: dict) -> str:
        A = msg['A'][4:].strip()
        B = msg['B'][3:].strip()
        obs_day, obs_hour = B.split('/')
        obs_hour, obs_min = obs_hour[:2], obs_hour[2:4]
        F = msg['F'][4:].strip()
        F_res = []
        trend = {'S': '维持', 'D': '增强', 'W': '减弱'}
        F_split = F.split(' ')
        curr = F_split[0]
        curr_res = curr.split('/')
        if len(curr_res) >= 2:
            # TX.X/Y.Y -> FT X.X CI Y.Y
            F_res.append(f"FT {curr_res[0][1:]}")
            F_res.append(f"CI {curr_res[1]}")
        elif len(curr_res) == 1 and curr_res[0] == "OVERLAND":
            F_res.append("环流中心位于陆地，德法不适用")
        elif F == "TOO WEAK":
            F_res.append("系统过弱，德法不适用")
        elif F == "EXTRATROPICAL":
            F_res.append("已变性为温带气旋")
        else:
            F_res.append("解析失败")
        # H.[][]REMARKS: ...
        # 把前面的H.[][]删除
        expl = [
            self.gen_header_expl(msg, "台风发展报文"),
            f"A.  分析对象：{self.translate_common_terms(A)}",
            f"B. 观测时间：{obs_day}日{obs_hour}时{obs_min}分（世界协调时）",
            "...",
            f"F.  德法结论：{', '.join(F_res)}",
            "...",
            "H.  " + send_request(msg['H'][4:]),
            "..."
        ]
        return '\n'.join(expl)
    
    def get_translation(self) -> dict:
        return {
            'type': '报文格式，表示基于卫星的德法分析',
            'area': '报文涉及的区域，PQ=北太平洋',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，KNES=NOAA卫星服务部（SSD）',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'tcswnp': '西北太平洋热带气旋分析',
            'A': '台风等级、名称与编号',
            'B': '观测时间',
            'C': '中心纬度',
            'D': '中心经度',
            'E': '定位精度及使用的卫星，ONE到SIX精度逐渐降低',
            'F': ('德法分析结果', (
                ('TOO WEAK', '强度过弱不分析'),
                ('TX.X', 'FT'),
                ('X.X', 'CI'),
                ('DX.X', '增强指数'),
                ('SX.X', '强度维持'),
                ('WX.X', '减弱指数'),
                ('HRS', '计算强度的时间间隔'),
                ('STT', '短期趋势'),
                ('XT', '温带气旋'),
                ('ST', '副热带气旋'))),
            'G': ('使用的卫星图像', (
                ('IR', '红外'),
                ('EIR', '增强红外'),
                ('VIS', '可见光'),
                ('MSI', '多光谱'),
                ('SSMIS', '微波成像'),
                ('SWIR', '短波红外'),
                ('ATMS', '先进技术微波探测仪'),
                ('PRXY', 'ProxyVis'))),
            'H': '分析理由',
            'I': '额外定位信息',
            'issuer': '预报员'
        }
    
    def get_format(self) -> list:
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', 'br',
            'tcswnp:-A.',
            'A:-B.',
            'B:-C.',
            'C:-D.',
            'D:-E.',
            'E:-F.',
            'F:-G.',
            'G:-H.',
            'H:-I.',
            'I:-...',
            'issuer:$$'
        ]
        return msg_format
        
