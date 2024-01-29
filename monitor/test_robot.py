import requests


def request_post(url, data):
    response = requests.post(url, data=data)
    return response
