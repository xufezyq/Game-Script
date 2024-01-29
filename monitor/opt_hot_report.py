# Optick热点函数解析，包含TP90热点函数和全程热点函数

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


class OptHotReport(OptFileParser):

    def __init__(self, input_path):
        super(OptHotReport, self).__init__(input_path)
        self.preset_event_index = []  # 预设事件对应的索引
        self.frame = []  # 帧数据集合（每个元素是一个帧相关的字典）
        self.stat = {}  # 帧相关数据统计
        self.stat_result = []  # 最终的统计结果
        self.json_result = {}  # 最终的Json
        # tp90
        self.tp90_value = 0  # TP90值（帧耗时）
        self.tp90_frame_count = 0  # TP90帧数量

    def reset(self):
        self.frame = []
        self.stat = {}
        self.stat_result = []
        self.json_result = {}

    def get_preset_event_index(self):
        """ 获取预设事件名称对应的索引 """
        event_count = len(self.event_descs)
        for event_index in range(event_count):
            event_desc = self.event_descs[event_index]
            for name in PresetEventName:
                if name in event_desc:
                    self.preset_event_index.append(event_index)

    def get_tp90_value(self):
        """ 获取tp90的值 """
        sort_cpu_frames_time_ms = copy.deepcopy(self.cpu_frames_time_ms)
        sort_cpu_frames_time_ms.sort()
        self.tp90_value = sort_cpu_frames_time_ms[round(self.cpu_frame_count * 0.9)]
        print(f"TP90 Elapse = {self.tp90_value}ms, TP90 FPS = {1000 / self.tp90_value}")

    def get_frames(self, is_tp90):
        """ 获取帧数据（帧索引，帧耗时，帧事件列表（事件索引，事件耗时）） """
        for frame_index in range(self.cpu_frame_count):
            frame_elapse = self.cpu_frames_time_ms[frame_index]
            if is_tp90 and frame_elapse > self.tp90_value:  # tp90特殊处理
                continue
            temp = {
                'frame_index': frame_index,
                'frame_elapse': frame_elapse,
                'frame_events': []
            }
            for event in self.frame_events[frame_index]:  # 获取此帧的每个事件的耗时
                event_elapse = get_round_time(event[1] - event[0])
                event_index = event[2]
                temp['frame_events'].append([event_index, event_elapse])
            self.frame.append(temp)
        if is_tp90:
            self.tp90_frame_count = len(self.frame)

    def merge_elapse(self):
        """ 合并同一帧中相同事件的耗时 """
        for frame in self.frame:
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
            # update
            frame['frame_events'] = main_index_dict

    def stat_data(self, is_tp90):
        """ 统计每一个事件在此次采集中的平均耗时及占比 """
        frame_elapse = []
        event_elapse = {}
        event_desc_len = len(self.event_descs)
        for i in range(event_desc_len):
            event_elapse[i] = []
        # 计算此次采集的帧平均耗时
        if is_tp90:
            for frame in self.frame:
                frame_elapse.append(frame['frame_elapse'])
            avg_frame_elapse = sum(frame_elapse) / len(frame_elapse)
        else:
            avg_frame_elapse = sum(self.cpu_frames_time_ms) / self.cpu_frame_count
        # 提取每帧每事件的耗时
        for frame in self.frame:
            for event_index in frame['frame_events'].keys():
                event_elapse[event_index].append(frame['frame_events'][event_index]['elapse'])
        # 计算每事件的平均耗时
        for event_index in event_elapse.keys():
            event_name = self.event_descs[event_index].split('(')[0]
            if not event_elapse[event_index]:
                avg_event_elapse = 0
                avg_event_proportion = 0
            else:
                avg_event_elapse = sum(event_elapse[event_index]) / len(event_elapse[event_index])
                avg_event_proportion = (avg_event_elapse / avg_frame_elapse) * 100
            self.stat[event_index] = (event_name, round(avg_event_elapse, 2), round(avg_event_proportion, 2))
        # 获取特定函数的统计数据
        for event_index in self.preset_event_index:
            self.stat_result.append(self.stat[event_index])
        return self.stat_result

    def get_json(self, tp90_stat_result, all_stat_result):
        self.json_result = {
            'tp90': {
                "attr": ["name", "elapse", "proportion"],
                "content": tp90_stat_result,
                "tp90_value": round(1000 / self.tp90_value, 2)
            },
            'all': {
                "attr": ["name", "elapse", "proportion"],
                "content": all_stat_result
            }
        }

    def write_table(self):
        f = xlwt.Workbook()
        sheet1 = f.add_sheet("TP90_Hot", cell_overwrite_ok=True)
        sheet1.write(0, 0, "Func", style1)
        sheet1.write(0, 1, "AvgElapse(ms)", style1)
        sheet1.write(0, 2, "AvgProportion(%)", style1)
        cur_row_index = 1
        for item in self.json_result['tp90']['content']:
            name, elapse, proportion = item[0], item[1], item[2]
            sheet1.write(cur_row_index, 0, name, style2)
            sheet1.write(cur_row_index, 1, elapse, style1)
            sheet1.write(cur_row_index, 2, proportion, style1)
            cur_row_index += 1
        sheet2 = f.add_sheet("All_Hot", cell_overwrite_ok=True)
        sheet2.write(0, 0, "Func", style1)
        sheet2.write(0, 1, "AvgElapse(ms)", style1)
        sheet2.write(0, 2, "AvgProportion(%)", style1)
        cur_row_index = 1
        for item in self.json_result['all']['content']:
            name, elapse, proportion = item[0], item[1], item[2]
            sheet2.write(cur_row_index, 0, name, style2)
            sheet2.write(cur_row_index, 1, elapse, style1)
            sheet2.write(cur_row_index, 2, proportion, style1)
            cur_row_index += 1
        f.save(self.input_path[0:-4] + "_hot.xls")

    def write_json(self):
        with open(self.input_path[0:-4] + "_hot.json", 'w') as f:
            json.dump(self.json_result, f)

    def run(self):
        self.read_opt_content()
        self.parse()
        self.get_preset_event_index()
        # tp90
        self.reset()
        self.get_tp90_value()
        self.get_frames(True)
        self.merge_elapse()
        tp90_stat_result = self.stat_data(True)
        # all
        self.reset()
        self.get_frames(False)
        self.merge_elapse()
        all_stat_result = self.stat_data(False)
        # json
        self.get_json(tp90_stat_result, all_stat_result)
        # write
        # self.write_table()
        self.write_json()


if __name__ == '__main__':
    xx = OptHotReport(r"D:\file_jx3\file_opt\每日性能监控\稻香村日常\20230817\1080_稻香村BD电影_8.17.opt")
    xx.run()
