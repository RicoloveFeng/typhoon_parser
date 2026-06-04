from .message_parser import MessageParser


class IUCC0x_VHHH(MessageParser):
    def __init__(self):
        # VHHH 香港天文台只发布 IUCC01 到 IUCC04
        headers = [f"IUCC{ii:02d} VHHH" for ii in range(1, 5)]
        super().__init__(headers)

    def explain(self, msg: dict) -> str:
        # remarks的数据格式（与 RJTD 的 IUCC10 结构一致）：
        # ORIGINATING CENTRE 110
        # IDENTIFICATION OF ORIGINATING/GENERATING SUB-CENTRE 0
        # YEAR 2026
        # MONTH 6
        # DAY 3
        # HOUR 23
        # MINUTE 50
        # SATELLITE IDENTIFIER 174
        # METHOD OF TROPICAL CYCLONE INTENSITY ANALYSIS USING SATELLITE DATA 2
        # DELAYED DESCRIPTOR REPLICATION FACTOR 1
        # WMO LONG STORM NAME b'NoName    '
        # TYPHOON INTERNATIONAL COMMON NUMBER (TYPHOON COMMITTEE) b'null'
        # IDENTIFICATION NUMBER OF TROPICAL CYCLONE 7
        # METEOROLOGICAL ATTRIBUTE SIGNIFICANCE 1
        # LATITUDE (COARSE ACCURACY) 18.0
        # LONGITUDE (COARSE ACCURACY) 117.2
        # METEOROLOGICAL ATTRIBUTE SIGNIFICANCE None
        # TIME INTERVAL OF THE TROPICAL CYCLONE ANALYSIS 4
        # DIRECTION OF MOTION OF FEATURE 69
        # SPEED OF MOTION OF FEATURE 8.4
        # ACCURACY OF GEOGRAPHICAL POSITION OF THE TROPICAL CYCLONE 5
        # MEAN DIAMETER OF THE OVERCAST CLOUD OF THE TROPICAL CYCLONE 5
        # APPARENT 24-HOUR CHANGE IN INTENSITY OF TROPICAL CYCLONE None
        # CURRENT INTENSITY (CI) NUMBER OF THE TROPICAL CYCLONE 1.0
        # DATA TROPICAL (DT) NUMBER OF THE TROPICAL CYCLONE 1.0
        # CLOUD PATTERN TYPE OF THE DT- NUMBER 1
        # MODEL EXPECTED TROPICAL (MET) NUMBER OF THE TROPICAL CYCLONE None
        # TREND OF PAST 24-HOUR CHANGE (+: DEVELOPED, -: WEAKENED) None
        # PATTERN TROPICAL (PT) NUMBER OF THE TROPICAL CYCLONE None
        # CLOUD PICTURE TYPE OF THE PT- NUMBER None
        # FINAL TROPICAL (T) NUMBER OF THE TROPICAL CYCLONE 1.0
        # TYPE OF THE FINAL T-NUMBER 1
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

            # VHHH 的 WMO LONG STORM NAME 可能为 "NoName    " 或 "nameless"
            name = bufr_kv['WMO LONG STORM NAME']
            if 'nameless' in name.lower() or 'noname' in name.lower():
                name = "未命名热带低压"
            else:
                name = f"热带气旋{name.strip()}"

            # VHHH 的国际编号可能为 "null"（未指定）
            number = bufr_kv['TYPHOON INTERNATIONAL COMMON NUMBER (TYPHOON COMMITTEE)']
            if number in ('null', '') or number.isspace():
                number = f"（内部编号{bufr_kv['IDENTIFICATION NUMBER OF TROPICAL CYCLONE']}）"
            else:
                number = f"（编号{number}）"

            lat = bufr_kv['LATITUDE (COARSE ACCURACY)']
            lon = bufr_kv['LONGITUDE (COARSE ACCURACY)']

            direction = bufr_kv['DIRECTION OF MOTION OF FEATURE']
            speed = bufr_kv['SPEED OF MOTION OF FEATURE']

            # VHHH 的趋势可能为 None
            trend = bufr_kv['APPARENT 24-HOUR CHANGE IN INTENSITY OF TROPICAL CYCLONE']
            trend_table = {
                '0': '大幅减弱',
                '1': '减弱',
                '2': '保持',
                '3': '增强',
                '4': '大幅增强',
                '9': '先前未观测',
                '10': '未分析',
                'None': '未分析',
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
                dbo = dbo_table.get(bufr_kv['TYPE OF THE FINAL T-NUMBER'],
                                    bufr_kv['TYPE OF THE FINAL T-NUMBER'])
                met_fix = bufr_kv['TREND OF PAST 24-HOUR CHANGE (+: DEVELOPED, -: WEAKENED)']

                cloud_picture_type = bufr_kv['CLOUD PICTURE TYPE OF THE PT- NUMBER']
                cloud_picture_table = {
                    '1': '弯曲云带型',
                    '2': '中心密闭云区（CDO）型',
                    '3': '切离型',
                }
                cloud_picture = cloud_picture_table.get(cloud_picture_type, cloud_picture_type)

                # VHHH 使用 JTWC(usa) × 0.93 的 Dvorak 风速转换
                dvorak_spd = self.dvorak_kts(ci, 'hko')

                # VHHH 数据中 MET、PT、met_fix、cloud_picture 可能为 None
                dvorak_lines = ['德法分析：']
                dvorak_lines.append(f'- 数据T值 DT={dt}, 基于{cloud_pattern}分析')
                if met != 'None' and met_fix != 'None':
                    dvorak_lines.append(f'- 模型预估T值 MET={met}, 趋势为{met_fix}')
                elif met_fix != 'None':
                    dvorak_lines.append(f'- 模型预估T值 MET={met}, 趋势为{met_fix}')
                else:
                    dvorak_lines.append(f'- 模型预估T值 MET={met}, 趋势未分析')
                if pt != 'None' and cloud_picture_type != 'None':
                    dvorak_lines.append(f'- 云型T值 PT={pt}, 特征类型为{cloud_picture}')
                elif pt != 'None':
                    dvorak_lines.append(f'- 云型T值 PT={pt}')
                else:
                    dvorak_lines.append(f'- 云型T值 PT=未分析')
                dvorak_lines.append(f'-> 结论：最终T值 FT={ft}, 结论基于{dbo}。现时强度 CI={ci}(~{dvorak_spd}kts)')

                dvorak_str = '\n'.join(dvorak_lines)

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
            'ii': '报文类型编号，VHHH使用01-04',
            'msg_center': '报文发布单位，VHHH=香港天文台',
            'msg_dd': '报文发布日期',
            'msg_hh': '报文发布小时',
            'msg_mm': '报文发布分钟',
            'remarks': 'BUFR解析数据预览',
        }

    def get_format(self) -> list:
        # IUCC0x VHHH XXXXXX
        msg_format = [
            'type:2', 'area:2', 'ii:2', 'ws', 'msg_center:4', 'ws', 'msg_dd:2', 'msg_hh:2', 'msg_mm:2',
            ['CC', 'ccx:3'], 'br',
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
