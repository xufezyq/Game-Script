
import xlsxwriter
from opt_file_parser import OptFileParser


class OptDataReport(OptFileParser):

    def __init__(self, input_path, auto_filter=False):
        super(OptDataReport, self).__init__(input_path)
        self.auto_filter = auto_filter
        self.frame_index = 0
        self.all_func_avg_elapse = {}           # 所有函数的平均每帧耗时（总耗时/帧数）
        self.target_func_avg_elapse = {}        # 目标函数的平均每帧耗时（总耗时/帧数）
        self.target_func_elapse_in_frames = {}  # 目标函数的每帧总耗时
        self.target_funcs = {
            'CPU Frame': '帧耗时',
            'KEventQueueMgr::HandleEventQueue': '处理表现逻辑事件',
            'KGameWorldHandler::UpdateBackend': '更新世界的后台数据',
            'UI::AsyncTask::FetchResult': '处理异步任务',
            'KG3D_Engine::FrameMove': 'KG3D_Engine',
            'KG3D_ASyncHLODLoader::_HandleLoadResult': '处理LOD更新',
            'KG3D_SceneObjectContainer::Update': '物件更新',
            'KG3D_FlexibleBodyScene::FetchResult': '柔体更新',
            'KG3D_SceneView::_UpdateVisibleList': '可见性',
            'KG3D_SceneView::_UpdateCommonRenderData_Optimise': 'RenderData',
            'KG3D_SceneView::_Render_SunCamera_VisibleObject_To_ShadowTexture_CSMVer2': '阴影',
            'KG3D_SceneView::RenderGBuffers': 'GBuffer',
            'KG3D_SceneView::RenderOITTransparent': 'OIT',
            'KG3D_SceneView::_Render_MainCamera_OITOpaqueObject': 'OIT',
            'KG3D_SceneView::renderMainCamera_BlendObject': 'Blend',
            'KG3D_SceneView::renderMainCamera_Cloaking': 'Cloak',
            'KG3D_SceneView::renderMainCamera_ParticleSystem': '粒子系统',
            'KG3D_SceneView::renderMainCamera_PSSShakeWaveTexture': 'PSS',
            'KG3D_2DScene::Render': '2D渲染',
            'KG3D_Window::Present': 'present',
        }
        self.target_funcs_detail = {
            'CPU Frame': '帧耗时',
            'KJX3RenderModule::BackgroundUpdate': 'CPU渲染',
            'KJX3RenderModule::BackgroundPresent': 'GPU渲染',
        }

    # Override: get the data for xlsx report need
    def read_events(self):
        """ DataResponse::EventFrame = 1 """
        if 1 != self.read_data_response(False)[2]:
            return
        self.record(f"{'-' * 5} DumpEvents {'-' * 5}")
        size = self.read_data_response()[1]
        # begin
        begin_pointer = self.pointer
        # ScopeData.header
        board_number = self.read_uint32()
        thread_number = self.read_uint32()
        fiber_number = self.read_uint32()
        event_time_begin = self.read_uint64()
        event_time_end = self.read_uint64()
        frame_type = self.read_uint32()
        # ScopeData.categories
        categories = []
        categories_count = self.read_uint32()
        for i in range(categories_count):
            categories.append(self.read_event_data())
        # ScopeData.events
        events = []
        events_count = self.read_uint32()
        for i in range(events_count):
            events.append(self.read_event_data())
        # end
        self.check_end(begin_pointer, size)
        # print
        self.record(f"boardNumber={board_number} threadNumber={thread_number} fiberNumber={fiber_number:0X} frameType={frame_type:0X}")
        self.record(f"event_time = [{event_time_begin}, {event_time_end}]")
        self.record(f"categories_count = {categories_count}")
        self.record(f"events_count = {events_count}")
        self.record(">>>  time_start   time_finish   desc_index")
        # if this event belongs to main thread, then record it
        if self.threads[thread_number] != self.main_thread_id:
            return
        temp = []
        self.frame_index += 1
        for i in range(events_count):
            events[i][2] = self.event_descs[events[i][2]].split('(')[0]  # 将event_desc的索引转换为字符串描述
            self.record(f"[{i}] {events[i][0]} {events[i][1]} {events[i][2]}")
            temp.append([events[i][0], events[i][1], events[i][2]])
            # add
            self.get_target_func_single_elapse(events[i])
            self.get_all_func_single_elapse(events[i])
            self.get_target_func_single_elapse_in_frames(events[i], self.frame_index)
        self.frame_events.append(temp)

    def get_all_func_single_elapse(self, event):
        event_start, event_end, event_desc = event
        event_elapse = int(event_end - event_start)
        if event_desc not in self.all_func_avg_elapse:
            self.all_func_avg_elapse[event_desc] = {
                'AvgFunctionTime': 0,
                'FunctionTime': [event_elapse, ]
            }
        else:
            self.all_func_avg_elapse[event_desc]['FunctionTime'].append(event_elapse)

    def get_target_func_single_elapse(self, event):
        event_start, event_end, event_desc = event
        if event_desc not in self.target_funcs:
            return
        event_elapse = int(event_end - event_start)
        if event_desc not in self.target_func_avg_elapse:
            self.target_func_avg_elapse[event_desc] = {
                'AvgFunctionTime': 0,
                'FunctionTime': [event_elapse, ]
            }
        else:
            self.target_func_avg_elapse[event_desc]['FunctionTime'].append(event_elapse)

    def get_target_func_single_elapse_in_frames(self, event, frame_index):
        event_start, event_end, event_desc = event
        if event_desc not in self.target_funcs_detail:
            return
        event_elapse = int(event_end - event_start)
        if event_desc not in self.target_func_elapse_in_frames:
            self.target_func_elapse_in_frames[event_desc] = {}
            self.target_func_elapse_in_frames[event_desc][frame_index] = event_elapse
        else:
            if frame_index not in self.target_func_elapse_in_frames[event_desc]:
                self.target_func_elapse_in_frames[event_desc][frame_index] = event_elapse
            else:
                self.target_func_elapse_in_frames[event_desc][frame_index] += event_elapse

    def get_all_func_avg_elapse(self):
        self.all_func_avg_elapse['FunctionTable'] = []
        print(self.all_func_avg_elapse)
        for key in self.all_func_avg_elapse.keys():
            if key == 'FunctionTable':
                continue
            total_func_time = sum(self.all_func_avg_elapse[key]['FunctionTime'])
            avg_func_time = round(total_func_time / self.cpu_frame_count / 10000, 3)
            self.all_func_avg_elapse[key]['AvgFunctionTime'] = avg_func_time
            self.all_func_avg_elapse['FunctionTable'].append([key, avg_func_time])

    def get_target_func_avg_elapse(self):
        self.target_func_avg_elapse['FunctionTable'] = []
        for key in self.target_func_avg_elapse.keys():
            if key == 'FunctionTable':
                continue
            total_func_time = sum(self.target_func_avg_elapse[key]['FunctionTime'])
            avg_func_time = round(total_func_time / self.cpu_frame_count / 10000, 3)
            self.target_func_avg_elapse[key]['AvgFunctionTime'] = avg_func_time
            self.target_func_avg_elapse['FunctionTable'].append([self.target_funcs[key], key, avg_func_time])

    def get_target_func_frame_elapse(self):
        for event_desc in self.target_func_elapse_in_frames.keys():
            if 'FunctionTable' not in self.target_func_elapse_in_frames[event_desc]:
                self.target_func_elapse_in_frames[event_desc]['FunctionTable'] = []
            for key, value in self.target_func_elapse_in_frames[event_desc].items():
                if key == 'FunctionTable':
                    continue
                self.target_func_elapse_in_frames[event_desc]['FunctionTable'].append([key, round(value / 10000, 3)])

    def write_all_func_avg_elapse(self, workbook, auto_filter=False):
        worksheet = workbook.add_worksheet('All')
        self.get_all_func_avg_elapse()
        cell_range = 'A%d:B%d' % (1, len(self.all_func_avg_elapse['FunctionTable']) + 1)
        data_format = {'data': self.all_func_avg_elapse['FunctionTable'],
                      'columns': [{'header': '函数'},
                                  {'header': '耗时(ms)'},
                                  ],
                      'autofilter': auto_filter}
        worksheet.add_table(cell_range, data_format)

    def write_target_func_avg_elapse(self, workbook, auto_filter=False):
        worksheet = workbook.add_worksheet('Target')
        self.get_target_func_avg_elapse()
        cell_range = 'A%d:C%d' % (1, len(self.target_func_avg_elapse['FunctionTable']) + 1)
        data_format = {'data': self.target_func_avg_elapse['FunctionTable'],
                      'columns': [{'header': '模块'},
                                  {'header': '函数'},
                                  {'header': '耗时(ms)'},
                                  ],
                      'autofilter': auto_filter}
        worksheet.add_table(cell_range, data_format)

    def write_target_func_frame_elapse(self, workbook, auto_filter=False):
        self.get_target_func_frame_elapse()
        for key in self.target_func_elapse_in_frames.keys():
            value = self.target_func_elapse_in_frames[key]
            cell_range = 'A%d:B%d' % (1, len(value['FunctionTable']) + 1)
            data_format = {'data': value['FunctionTable'],
                          'columns': [{'header': '帧数'},
                                      {'header': '耗时(ms)'},
                                      ],
                          'autofilter': auto_filter}
            worksheet = workbook.add_worksheet(self.target_funcs_detail[key])
            worksheet.add_table(cell_range, data_format)

    def write_func_elapse(self):
        workbook = xlsxwriter.Workbook(self.input_path[0:-3] + "xlsx")
        self.write_target_func_avg_elapse(workbook, self.auto_filter)
        self.write_all_func_avg_elapse(workbook, self.auto_filter)
        self.write_target_func_frame_elapse(workbook, self.auto_filter)
        workbook.close()

    def run(self):
        self.read_opt_content()
        self.parse()
        self.write_func_elapse()


if __name__ == '__main__':
    xx = OptDataReport(r"D:\opt_file\9.opt", True)
    xx.run()
