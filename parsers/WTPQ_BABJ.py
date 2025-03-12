from .message_parser import MessageParser

class WTPQ_BABJ(MessageParser):
    def __init__(self):
        super().__init__('WTPQ_BABJ')
    
    def explain(self, msg: dict) -> str:
        return ""
    
    def translate(self, msg: dict) -> str:
        return {
            'type': '报文格式，表示基于台风卫星云图的发展趋势分析',
            'area': '报文涉及的区域，PQ=西北太平洋',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，BABJ=中央气象台',
            'ccx': '第几次修订，如A=第一次修订',
            'cat': '热带气旋等级',
            'name': '热带气旋名称',
            'dom_num': '热带气旋国内编号',
            'inter_num': '热带气旋国际编号',
            'init_dd': '起报时间-日期',
            'init_hh': '起报时间-小时',
            'init_mm': '起报时间-分钟',
            '00hr': '当前时间',
            'ty_la': '中心经度',
            'ty_lo': '中心纬度',
            'pressure': '中心气压',
            'wind_spd': '中心附近最大风速',
            '30kts_winds': '七级风圈',
            '30kts_NE_rad': '七级风圈东北半径',
            '30kts_SE_rad': '七级风圈东南半径',
            '30kts_SW_rad': '七级风圈西南半径',
            '30kts_NW_rad': '七级风圈西北半径',
            '50kts_winds': '十级风圈',
            '50kts_NE_rad': '十级风圈东北半径',
            '50kts_SE_rad': '十级风圈东南半径',
            '50kts_SW_rad': '十级风圈西南半径',
            '50kts_NW_rad': '十级风圈西北半径',
            '64kts_winds': '十二级风圈',
            '64kts_NE_rad': '十二级风圈东北半径',
            '64kts_SE_rad': '十二级风圈东南半径',
            '64kts_SW_rad': '十二级风圈西南半径',
            '64kts_NW_rad': '十二级风圈西北半径',
            'move_dir': '移动方向',
            'move_spd': '移动速度',
            'p+06hr': '6小时预报',
            'p+12hr': '12小时预报',
            'p+18hr': '18小时预报',
            'p+24hr': '24小时预报',
            'p+36hr': '36小时预报',
        }
    
    def get_format(self) -> list:
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', [' CC', 'ws', 'ccx:3'],  'br',
            'subjective_forecast:$', 'br',
            'cat:S', 'ws', 'name:S', 'ws', 'dom_num:S', 'ws', 'inter_num:S', 'ws', 'initial_time:12', 'ws', 'init_dd:2', 'ws', 'init_hh:2', 'ws', 'init_mm:2', 'ws', 'utc:3', 'br',
            '00hr:4', 'ws', 'ty_la:S', 'ws', 'ty_lo:S', 'ws', 'pressure:S', 'ws', 'wind_spd:S', 'br',
            ['30KTS', '30kts_winds:11', 'ws', '30kts_NE_rad:S', 'ws', 'northeast:S', 'br',
            '30kts_SE_rad:S', 'ws', 'southeast:S', 'br',
            '30kts_SW_rad:S', 'ws', 'southwest:S', 'br',
            '30kts_NW_rad:S', 'ws', 'northwest:S', 'br',], 
            ['50KTS', '50kts_winds:11', 'ws', '50kts_NE_rad:S', 'ws', 'northeast:S', 'br',
            '50kts_SE_rad:S', 'ws', 'southeast:S', 'br',
            '50kts_SW_rad:S', 'ws', 'southwest:S', 'br',
            '50kts_NW_rad:S', 'ws', 'northwest:S', 'br',],
            ['64KTS', '64kts_winds:11', 'ws', '64kts_NE_rad:S', 'ws', 'northeast:S', 'br',
             '64kts_SE_rad:S', 'ws', 'southeast:S', 'br',
             '64kts_SW_rad:S', 'ws', 'southwest:S', 'br',
             '64kts_NW_rad:S', 'ws', 'northwest:S', 'br',],
            'move:4', 'ws', 'move_dir:S', 'ws', 'move_spd:S', 'br',
            ['P+06HR', 'p+06hr:6', 'ws', 'p+06hr_la:S', 'ws', 'p+06hr_lo:S', 'ws', 'p+06hr_pressure:S', 'ws', 'p+06hr_wind_spd:S', 'br',],
            ['P+12HR', 'p+12hr:6', 'ws', 'p+12hr_la:S', 'ws', 'p+12hr_lo:S', 'ws', 'p+12hr_pressure:S', 'ws', 'p+12hr_wind_spd:S', 'br',],
            ['P+18HR', 'p+18hr:6', 'ws', 'p+18hr_la:S', 'ws', 'p+18hr_lo:S', 'ws', 'p+18hr_pressure:S', 'ws', 'p+18hr_wind_spd:S', 'br',],
            ['P+24HR', 'p+24hr:6', 'ws', 'p+24hr_la:S', 'ws', 'p+24hr_lo:S', 'ws', 'p+24hr_pressure:S', 'ws', 'p+24hr_wind_spd:S', 'br',],
            ['P+36HR', 'p+36hr:6', 'ws', 'p+36hr_la:S', 'ws', 'p+36hr_lo:S', 'ws', 'p+36hr_pressure:S', 'ws', 'p+36hr_wind_spd:S',],
        ]
        return msg_format
        
if __name__ == '__main__':
    test_wt = """
WTPQ20 BABJ 242100 CCA
SUBJECTIVE FORECAST
TS PABUK 2426 (2426) INITIAL TIME 242100 UTC
00HR 10.8N 110.6E 1000HPA 18M/S
30KTS WINDS 140KM NORTHEAST
100KM SOUTHEAST
100KM SOUTHWEST
160KM NORTHWEST
MOVE WSW 13KM/H
P+06HR 10.4N 110.0E 1000HPA 18M/S
P+12HR 10.1N 109.4E 1002HPA 15M/S
P+18HR 9.7N 108.7E 1002HPA 15M/S
"""
    wt = WTPQ_BABJ()
    print(wt.explain(wt.parse(test_wt)))