from .message_parser import MessageParser

class TCPQ_BABJ(MessageParser):
    def __init__(self):
        super().__init__(['TCPQ40 BABJ'])

    
    def explain(self, msg: dict) -> str:
        ty_loc_tmpl = {
            '1': '东经{}°，北纬{}°',
            '3': '东经{}°，南纬{}°',
            '5': '西经{}°，南纬{}°',
            '7': '西经{}°，北纬{}°',
        }
        ty_intense_expl = {
            '0': '明显减弱',
            '1': '逐渐减弱',
            '2': '维持',
            '3': '逐渐增强',
            '4': '明显增强',
            '9': '先前未观测，无法提供变化趋势',
            '/': '变化趋势不适用',
        }
        time_intv_expl = {
            '0': '<1h',
            '1': '1-2h',
            '2': '2-3h',
            '3': '3-6h',
            '4': '6-9h',
            '5': '9-12h',
            '6': '12-15h',
            '7': '15-18h',
            '8': '18-21h',
            '9': '21-30h',
            '/': '【不适用】',
        }
        
        expl = [
            self.gen_header_expl(msg, "台风发展报文"),
            f"观测时间：世界协调时{msg['ob_dd']}日{msg['ob_hh']}时{msg['ob_mm']}0分",
        ]
        
        for i in range(5):
            idx_string = f"/{i}" if i > 0 else ''
            if 'name'+idx_string not in msg:
                break
            name = msg['name'+idx_string]
            ty_num = msg['ty_num'+idx_string]
            quad = msg['quadrant'+idx_string]
            ty_la = msg['ty_la'+idx_string]
            ty_lo = msg['ty_lo'+idx_string]
            intense = msg['intense'+idx_string]
            time_intv = msg['time_intv'+idx_string]
            
            ci_raw = msg['ci'+idx_string]
            if ci_raw == '//':
                ci_str = 'CI值不适用'
            elif ci_raw == '99':
                ci_str = '该气旋将逐渐转为温带气旋'
            else:
                ci_str = f"CI值为{ci_raw[0]}.{ci_raw[1]}"
                
            dir = msg['dir'+idx_string]
            spd = msg['spd'+idx_string]
            if dir == '//':
                dir_spd_str = "无移速与移向信息"
            else:
                dir_spd_str = f"过去一段时间以{int(spd)}节的速度向{int(dir)*10}°方向移动"
                
            time_intv_str = "" if time_intv == '/' else f"计算以上运动的时间间隔为{time_intv_expl[time_intv]}"
                
            expl.extend([
                f"热带气旋{name}(编号{ty_num})，当前中心位于"+ty_loc_tmpl[quad].format(float(ty_lo)/10, float(ty_la)/10),
                f"{ci_str}，{dir_spd_str}，强度{ty_intense_expl[intense]}。",
                time_intv_str
            ])
        
        return '\n'.join(expl)
    
    def get_translation(self) -> dict:
        return {
            'type': '报文格式，表示基于台风卫星云图的发展趋势分析',
            'area': '报文涉及的区域，PQ=西北太平洋',
            'ii': '报文类型编号，无具体含义',
            'msg_center': '报文发布单位，BABJ=中央气象台',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'sarep': '观测站位置，CC=地面，DD=海洋',
            'ty_dev': '固定为AA，表示台风过程扩展',
            'ob_dd': '观测日期',
            'ob_hh': '观测小时',
            'ob_mm': '观测分钟',
            'ob_la': '观测站纬度，即39.8N',
            'ob_lo': '观测站经度，即116.5E',
            'name': '热带气旋名称',
            'ty_num': '热带气旋编号',
            'ty_la': '中心纬度',
            'ty_lo': '中心经度',
            'quadrant': '经纬度象限，1=NE,3=SE,5=SW,7=NW',
            'prec': '确定台风位置的准确性，越小精确度越高',
            'horizon': '密闭云区直径，以纬度表示，以当前纬距向下取整',
            'intense': '热带气旋强度24小时变化情况，0-4为减弱或增强，9=未观测，/=未确定',
            'time_intv': '计算热带气旋变化的时间间隔',
            'ci': '强度，以CI值表示',
            'dir': '移动方向，以正北方向顺时针旋转计算，单位为10度',
            'spd': '移动速度，以节表示',
        }
    
    def get_format(self) -> list:
        ty_disc_format = ['.', 'name:S', 'ws', 'ty_num:2', 'ty_la:3', 'ws', 'quadrant:1', 'ty_lo:4', 'ws', 'pad3:1', 'prec:1', 'horizon:1', 'intense:1', 'time_intv:1', 'ws', 'pad4:1', 'ci:2', 'slash:S', 'ws', 'pad5:1', 'dir:2', 'spd:2', 'br',],
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', 'br',
            'sarep:2', 'ty_dev:2', 'ws', 'ob_dd:2', 'ob_hh:2', 'ob_mm:1', 'ws', 'pad1:2', 'ob_la:3', 'ws', 'pad2:1', 'ob_lo:4', 'br',
        ]
        msg_format.extend(ty_disc_format * 5)
        return msg_format
        