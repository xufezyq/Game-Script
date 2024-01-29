# Optick卡顿报告

import copy
import json
from util import *
from opt_file_parser import OptFileParser

PresetEventName = [
    "RLActorMgrNT::Activate",
    "RLRemoteCharacterMgr::Activate",
    "KEventQueueMgr::HandleEventQueue",
    "KG3D_Scene::FetchSceneResults",
    "KG3D_Window::_Present",
    "KG3D_SceneObjectContainer::_UpdateDynamicActor",
    "KG3D_SceneObjectContainer::UpdateMiddleWareScene",
    "KG3D_SceneView::_UpdateCommonRenderData_Optimise",
    "KG3D_SceneView::_UpdateVisibleList",
    "KG3D_Scene::UpdateAsyncLoader",
    "KG3D_SceneView::Render2D",
    "KG3D_SceneView::_Render_MainCamera_OpaqueObject",
    "KG3D_SceneView::_Render_SunCamera_VisibleObject_To_ShadowTexture_CSMVer2",
    "KG3D_SceneView::_Render_SunCamera_VisibleObject_To_ShadowTexture_CSMVer3",
    "KG3D_SceneView::_Render_TopCamera_VisibleObject_To_DepthTexture",
    "KG3D_SceneView::RenderGBuffers",
    "KG3D_SceneView::renderMainCamera_ParticleSystem",
]

style1 = set_style(0x02)  # 水平方向上居中对齐
style2 = set_style(0x01)  # 水平方向上居左对齐


