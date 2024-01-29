# 解析.opt文件
# 解析结果记录至.json文件
# 解析日志记录至.log文件
# 可供后续程序进行进一步解析


import os
import sys
import json
import time
import struct
import numpy as np
import util
from opt_frame_build import OptickFrameBuilder
from ubox_frame_build import SpeedScopeFrameBuilder
from concurrent.futures import ThreadPoolExecutor

# 参考链接
# https://www.delftstack.com/zh/howto/python/read-binary-files-in-python/

UINT8_LENGTH = 1
UINT16_LENGTH = 2
UINT32_LENGTH = 4
UINT64_LENGTH = 8
FLOAT_LENGTH = 4
DATA_RESPONSE_LEN = 12


class OptFileParser(object):

    def __init__(self, input_path):
        self.input_path = input_path
        self.input_dir = self.input_path[:self.input_path.rindex(os.sep)]
        self.output_path = input_path[0:-3] + "log"
        self.recorder = open(self.output_path, 'w')
        self.data = None  # 读取的opt文件内容
        self.data_len = 0  # opt数据总大小
        self.pointer = 0  # 当前数据偏移
        # data about opt
        self.main_thread_id = 0  # 主线程id
        self.cpu_frame_count = 0  # CPU帧数
        self.cpu_frames_time_ms = []  # CPU帧的耗时，注意最后一帧耗时为0
        self.max_cpu_frame_time = 0  # CPU帧耗时最多的数值
        self.min_cpu_frame_time = 0  # CPU帧耗时最少的数值
        self.avg_cpu_frame_time = 0  # CPU帧耗时的平均值
        self.summary = {}  # 概要：Platform,CPU,GPU...
        self.attachments = []  # 附加数据
        self.threads = []  # thread_id list
        self.fibers = []  # fiber_id list, not used
        self.event_descs = []  # 事件的文字描述：name(file,line)
        self.cpu_frames = []  # CPU帧的数据：time_start, time_finish, desc_index, thread_id
        self.gpu_frames = []  # not used
        self.render_frames = []  # not used
        self.frame_events = []  # 主线程的CPU帧的事件数据：time_start, time_finish, desc_index|desc
        self.speedscope_json = None
        self.executor = ThreadPoolExecutor(max_workers=5)

    def __del__(self):
        if self.recorder:
            self.recorder.close()
        self.executor.shutdown(wait=True)

    def record(self, data):
        self.recorder.write(data)
        self.recorder.write('\n')

    def read_opt_content(self):
        # Method 1
        with open(self.input_path, "rb") as f:
            self.data = f.read()
            self.data_len = len(self.data)
            self.record(f"[DEBUG] data len = {self.data_len}")
        # Method 2
        # self.data = Path(input_path).read_bytes()

    def read_uint8(self):
        result = struct.unpack("B", self.data[self.pointer: self.pointer + UINT8_LENGTH])
        self.pointer += UINT8_LENGTH
        return result[0]

    def read_uint16(self):
        result = struct.unpack("H", self.data[self.pointer: self.pointer + UINT16_LENGTH])
        self.pointer += UINT16_LENGTH
        return result[0]

    def read_uint32(self):
        result = struct.unpack("I", self.data[self.pointer: self.pointer + UINT32_LENGTH])
        self.pointer += UINT32_LENGTH
        return result[0]

    def read_uint64(self):
        result = struct.unpack("Q", self.data[self.pointer: self.pointer + UINT64_LENGTH])
        self.pointer += UINT64_LENGTH
        return result[0]

    def read_float(self):
        result = struct.unpack("f", self.data[self.pointer: self.pointer + FLOAT_LENGTH])
        self.pointer += FLOAT_LENGTH
        return result[0]

    def read_string(self):
        str_len = self.read_uint32()
        if str_len <= 0:
            return
        bytes = struct.unpack("c" * str_len, self.data[self.pointer: self.pointer + str_len])
        self.pointer += str_len
        str_index = 0
        str_data = []
        while str_index < str_len:
            try:
                b = bytes[str_index]
                c = b.decode("utf-8")
                str_index = str_index + 1
            except:
                b = bytes[str_index] + bytes[str_index + 1]
                c = b.decode("gbk")
                str_index = str_index + 2
            str_data.append(c)
        result = ''.join(str_data)
        return result

    # -----------------------------------------------------------------------------------------------------------------

    def read_data_response(self, offset=True):
        """ 读取数据响应头(version,size,type,application)，offset标识是否执行指针偏移 """
        try:
            data_response = struct.unpack("IIHH", self.data[self.pointer:self.pointer + DATA_RESPONSE_LEN])
        except:
            return [0, 0, -1, 0]
        (v, s, t, a) = data_response
        if offset:
            self.pointer += DATA_RESPONSE_LEN
            self.record(f"[DataResponse] type={t} size={s} version={v} application={a:0X}")
        return data_response

    def read_event_desc(self):
        """ event_desc = (name, file, line, filter, color, flags) """
        name = self.read_string()
        file = self.read_string()
        line = self.read_uint32()
        filter = self.read_uint32()
        color = self.read_uint32()
        _ = self.read_float()  # 0.0f
        flags = self.read_uint8()
        event_desc = (name, file, line, filter, color, flags)
        return event_desc

    def read_process_desc(self):
        """ process_desc = (process_id, name, unique_key) """
        process_id = self.read_uint32()
        name = self.read_string()
        unique_key = self.read_uint64()
        process_desc = (process_id, name, unique_key)
        return process_desc

    def read_thread_desc(self):
        """ thread_desc = (thread_id, process_id, name, max_depth, priority, mask) """
        thread_id = self.read_uint64()
        process_id = self.read_uint32()
        name = self.read_string()
        max_depth = self.read_uint32()
        priority = self.read_uint32()
        mask = self.read_uint32()
        thread_desc = (thread_id, process_id, name, max_depth, priority, mask)
        return thread_desc

    def read_fiber_desc(self):
        """ fiber_desc = (id,) """
        id = self.read_uint64()
        fiber_desc = (id,)
        return fiber_desc

    def read_event_data(self):
        """ event_data = [time_start, time_finish, desc_index] """
        time_start = self.read_uint64()
        time_finish = self.read_uint64()
        desc_index = self.read_uint32()  # ob.description ? ob.description->index : (uint32)-1
        event_data = [time_start, time_finish, desc_index]
        return event_data

    def read_frame_data(self):
        """ frame_data = [time_start, time_finish, desc_index, thread_id] """
        event_data = self.read_event_data()
        thread_id = self.read_uint64()
        frame_data = event_data + [thread_id]
        return frame_data

    def read_fiber_sync_data(self):
        """ fiber_sync_data = [time_start, time_end, thread_id] """
        time_start = self.read_uint64()
        time_end = self.read_uint64()
        thread_id = self.read_uint64()
        fiber_sync_data = [time_start, time_end, thread_id]
        return fiber_sync_data

    def read_sys_call_data(self):
        """ sys_call_data = [time_start, time_finish, desc_index, thread_id, id] """
        event_data = self.read_event_data()
        thread_id = self.read_uint64()
        id = self.read_uint64()
        sys_call_data = event_data + [thread_id, id]
        return sys_call_data

    def read_switch_context_desc(self):
        """ desc = [timestamp, old_tid, new_tid, cpu_id, reason] """
        timestamp = self.read_uint64()
        old_tid = self.read_uint64()
        new_tid = self.read_uint64()
        cpu_id = self.read_uint8()
        reason = self.read_uint8()
        desc = [timestamp, old_tid, new_tid, cpu_id, reason]
        return desc

    def read_module(self):
        """ module = [path, address, size] """
        path = self.read_string()
        address = self.read_uint64()
        size = self.read_uint64()
        return [path, address, size]

    def read_symbol(self):
        """ symbol = [address, function, file, line] """
        address = self.read_uint64()
        function = self.read_string()
        file = self.read_string()
        line = self.read_uint32()
        return [address, function, file, line]

    def check_end(self, start_pointer, size):
        """ 检查每一段数据是否正确读取 """
        end_pointer = self.pointer
        if size == (end_pointer - start_pointer):
            pass
        else:
            self.record("read fail")

    # -------------------------------------------------------------------------------------------------

    def read_start(self):
        """ 读取opt文件开头 """
        self.record(f"{'-' * 15} Start {'-' * 15}")
        # magic = self.read_uint32()
        # version = self.read_uint16()
        # flags = self.read_uint16()
        # self.record(f"magic={magic:0X} version={version} flags={flags}")
        self.pointer += 8

    def read_progress(self):
        """ DataResponse::ReportProgress = 4 """
        self.record(f"{'-' * 15} report progress {'-' * 15}")
        size = self.read_data_response()[1]
        # self.pointer += size
        # begin
        begin_pointer = self.pointer
        # message
        message = self.read_string()
        # end
        self.check_end(begin_pointer, size)
        # print
        self.record(f"Report Progress = {message}")

    def read_summary(self):
        """ DataResponse::SummaryPack = 258 """
        self.record(f"{'-' * 15} Summary {'-' * 15}")
        size = self.read_data_response()[1]
        # begin
        begin_pointer = self.pointer
        # Board Number
        board_number = self.read_uint32()
        # Frames
        cpu_frames_count = self.read_uint32()
        # self.cpu_frame_count = cpu_frames_count
        for i in range(cpu_frames_count):
            self.cpu_frames_time_ms.append(self.read_float())
            self.record(f"frames time[{i}]: {self.cpu_frames_time_ms[i]}")
        # Summary
        summary_count = self.read_uint32()
        for i in range(summary_count):
            summary_key = self.read_string()
            summary_value = self.read_string()
            self.summary[summary_key] = summary_value
        # Attachments (Not Used Now)
        attachment_count = self.read_uint32()
        for i in range(attachment_count):
            att_type = self.read_uint32()
            att_name = self.read_string()
            att_data = []
            att_data_count = self.read_uint32()
            for j in range(att_data_count):
                att_data.append(self.read_uint8())
            self.attachments.append((att_type, att_name, att_data))
        # end
        self.check_end(begin_pointer, size)
        # print
        self.record(f"Board Number = {board_number}")
        self.record(f"CPU frames count = {cpu_frames_count}")
        self.record(f"Summary count = {summary_count}")
        for k in self.summary.keys():
            self.record(f"{k} = {self.summary[k]}")
        self.record(f"Attachment count = {attachment_count}")

    def read_board(self):
        """ DataResponse::FrameDescriptionBoard = 0 """
        self.record(f"{'-' * 15} Board {'-' * 15}")
        size = self.read_data_response()[1]
        # begin
        begin_pointer = self.pointer
        board_number = self.read_uint32()
        self.record(f"board number = {board_number}")
        platform_frequency = self.read_uint64()
        self.record(f"platform_frequency = {platform_frequency}")
        origin = self.read_uint64()  # 0
        precision = self.read_uint32()  # 0
        time_slice_begin = self.read_uint64()
        self.record(f"time_slice_begin = {time_slice_begin}")
        time_slice_end = self.read_uint64()
        self.record(f"time_slice_end = {time_slice_end}")
        # self.pointer += 40
        threads_count = self.read_uint32()
        for i in range(threads_count):
            thread_desc = self.read_thread_desc()
            self.threads.append(thread_desc[0])
            self.record(f"thread desc[{i}: {thread_desc}]")
        fibers_count = self.read_uint32()
        for i in range(fibers_count):
            fid = self.read_fiber_desc()[0]
            self.fibers.append(fid)
        forced_main_thread_index = self.read_uint32()
        event_descs_count = self.read_uint32()
        for i in range(event_descs_count):
            temp = self.read_event_desc()
            self.event_descs.append(f"{temp[0]}")  # 只有函数名
            self.record(f"event desc[{i}]: {temp}")
        # _ = self.read_uint32()      # 0
        # _ = self.read_uint32()      # 0
        # _ = self.read_uint32()      # 0
        # _ = self.read_uint32()      # 0
        # mode = self.read_uint32()
        self.pointer += 20
        process_descs = []
        process_descs_count = self.read_uint32()
        for i in range(process_descs_count):
            process_descs.append(self.read_process_desc())
        thread_descs = []
        threads_descs_count = self.read_uint32()
        for i in range(threads_descs_count):
            thread_descs.append(self.read_thread_desc())
        # process_id = self.read_uint32()
        # hardware_concurrency = self.read_uint32()
        self.pointer += 8
        # end
        self.check_end(begin_pointer, size)
        # print
        self.record(f"thread count = {threads_count}")
        self.record(f"fiber_count = {fibers_count}")
        self.record(f"forcedMainThreadIndex = {forced_main_thread_index:0X}")
        self.record(f"Event Desc ({event_descs_count})")
        self.record(f"processDescs count = {process_descs_count}")
        self.record(f"threadDescs count = {threads_descs_count}")

    def read_frames(self):
        """ DataResponse::FramesPack = 259 """
        self.record(f"{'-' * 15} Serializing Frames {'-' * 15}")
        size = self.read_data_response()[1]
        # begin
        begin_pointer = self.pointer
        # board_number = self.read_uint32()
        self.pointer += 4
        # 各种类型的帧数据
        frames_types = self.read_uint32()
        for i in range(frames_types):  # "CPU", "GPU", "Render"
            frame_size = self.read_uint32()
            if i == 0:
                for j in range(frame_size):
                    self.cpu_frames.append(self.read_frame_data())
                    self.record(f"cpu frames[{j}]: {self.cpu_frames[j]}")
                # 这里我们假设所有CPU帧所属的线程都是一致的
                self.main_thread_id = self.cpu_frames[0][3]
            elif i == 1 or i == 2:
                self.pointer += (frame_size * 28)
            else:
                print(f"[ERROR] Unknown Frame Type {i}")
        # end
        self.check_end(begin_pointer, size)
        # print
        self.record(f"main thread id = {self.main_thread_id}")
        self.record(f"CPU Frames count = {len(self.cpu_frames)}")
        self.record(f"GPU Frames count = {len(self.gpu_frames)}")
        self.record(f"Render Frames count = {len(self.render_frames)}")

    def read_GPU_dump(self):
        pass

    def read_thread_and_fiber(self):
        """ 因为threads和fibers数据很难从头部区分，都是DumpEvnets，所以这里统一处理  """
        self.record(f"{'-' * 15} Serializing Threads & Fibers {'-' * 15}")
        index = 0
        while 1 == self.read_data_response(False)[2]:  # type == DataResponse::EventFrame
            index += 1
            self.read_events()
            self.read_tags()
            self.read_fiber_sync_buffer()

    def read_events(self):
        """ DataResponse::EventFrame = 1 (For Thread and Fiber)"""
        if 1 != self.read_data_response(False)[2]:
            return
        size = self.read_data_response()[1]
        # begin
        begin_pointer = self.pointer
        # ScopeData.header
        board_number = self.read_uint32()
        self.record(f"board number: {board_number}")
        # self.pointer += 4
        thread_number = self.read_uint32()
        fiber_number = self.read_uint32()
        event_time_begin = self.read_uint64()
        event_time_end = self.read_uint64()
        frame_type = self.read_uint32()
        self.record(
            f"thread_number={thread_number},fiber_number={fiber_number},event_time_begin={event_time_begin},event_time_end={event_time_end},frame_type={frame_type}")
        self.record(f"timescope = {round((event_time_end - event_time_begin) / 10000, 3)}")
        # self.pointer += 24
        # ScopeData.categories
        categories_count = self.read_uint32()
        # self.pointer += (categories_count * 20)
        categories = []
        for i in range(categories_count):
            categories.append(self.read_event_data())
            self.record(f"categories[{i}]: {categories[i]}")
        # ScopeData.events
        temp = []
        flag = (self.threads[thread_number] == self.main_thread_id)
        events_count = self.read_uint32()
        for i in range(events_count):
            event = self.read_event_data()
            self.record(f"event[{i}]: {event}")
            # if this scope belongs to main thread, then record it
            if flag:
                temp.append(event)
        if temp:
            self.frame_events.append(temp)
        # end
        self.check_end(begin_pointer, size)

    def read_tags(self):
        """ DataResponse::TagsPack = 8 (For Thread Only)"""
        if 8 != self.read_data_response(False)[2]:
            return
        size = self.read_data_response()[1]
        # self.pointer += size
        self.record(f"{'-' * 5} Tags {'-' * 5}")
        # begin
        begin_pointer = self.pointer
        # ScopeData.header
        board_number = self.read_uint32()
        thread_number = self.read_uint32()
        self.record(f"boardNumber = {board_number} threadNumber = {thread_number}")
        # 固定数值 0
        _ = self.read_uint32()
        # Float Buffer
        float_buffer = []
        float_buffer_size = self.read_uint32()
        for i in range(float_buffer_size):
            timestamp = self.read_uint64()
            desc_index = self.read_uint32()
            data = self.read_float()
            float_buffer.append((timestamp, desc_index, data))
        self.record(f"FloatBuffer[{float_buffer_size}]")
        # UInt32 Buffer
        uint32_buffer = []
        uint32_buffer_size = self.read_uint32()
        for i in range(uint32_buffer_size):
            timestamp = self.read_uint64()
            desc_index = self.read_uint32()
            data = self.read_uint32()
            uint32_buffer.append((timestamp, desc_index, data))
        self.record(f"U32Buffer[{uint32_buffer_size}]")
        # SInt32 Buffer
        sint32_buffer = []
        sint32_buffer_size = self.read_uint32()
        for i in range(sint32_buffer_size):
            timestamp = self.read_uint64()
            desc_index = self.read_uint32()
            data = self.read_uint32()
            sint32_buffer.append((timestamp, desc_index, data))
        self.record(f"S32Buffer[{sint32_buffer_size}]")
        # UInt64 Buffer
        uint64_buffer = []
        uint64_buffer_size = self.read_uint32()
        for i in range(uint64_buffer_size):
            timestamp = self.read_uint64()
            desc_index = self.read_uint32()
            data = self.read_uint64()
            uint64_buffer.append((timestamp, desc_index, data))
        self.record(f"U64Buffer[{uint64_buffer_size}]")
        # Point Buffer
        point_buffer = []
        point_buffer_size = self.read_uint32()
        for i in range(point_buffer_size):
            timestamp = self.read_uint64()
            desc_index = self.read_uint32()
            x = self.read_float()
            y = self.read_float()
            z = self.read_float()
            data = (x, y, z)
            point_buffer.append((timestamp, desc_index, data))
        self.record(f"PointBuffer[{point_buffer_size}]")
        # 固定数值 0
        _ = self.read_uint32()
        _ = self.read_uint32()
        # String Buffer
        string_buffer = []
        string_buffer_size = self.read_uint32()
        for i in range(string_buffer_size):
            timestamp = self.read_uint64()
            desc_index = self.read_uint32()
            data = self.read_string()
            string_buffer.append((timestamp, desc_index, data))
        self.record(f"StringBuffer[{string_buffer_size}]")
        # end
        self.check_end(begin_pointer, size)
        # print
        index = 0
        for i in float_buffer:
            self.record(f"float[{index}] = {i[0]} | {i[1]} | {i[2]}")
            index += 1
        index = 0
        for i in uint32_buffer:
            self.record(f"uint32[{index}] = {i[0]} | {i[1]} | {i[2]}")
            index += 1
        index = 0
        for i in sint32_buffer:
            self.record(f"sint32[{index}] = {i[0]} | {i[1]} | {i[2]}")
            index += 1
        index = 0
        for i in uint64_buffer:
            self.record(f"uint64[{index}] = {i[0]} | {i[1]} | {i[2]}")
            index += 1
        index = 0
        for i in point_buffer:
            self.record(f"point[{index}] = {i[0]} | {i[1]} | {i[2]}")
            index += 1
        index = 0
        for i in string_buffer:
            self.record(f"string[{index}] = {i[0]} | {i[1]} | {i[2]}")
            index += 1

    def read_fiber_sync_buffer(self):
        """ DataResponse::FiberSynchronizationData = 256 (For Fiber Only)"""
        if 256 != self.read_data_response(False)[2]:
            return
        size = self.read_data_response()[1]
        self.pointer += size
        # self.record(f"{'-' * 5} FiberSynchronizationData {'-' * 5}")
        # # begin
        # begin_pointer = self.pointer
        # # ScopeData.header
        # board_number = self.read_uint32()
        # fiber_number = self.read_uint32()
        # # data
        # fiber_sync_buffer = []
        # fiber_sync_buffer_size = self.read_uint32()
        # for i in range(fiber_sync_buffer_size):
        #     fiber_sync_buffer.append(self.read_fiber_sync_data())
        # # end
        # self.check_end(begin_pointer, size)
        # # print
        # self.record(f"fiber_sync_buffer_size = {fiber_sync_buffer_size}")

    def read_switch_contexts(self):
        """ DataResponse::SynchronizationData = 7 """
        size = self.read_data_response()[1]
        self.pointer += size
        # self.record(f"{'-' * 15} SwitchContexts {'-' * 15}")
        # # begin
        # begin_pointer = self.pointer
        # # Board Number
        # board_number = self.read_uint32()
        # # Switch Context
        # switch_context = []
        # switch_context_size = self.read_uint32()
        # for i in range(switch_context_size):
        #     switch_context.append(self.read_switch_context_desc())
        # # end
        # self.check_end(begin_pointer, size)
        # # print
        # self.record(f"boardNumber = {board_number} switch_context count = {switch_context_size}")

    def read_syscalls(self):
        """ DataResponse::SyscallPack = 257 """
        size = self.read_data_response()[1]
        self.pointer += size
        # self.record(f"{'-' * 15} SysCalls {'-' * 15}")
        # # begin
        # begin_pointer = self.pointer
        # # Board Number
        # board_number = self.read_uint32()
        # # Sys Calls
        # sys_call = []
        # sys_call_size = self.read_uint32()
        # for i in range(sys_call_size):
        #     sys_call.append(self.read_sys_call_data())
        # # end
        # self.check_end(begin_pointer, size)
        # # print
        # self.record(f"boardNumber = {board_number}  sys_call count = {sys_call_size}")

    def read_modules_and_symbols(self):
        """ DataResponse::CallstackDescriptionBoard = 9 """
        size = self.read_data_response()[1]
        self.pointer += size
        # self.record(f"{'-' * 15} Modules and Symbols {'-' * 15}")
        # # begin
        # begin_pointer = self.pointer
        # # Board Number
        # board_number = self.read_uint32()
        # # modules
        # modules = []
        # module_count = self.read_uint32()
        # for i in range(module_count):
        #     modules.append(self.read_module())
        # # symbols
        # symbols = []
        # symbol_count = self.read_uint32()
        # for i in range(symbol_count):
        #     symbols.append(self.read_symbol())
        # # end
        # self.check_end(begin_pointer, size)
        # # print
        # self.record(f"boardNumber = {board_number}  module_count = {module_count} symbol_count = {symbol_count}")

    def read_callstacks(self):
        """ DataResponse::CallstackPack = 10 """
        size = self.read_data_response()[1]
        self.pointer += size
        # self.record(f"{'-' * 15} Callstacks {'-' * 15}")
        # # begin
        # begin_pointer = self.pointer
        # # Board Number
        # board_number = self.read_uint32()
        # # callstacks
        # callstacks = []
        # callstack_count = self.read_uint32()
        # for i in range(callstack_count):
        #     callstacks.append(self.read_uint64())
        # # end
        # self.check_end(begin_pointer, size)
        # # print
        # self.record(f"boardNumber = {board_number}  callstack_count = {callstack_count}")

    def read_opt_filename(self):
        """ DataResponse::OptFilePath = 260 """
        self.record(f"{'-' * 15} Filename {'-' * 15}")
        size = self.read_data_response()[1]
        # begin
        begin_pointer = self.pointer
        # data
        filename = self.read_string()
        # end
        self.check_end(begin_pointer, size)
        # print
        self.record(f"filename={filename}")

    def read_finish(self):
        """ DataResponse::NullFrame = 3 """
        self.record(f"{'-' * 15} Finish {'-' * 15}")
        self.read_data_response()
        self.record(f"End Address = {self.pointer}")

    def parse(self):
        self.read_start()
        while self.pointer < self.data_len:
            t = self.read_data_response(False)[2]
            if t == 258:
                self.read_summary()
            elif t == 0:
                self.read_board()
            elif t == 259:
                self.read_frames()
            elif t == 1:
                self.read_thread_and_fiber()
            elif t == 7:
                self.read_switch_contexts()
            elif t == 257:
                self.read_syscalls()
            elif t == 9:
                self.read_modules_and_symbols()
            elif t == 10:
                self.read_callstacks()
            elif t == 260:
                self.read_opt_filename()
            elif t == 3:
                self.read_finish()
            elif t == 4:
                self.read_progress()
            elif t == 8:
                self.read_tags()
            else:
                self.record(f"Unexcepted Type = {t}")
                break
        self.recorder.flush()
        self.recorder.close()
        self.recorder = None
        # 最后一帧无用
        self.cpu_frames_time_ms = self.cpu_frames_time_ms[:-1]
        self.cpu_frames = self.cpu_frames[:-1]
        self.cpu_frame_count = len(self.cpu_frames)
        self.avg_cpu_frame_time = round(np.mean(self.cpu_frames_time_ms), 3)  # 平均值
        self.max_cpu_frame_time = round(np.max(self.cpu_frames_time_ms), 3)  # 最大值
        self.min_cpu_frame_time = round(np.min(self.cpu_frames_time_ms), 3)  # 最小值

    def output_in_json(self):
        # 火焰图-分析每一帧
        # handled_frame_events = []
        # for frame_event in self.frame_events:
        #    builder = OptickFrameBuilder(frame_event)
        #    handled_frame_events.append(builder.run())
        # 写json文件
        json_file = self.output_path[:-3] + "json"
        json_data = {
            'summary': self.summary,
            'cpu_frames_count': self.cpu_frame_count,
            'cpu_frames_time_ms': self.cpu_frames_time_ms,
            'avg_cpu_frames_time': self.avg_cpu_frame_time,
            'max_cpu_frames_time': self.max_cpu_frame_time,
            'min_cpu_frames_time': self.min_cpu_frame_time,
            'cpu_frames': self.cpu_frames,
            'event_desc': self.event_descs,
            # 'frame_events': self.frame_events
        }
        with open(json_file, 'w') as f:
            json.dump(json_data, f)
        # 将每一帧的事件堆栈单独写入Json文件
        cut_index = self.output_path.rindex(os.sep)
        dir_path = f"{self.output_path[:cut_index]}{os.sep}frame_events"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        for frame_index in range(self.cpu_frame_count):
            json_data = {
                'data': self.frame_events[frame_index]
            }
            json_file = f"{dir_path}{os.sep}{frame_index}.json"
            with open(json_file, 'w') as f:
                json.dump(json_data, f)

    def pre_run_speed_scope_task(self):
        self.speedscope_json = {
            "activeProfileIndex": 0,
            'shared': {
                'frames': []
            },
            'profiles': [],
            "$schema": "https://www.speedscope.app/file-format-schema.json"
        }
        for desc in self.event_descs:
            self.speedscope_json['shared']['frames'].append(
                {"name": desc}
            )
        file = f"{self.input_dir}{os.sep}speedscope.json"
        with open(file, 'w') as f:
            json.dump(self.speedscope_json, f)
        dir_path = f"{self.input_dir}{os.sep}frame_graph"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def run_speed_scope_task(self, frame_index):
        frame = self.frame_events[frame_index]
        builder = SpeedScopeFrameBuilder(frame)
        self.speedscope_json['profiles'] = [builder.run()]
        json_file = f"{self.input_dir}{os.sep}frame_graph{os.sep}{frame_index}.json"
        with open(json_file, 'w') as f:
            json.dump(self.speedscope_json, f)

    def output_in_ubox_json(self):
        self.pre_run_speed_scope_task()
        frame_count = len(self.frame_events)
        all_task = [self.executor.submit(self.run_speed_scope_task, i, dir_path) for i in range(frame_count)]

    def run(self):
        self.read_opt_content()
        self.parse()
        self.output_in_json()
        self.pre_run_speed_scope_task()
        # self.output_in_ubox_json()


def Parse_SpeedScope(frame_index):
    speedscope_json = {}
    file_path = r"C:\Users\shichunkang\Desktop\speedscope.json"
    with open(file_path, 'r') as f:
        speedscope_json = json.load(f)
    file_path = f"C:\\Users\\shichunkang\\Desktop\\frame_events\\{frame_index}.json"
    with open(file_path, 'r') as f:
        load_data = json.load(f)
        frame = load_data['data']
        builder = SpeedScopeFrameBuilder(frame)
        speedscope_json['profiles'] = [builder.run()]
    file_path = f"C:\\Users\\shichunkang\\Desktop\\frame_graph\\{frame_index}.json"
    with open(file_path, 'w') as f:
        json.dump(speedscope_json, f)


if __name__ == '__main__':
    util.print_cur_time()
    # x = OptFileParser(r'C:\Users\shichunkang\Desktop\test1.opt')
    # # x = OptFileParser(sys.argv[1])
    # x.run()
    Parse_SpeedScope(113)
    util.print_cur_time()
