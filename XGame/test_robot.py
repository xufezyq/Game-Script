import requests
import json

# # 要发送的数据
# data = {
#     "msgtype": "text",
#     "text": {
#         "content": "每日数据监控报告：\n今日数据统计结果请相关同事注意<at user_id=\"17856\">李三</at><at user_id=\"-1\">所有人</at>"
#     }
# }
# json_data = json.dumps(data)
#
# # 目标 URL
# url = 'https://xz.wps.cn/api/v1/webhook/send?key=7e60aa09abca467e00bcbe0f69ed861d'  # 替换为目标服务器的URL
#
# # 发起 HTTP POST 请求
# response = requests.post(url, data=json_data)
#
# # 输出响应内容
# print(response.status_code)
# print(response.json())


def request_post(url, data):
    response = requests.post(url, data=data)
    return response
