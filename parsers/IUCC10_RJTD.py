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
            number = bufr_kv['TYPHOON INTERNATIONAL COMMON NUMBER (TYPHOON COMMITTEE)']

            lat = bufr_kv['LATITUDE (COARSE ACCURACY)']
            lon = bufr_kv['LONGITUDE (COARSE ACCURACY)']

            ci = bufr_kv['CURRENT INTENSITY (CI) NUMBER OF THE TROPICAL CYCLONE']
            dt = bufr_kv['DATA TROPICAL (DT) NUMBER OF THE TROPICAL CYCLONE']
            met = bufr_kv['MODEL EXPECTED TROPICAL (MET) NUMBER OF THE TROPICAL CYCLONE']
            pt = bufr_kv['PATTERN TROPICAL (PT) NUMBER OF THE TROPICAL CYCLONE']
            ft = bufr_kv['FINAL TROPICAL (T) NUMBER OF THE TROPICAL CYCLONE']

            trend = bufr_kv['TREND OF PAST 24-HOUR CHANGE (+: DEVELOPED, -: WEAKENED)']

            expl = [
                self.gen_header_expl(msg, "卫星分析报告"),
                f"观测时间: {obs_time}",
                f"热带气旋{name}(编号{number})，位置：{lat}N {lon}E",
                f"德法结论：CI={ci}, DT={dt}, MET={met}, PT={pt}, FT={ft}",
                f"过去24小时变化趋势：{trend}"
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
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2', [' CC', 'ws', 'ccx:3'], 'br',
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