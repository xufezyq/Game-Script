import xlwt
import time

# VERT_TOP      = 0x00    上端对齐
# VERT_CENTER   = 0x01    居中对齐（垂直方向上）
# VERT_BOTTOM   = 0x02    低端对齐
# HORZ_LEFT     = 0x01    左端对齐
# HORZ_CENTER   = 0x02    居中对齐（水平方向上）
# HORZ_RIGHT    = 0x03    右端对齐


def set_style(alignment):
    style = xlwt.XFStyle()
    al = xlwt.Alignment()
    al.horz = alignment
    al.vert = 1  # 垂直方向上居中对齐
    style.alignment = al
    return style


def get_round_time(time_counter):
    """ 将高性能计数器转换为时间，并保留3位小数（四舍五入） """
    time_real = round(time_counter / 10000, 3)
    return time_real


def print_cur_time():
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
