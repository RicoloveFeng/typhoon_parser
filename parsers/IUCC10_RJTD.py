from calendar import c
from .message_parser import MessageParser
from .deepseek_client import send_request
class IUCC10_RJTD(MessageParser):
    def __init__(self):
        headers = ["IUCC10 RJTD"]
        super().__init__(headers)

    def explain(self, msg: dict) -> str:
        # remarks的数据格式：
        # ORIGINATING CENTRE 34
        # IDENTIFICATION OF ORIGINATING/GENERATING SUB-CENTRE 0
        # YEAR 2026
        # MONTH 3
        # DAY 11
        # HOUR 0
        # MINUTE 0
        # SATELLITE IDENTIFIER 174
        # SATELLITE INTENSITY ANALYSIS METHOD OF TROPICAL CYCLONE 2
        # DELAYED DESCRIPTOR REPLICATION FACTOR 1
        # WMO LONG STORM NAME b'Nuri '
        # TYPHOON INTERNATIONAL COMMON NUMBER (TYPHOON COMMITTEE) b'2603'
        # IDENTIFICATION NUMBER OF TROPICAL CYCLONE 3
        # METEOROLOGICAL ATTRIBUTE SIGNIFICANCE 1
        # LATITUDE (COARSE ACCURACY) 10.98
        # LONGITUDE (COARSE ACCURACY) 138.58
        # METEOROLOGICAL ATTRIBUTE SIGNIFICANCE None
        # TIME INTERVAL OF THE TROPICAL CYCLONE ANALYSIS 6
        # DIRECTION OF MOTION OF FEATURE 136
        # SPEED OF MOTION OF FEATURE 4.12
        # ACCURACY OF GEOGRAPHICAL POSITION OF THE TROPICAL CYCLONE 3
        # MEAN DIAMETER OF THE OVERCAST CLOUD OF THE TROPICAL CYCLONE 2
        # APPARENT 24-HOUR CHANGE IN INTENSITY OF TROPICAL CYCLONE 4
        # CURRENT INTENSITY (CI) NUMBER OF THE TROPICAL CYCLONE 2.5
        # DATA TROPICAL (DT) NUMBER OF THE TROPICAL CYCLONE 2.5
        # CLOUD PATTERN TYPE OF THE DT- NUMBER 1
        # MODEL EXPECTED TROPICAL (MET) NUMBER OF THE TROPICAL CYCLONE 2.0
        # TREND OF PAST 24-HOUR CHANGE (+: DEVELOPED, -: WEAKENED) 1.0
        # PATTERN TROPICAL (PT) NUMBER OF THE TROPICAL CYCLONE 2.5
        # CLOUD PICTURE TYPE OF THE PT- NUMBER 2
        # FINAL TROPICAL (T) NUMBER OF THE TROPICAL CYCLONE 2.5
        # TYPE OF THE FINAL T-NUMBER 2
        try:
            all_content = msg['remarks'].split('\n')
            def gen_bufr_kv(line):
                if "b'" in line:
                    k = line.split("b'")[0].strip()
                    v = line.split("b'")[1].split("'")[0]
                else:
                    k = " ".join(line.split(" ")[:-1])
                    v = line.split(" ")[-1]
                return k, v
            bufr_kv = dict(gen_bufr_kv(line) for line in all_content)
            year = bufr_kv['YEAR']
            month = bufr_kv['MONTH']
            day = bufr_kv['DAY']
            hour = bufr_kv['HOUR']
            minute = bufr_kv['MINUTE']
            obs_time = f"{year}年{month}月{day}日{hour}时{minute}分"

            name = bufr_kv['WMO LONG STORM NAME']
            if 'nameless' in name:
                name = "未命名热带低压"
            else:
                name = f"热带气旋{name}"
                
            number = bufr_kv['TYPHOON INTERNATIONAL COMMON NUMBER (TYPHOON COMMITTEE)']
            if number.isspace():
                number = f"（内部编号{bufr_kv['IDENTIFICATION NUMBER OF TROPICAL CYCLONE']}）"
            else:
                number = f"（编号{number}）"

            lat = bufr_kv['LATITUDE (COARSE ACCURACY)']
            lon = bufr_kv['LONGITUDE (COARSE ACCURACY)']
            
            direction = bufr_kv['DIRECTION OF MOTION OF FEATURE']
            speed = bufr_kv['SPEED OF MOTION OF FEATURE']
            
            trend = bufr_kv['APPARENT 24-HOUR CHANGE IN INTENSITY OF TROPICAL CYCLONE']
            trend_table = {
                '0': '大幅减弱',
                '1': '减弱',
                '2': '保持',
                '3': '增强',
                '4': '大幅增强',
                '9': '先前未观测',
                '10': '未分析',
            }
            trend = trend_table.get(trend, '*解析失败*')

            ci = bufr_kv['CURRENT INTENSITY (CI) NUMBER OF THE TROPICAL CYCLONE']
            if ci == 'None':
                dvorak_str = "本报无德法分析"
            else:
                dt = bufr_kv['DATA TROPICAL (DT) NUMBER OF THE TROPICAL CYCLONE']
                cloud_pattern_type = bufr_kv['CLOUD PATTERN TYPE OF THE DT- NUMBER']
                cloud_pattern_table = {
                    '1': '弯曲云带',
                    '2': '切离度',
                    '3': '风眼',
                    '4': '云卷眼',
                    '5': '中心密闭云区（CDO）',
                    '6': '嵌匿中心',
                    '7': '中心冷云盖（CCC)'
                }
                cloud_pattern = cloud_pattern_table.get(cloud_pattern_type, cloud_pattern_type)
                
                met = bufr_kv['MODEL EXPECTED TROPICAL (MET) NUMBER OF THE TROPICAL CYCLONE']
                pt = bufr_kv['PATTERN TROPICAL (PT) NUMBER OF THE TROPICAL CYCLONE']
                ft = bufr_kv['FINAL TROPICAL (T) NUMBER OF THE TROPICAL CYCLONE']
                dbo_table = {
                    '1': 'DT',
                    '2': 'PT',
                    '3': 'MET'
                }
                dbo = dbo_table.get(bufr_kv['TYPE OF THE FINAL T-NUMBER'], bufr_kv['TYPE OF THE FINAL T-NUMBER'])
                met_fix = bufr_kv['TREND OF PAST 24-HOUR CHANGE (+: DEVELOPED, -: WEAKENED)']

                cloud_picture_type = bufr_kv['CLOUD PICTURE TYPE OF THE PT- NUMBER']
                cloud_picture_table = {
                    '1': '弯曲云带型',
                    '2': '中心密闭云区（CDO）型',
                    '3': '切离型',
                }
                cloud_picture = cloud_picture_table.get(cloud_picture_type, cloud_picture_type)
                
                dvorak_spd = self.dvorak_kts(ci, 'jma')

                dvorak_conclusion = [
                    f'德法分析：',
                    f'- 数据T值 DT={dt}, 基于{cloud_pattern}分析',
                    f'- 模型预估T值 MET={met}, 趋势为{met_fix}',
                    f'- 云型T值 PT={pt}, 特征类型为{cloud_picture}',
                    f'-> 结论：最终T值 FT={ft}, 结论基于{dbo}。现时强度 CI={ci}(~{dvorak_spd}kts)'
                ]

                dvorak_str = '\n'.join(dvorak_conclusion)

            
            expl = [
                self.gen_header_expl(msg, "卫星分析报告"),
                f"观测时间：{obs_time}",
                f"观测对象：{name}{number}，位置：{lat}N {lon}E",
                f"移速移向：以{speed}m/s向{direction}°移动",
                f"过去24小时变化趋势：{trend}",
                dvorak_str
            ]
        except Exception as e:
            print(e)
            expl = [
                self.gen_header_expl(msg, "卫星分析报告"),
                msg['remarks']
            ]
        return '\n'.join(expl)
    
    def get_translation(self) -> dict:
        return {
            'type': '报文格式，表示高空观测数据',
            'area': 'A1是报文的数据类型，C=卫星分析报告SAREP；A2是报文涉及的区域，C=北半球',
            'ii': '报文类型编号，固定为10',
            'msg_center': '报文发布单位，RJTD=日本气象厅',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'remarks': 'BUFR解析数据预览',
        }
    
    def get_format(self) -> list:
        # IUCC10 RJTD 100000CCA <- no space
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', ['CC', 'ccx:3'], 'br',
            'remarks:$$',
        ]
        return msg_format
        
    def get_location_if_exists(self, msg: dict) -> list:
        all_content = msg['remarks'].split('\n')
        def gen_bufr_kv(line):
            if "b'" in line:
                k = line.split("b'")[0].strip()
                v = line.split("b'")[1].split("'")[0]
            else:
                k = " ".join(line.split(" ")[:-1])
                v = line.split(" ")[-1]
            return k, v
        bufr_kv = dict(gen_bufr_kv(line) for line in all_content)
        lat = bufr_kv['LATITUDE (COARSE ACCURACY)']
        lon = bufr_kv['LONGITUDE (COARSE ACCURACY)']
        return [lat, lon]