import requests

from config import config


def send_wechat(message):
    if config.global_config.get('messenger', 'enable') != 'true':
        return

    """推送信息到微信"""
    url = 'http://sc.ftqq.com/{}.send'.format(config.global_config.get('messenger', 'sckey'))
    payload = {
        "text": '疫苗结果',
        "desp": message
    }
    headers = {
        'User-Agent': config.global_config.getConfigSection('DEFAULT_USER_AGENT')
    }
    requests.get(url, params=payload, headers=headers)
