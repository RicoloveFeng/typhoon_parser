from .message_parser import MessageParser
from .deepseek_client import send_request
class WDPN3x_PGTW(MessageParser):
    def __init__(self):
        headers = [f"WDPN3{x} PGTW" for x in range(6)]
        super().__init__(headers)

    def explain(self, msg: dict) -> str:
        # title: SUBJ/PROGNOSTIC REASONING FOR TROPICAL DEPRESSION 02W (SEPAT) WARNING NR 011//

        title = msg['title']
        # 提取FOR后面的对象
        start_idx = title.find('FOR ') + 4
        end_idx = max(title.find(' WARNING'), title.find('\nWARNING'))
        target = title[start_idx:end_idx].strip()

        # 提取最后的编号
        nr_idx = max(title.find('NR '), title.find('NR\n')) + 3
        nr_end = title.find('//', nr_idx)
        warning_nr = title[nr_idx:nr_end].strip()


        expl = [
            self.gen_header_expl(msg, "预测推理公告"),
            '...',
            f'针对{self.translate_common_terms(target)}的预测推理公告 编号{warning_nr}',
            '备注/',
            '1. 供气象研究者阅读。',
            '2. 6小时综述与预报。',
            send_request(msg['summary'][1:] + msg['analysis'] + msg['iwrb'] + msg['steering'] + msg['dvorak'] + msg['env'] + msg['confidence']) + 
            "\n\n" + 
            send_request(msg['reasoning'])
        ]
        return '\n'.join(expl)
    
    def get_translation(self) -> dict:
        return {
            'type': '报文格式，表示预测推理公告',
            'area': '报文涉及的区域，PN=北太平洋',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，PGTW=联合台风警报中心',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'source': '综合行政报文，由联合台风警报中心签发',
            'summary': '摘要，包含经纬度、风速、参考位置、6小时位置变化、有效波高',
            'analysis': '卫星分析、初始位置及强度讨论',
            'iwrb': '初始风圈半径基础',
            'steering': '当前引导机制',
            'dvorak': '机构德沃夏克及自动定位结果',
            'env': '预报员当前环境评估',
            'confidence': '分析置信度',
            'reasoning': '预报依据'

        }
    
    def get_format(self) -> list:
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', 'br',
            'source:-SUBJ',
            'title:-\nSUMMARY',
            'summary:-SATELLITE ANALYSIS, INITIAL POSITION AND',
            'analysis:-INITIAL WIND RADII BASIS',
            'iwrb:-CURRENT STEERING MECHANISM',
            'steering:-AGENCY DVORAK AND AUTOMATED FIXES',
            'dvorak:-FORECASTER ASSESSMENT OF CURRENT ENVIRONMENT',
            'env:-ANALYSIS CONFIDENCE',
            'confidence:-3. FORECAST REASONING',
            'reasoning:$$',
        ]
        return msg_format
        