from .message_parser import MessageParser

class WTPQ_BABJ(MessageParser):
    def __init__(self):
        super().__init__('WTPQ_BABJ')
    
    def explain(self, msg: dict) -> str:
        cat_expl = {
            'TD': '热带低压',
            'TS': '热带风暴',
            'STS': '强热带风暴',
            'TY': '台风',
            'STY': '强台风',
            'SuperTY': '超强台风',
        }
        
        move_dir_expl = {
            'N': '北',
            'NNE': '东北偏北',
            'NE': '东北',
            'ENE': '东北偏东',
            'E': '东',
            'ESE': '东偏南',
            'SE': '东南',
            'SSE': '东南偏东',
            'S': '南',
            'SSW': '西南偏西',
            'SW': '西南',
            'WSW': '西南偏西',
            'W': '西',
            'WNW': '西北偏北',
            'NW': '西北',
            'NNW': '西北偏北',
        }
        
        if 'dom_num' not in msg:
            name_str = f"热带低压{msg['name']} 未命名"
        else:
            name_str = f"{cat_expl[msg['cat']]}{msg['name']}，编号{msg['dom_num']}，国际编号{msg['inter_num']}"
        expl = [
            f"中央气象台于世界协调时{msg['msg_dd']}日{msg['msg_hh']}时{msg['msg_mm']}分发布台风综合预报报文",
            name_str,
            f"起报时间：世界协调时{msg['init_dd']}日{msg['init_hh']}时{msg['init_mm']}分",
            f"当前位置：{msg['ty_la']} {msg['ty_lo']}",
            f"中心气压：{msg['wind_spd']}，最大风速：{msg['wind_spd']}",
        ]
        if '30kts_winds' in msg:
            expl.append(f"七级风圈半径：东北方向{msg['30kts_NE_rad']}、东南方向{msg['30kts_SE_rad']}、西南方向{msg['30kts_SW_rad']}、西北方向{msg['30kts_NW_rad']}")
        if '50kts_winds' in msg:
            expl.append(f"十级风圈半径：东北方向{msg['50kts_NE_rad']}、东南方向{msg['50kts_SE_rad']}、西南方向{msg['50kts_SW_rad']}、西北方向{msg['50kts_NW_rad']}")
        if '64kts_winds' in msg:
            expl.append(f"十二级风圈半径：东北方向{msg['64kts_NE_rad']}、东南方向{msg['64kts_SE_rad']}、西南方向{msg['64kts_SW_rad']}、西北方向{msg['64kts_NW_rad']}")
            
        expl.append(f"移向移速：以{msg['move_spd']}向{move_dir_expl[msg['move_dir']]}移动")
        if 'p+xxhr' in msg:
            expl.append(f"路径预报：")
        for i in range(10):
            idx_string = f"/{i}" if i > 0 else ''
            if 'p+xxhr'+idx_string not in msg:
                break
            hr = msg['p+xxhr'+idx_string][2:-2]
            la = msg['p+xxhr_la'+idx_string]
            lo = msg['p+xxhr_lo'+idx_string]
            pressure = msg['p+xxhr_pressure'+idx_string]
            wind_spd = msg['p+xxhr_wind_spd'+idx_string]
            expl.append(f"+{hr}h：{la} {lo}，中心气压{pressure}，最大风速{wind_spd}")
        report = '\n'.join(expl)
        report = report.replace('HPA', 'hPa').replace('M/S', 'm/s').replace('KM', 'km').replace('/H', '/h')
        return report
    
    def get_translation(self) -> dict:
        translation = {
            'type': '报文格式，表示台风警告报文',
            'area': '报文涉及的区域，PQ=西北太平洋',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，BABJ=中央气象台',
            'ccx': '第几次修订，如A=第一次修订',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'subjective_forecast': '主观预报，即预报员对未来台风的预测',
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
            'p+xxhr': '路径预报未来时刻',
            'p+xxhr_la': '预报中心纬度',
            'p+xxhr_lo': '预报中心经度',
            'p+xxhr_pressure': '预报中心气压',
            'p+xxhr_wind_spd': '预报中心最大风速',
        }
        return translation
    
    def get_format(self) -> list:
        route_forecast_format = ['P+', 'p+xxhr:S', 'ws', 'p+xxhr_la:S', 'ws', 'p+xxhr_lo:S', 'ws', 'p+xxhr_pressure:S', 'ws', 'p+xxhr_wind_spd:S', 'br',]
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', [' CC', 'ws', 'ccx:3'],  'br',
            'subjective_forecast:$', 'br',
            'cat:S', 'ws', 'name:S', [' [0-9]', 'ws', 'dom_num:S', 'ws', 'inter_num:S'], 'ws', 'initial_time:12', 'ws', 'init_dd:2', 'init_hh:2', 'init_mm:2', 'ws', 'utc:3', 'br',
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
        ]
        msg_format.extend([route_forecast_format] * 10)
        return msg_format