class OptJankReport(OptFileParser):

    def __init__(self, input_path, frame_elapse_limit, event_elapse_limit, event_proportion_limit):
        super(OptJankReport, self).__init__(input_path)
        self.preset_event_index = []                            # 预设事件对应的索引
        self.jank_count = 0                                     # 卡顿帧数
        self.frame_elapse_limit = frame_elapse_limit            # 帧耗时限制，暂定80ms
        self.event_elapse_limit = event_elapse_limit            # 事件耗时限制，暂定6ms
        self.event_proportion_limit = event_proportion_limit    # 事件耗时占比限制，暂定8%
        self.jank_frame = []                                    # 卡顿帧数据集合（每个元素是一个卡顿帧相关的字典）
        self.jank_stat = {}                                     # 卡顿帧相关数据统计
        self.jank_json = {}                                     # 卡顿帧Json结果

    def get_preset_event_index(self):
        """ 获取预设事件名称对应的索引 """
        event_count = len(self.event_descs)
        for event_index in range(event_count):
            event_name = self.event_descs[event_index].split('(')[0]
            for name in PresetEventName:
                if name == event_name:
                    self.preset_event_index.append(event_index)

    def get_jank_frame(self):
        """ 获取卡顿帧数据 """
        for frame_index in range(self.cpu_frame_count):  # 遍历所有帧，寻找卡顿帧并解析
            frame_elapse = self.cpu_frames_time_ms[frame_index]
            if frame_elapse >= self.frame_elapse_limit:  # 帧耗时过高，判定为卡顿帧
                temp = {
                    'frame_index': frame_index,
                    'frame_elapse': round(frame_elapse, 2),
                    'frame_events': [],
                    'selected_events': []
                }
                for event in self.frame_events[frame_index]:  # 获取此帧的每个事件的耗时
                    event_elapse = get_round_time(event[1] - event[0])
                    event_index = event[2]
                    temp['frame_events'].append([event_index, event_elapse])
                self.jank_frame.append(temp)
        self.jank_count = len(self.jank_frame)

    def merge_event_elapse(self):
        """ 合并相同事件的耗时并计算其占比 """
        for frame in self.jank_frame:
            # merge elapse by the same event index
            main_index_dict = {}
            for event in frame['frame_events']:
                event_index, event_elapse = event[0], event[1]
                if event_index not in main_index_dict.keys():
                    main_index_dict[event_index] = {
                        'elapse': event_elapse
                    }
                else:
                    main_index_dict[event_index]['elapse'] += event_elapse
            # calculate proportion
            for event_index in main_index_dict.keys():
                event_proportion = round(main_index_dict[event_index]['elapse'] * 100 / frame['frame_elapse'], 2)
                main_index_dict[event_index]['proportion'] = event_proportion
            # update
            frame['frame_events'] = main_index_dict

    def select_event(self):
        """ 从卡顿帧的堆栈中筛选符合条件的事件索引 """
        for frame in self.jank_frame:
            for event_index in frame['frame_events'].keys():
                if event_index in self.preset_event_index:
                    frame['selected_events'].append(event_index)

    def stat_jank_data(self):
        """ 统计卡顿帧相关数据（相关比例，最大耗时，最小耗时，平均耗时） """
        for event_index in self.preset_event_index:
            self.jank_stat[event_index] = {
                'name': self.event_descs[event_index].split('(')[0],
                'elapse': [],
                'elapse_frame': [],  # 满足耗时要求的帧索引列表
                'proportion_frame': [],  # 满足耗时占比要求的帧索引列表
                'min_elapse': 0,
                'max_elapse': 0,
                'avg_elapse': 0
            }
        for frame in self.jank_frame:
            for event_index in frame['selected_events']:
                event = frame['frame_events'][event_index]
                elapse, proportion = event['elapse'], event['proportion']
                self.jank_stat[event_index]['elapse'].append(elapse)
                if elapse >= self.event_elapse_limit:
                    self.jank_stat[event_index]['elapse_frame'].append(frame['frame_index'])
                if proportion >= self.event_proportion_limit:
                    self.jank_stat[event_index]['proportion_frame'].append(frame['frame_index'])
        for event_index in self.jank_stat.keys():
            elapse_list = self.jank_stat[event_index]['elapse']
            if not elapse_list:  # 特殊处理
                elapse_list = [0, ]
            self.jank_stat[event_index]['min_elapse'] = round(min(elapse_list), 2)
            self.jank_stat[event_index]['max_elapse'] = round(max(elapse_list), 2)
            self.jank_stat[event_index]['avg_elapse'] = round(sum(elapse_list)/len(elapse_list), 2)

    def write_table(self):
        """ 写卡顿帧数据至表 """
        # 准备工作
        func_name_index = {}  # k=name, v=index
        for i in range(len(PresetEventName)):
            func_name_index[PresetEventName[i]] = i + 1
        f = xlwt.Workbook()
        # 写入卡顿帧的指定函数的耗时
        sheet1 = f.add_sheet('event_elapse (ms)', cell_overwrite_ok=True)
        sheet1.write(0, 0, "Func", style1)
        for i in func_name_index.keys():
            sheet1.write(func_name_index[i], 0, i, style2)
        cur_col_index = 1
        for frame in self.jank_frame:
            sheet1.write(0, cur_col_index, frame['frame_index'], style1)
            for event_index in frame['selected_events']:
                name = self.event_descs[event_index].split('(')[0]
                event = frame['frame_events'][event_index]
                elapse, proportion = event['elapse'], event['proportion']
                sheet1.write(func_name_index[name], cur_col_index, elapse, style1)
            cur_col_index += 1
        # 写入卡顿帧的指定函数的耗时占比
        sheet2 = f.add_sheet('event_proportion (%)', cell_overwrite_ok=True)
        sheet2.write(0, 0, "Func", style1)
        for i in func_name_index.keys():
            sheet2.write(func_name_index[i], 0, i, style2)
        sheet2.write(len(PresetEventName) + 1, 0, "耗时占比总和", style2)
        cur_col_index = 1
        for frame in self.jank_frame:
            sheet2.write(0, cur_col_index, frame['frame_index'], style1)
            proportion_sum = 0
            for event_index in frame['selected_events']:
                name = self.event_descs[event_index].split('(')[0]
                event = frame['frame_events'][event_index]
                elapse, proportion = event['elapse'], event['proportion']
                proportion_sum += proportion
                sheet2.write(func_name_index[name], cur_col_index, proportion, style1)
            sheet2.write(len(PresetEventName) + 1, cur_col_index, round(proportion_sum, 2), style1)
            cur_col_index += 1
        # 写入指定函数的高耗时帧比例、高占比帧比例、最小耗时、最大耗时、平均耗时
        sheet3 = f.add_sheet('others', cell_overwrite_ok=True)
        sheet3.write(0, 0, "Func", style1)
        for i in func_name_index.keys():
            sheet3.write(func_name_index[i], 0, i, style1)
        sheet3.write(0, 1, "elapse_frame", style1)
        sheet3.write(0, 2, "prop_frame", style1)
        sheet3.write(0, 3, "min_elapse", style1)
        sheet3.write(0, 4, "max_elapse", style1)
        sheet3.write(0, 5, "avg_elapse", style1)
        for event_index in self.jank_stat.keys():
            event_name = self.event_descs[event_index].split('(')[0]
            sheet3.write(func_name_index[event_name], 1, f"{len(self.jank_stat[event_index]['elapse_frame'])}/{self.jank_count}", style1)
            sheet3.write(func_name_index[event_name], 2, f"{len(self.jank_stat[event_index]['proportion_frame'])}/{self.jank_count}", style1)
            sheet3.write(func_name_index[event_name], 3, f"{self.jank_stat[event_index]['min_elapse']}ms", style1)
            sheet3.write(func_name_index[event_name], 4, f"{self.jank_stat[event_index]['max_elapse']}ms", style1)
            sheet3.write(func_name_index[event_name], 5, f"{self.jank_stat[event_index]['avg_elapse']}ms", style1)
        # 保存文件
        f.save(self.input_path[0:-4]+"_jank.xls")

    def write_json(self):
        json_data = {
            'frame_count': self.cpu_frame_count,
            'jank_count': self.jank_count,
            'func': {},
            'frames': {}
        }
        # 函数相关
        for event_index in self.preset_event_index:
            json_data['func'][event_index] = {
                'name': self.event_descs[event_index].split('(')[0],
                'elapse_frame': None,
                'prop_frame': None,
                'min_elapse': None,
                'max_elapse': None,
                'avg_elapse': None
            }
        # 每帧的函数耗时及占比
        for frame in self.jank_frame:
            json_data['frames'][frame['frame_index']] = {
                'title': f"{frame['frame_index']}({frame['frame_elapse']}ms)",
                'prop_sum': 0,
                'events': {
                    'attr': ["event_index", "event_elapse", "event_proportion"],
                    'content': []
                }
            }
            for event_index in frame['selected_events']:
                event = frame['frame_events'][event_index]
                #  name = self.event_descs[event_index].split('(')[0]
                elapse, proportion = event['elapse'], event['proportion']
                json_data['frames'][frame['frame_index']]['events']['content'].append([event_index, elapse, proportion])
                json_data['frames'][frame['frame_index']]['prop_sum'] += proportion
            json_data['frames'][frame['frame_index']]['prop_sum'] = round(json_data['frames'][frame['frame_index']]['prop_sum'], 1)
        # 统计
        for event_index in self.jank_stat.keys():
            json_data['func'][event_index]['elapse_frame'] = f"{len(self.jank_stat[event_index]['elapse_frame'])}/{self.jank_count}"
            json_data['func'][event_index]['prop_frame'] = f"{len(self.jank_stat[event_index]['proportion_frame'])}/{self.jank_count}"
            json_data['func'][event_index]['min_elapse'] = f"{self.jank_stat[event_index]['min_elapse']}ms"
            json_data['func'][event_index]['max_elapse'] = f"{self.jank_stat[event_index]['max_elapse']}ms"
            json_data['func'][event_index]['avg_elapse'] = f"{self.jank_stat[event_index]['avg_elapse']}ms"
        with open(self.input_path[0:-4]+"_jank.json", "w") as f:
            json.dump(json_data, f, indent=2)

    def run(self):
        self.read_opt_content()
        self.parse()
        self.get_preset_event_index()
        self.get_jank_frame()
        self.merge_event_elapse()
        self.select_event()
        self.stat_jank_data()
        # self.write_table()
        self.write_json()


if __name__ == '__main__':
    xx = OptJankReport(r"C:\Users\shichunkang\Desktop\1080_外网_家园卡顿重现_1.opt", 80, 6, 10)
    xx.run()


