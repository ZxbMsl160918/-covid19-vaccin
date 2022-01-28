import json
import logging as log
import multiprocessing
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from urllib.parse import urlencode

import requests

from config import config
from constant import constant
from param import covid_req_params


def get_url(url):
    """
    拼接主机url地址
    :param url:
    :return:
    """
    return constant.URLS["hostUrl"] + "/" + url


def get_session():
    # 初始化session
    session = requests.session()
    session.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Referer': 'https://m.r.umiaohealth.com/Home/Index',
        'Cookie': config.global_config.getConfigSection("cookie"),
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
    }
    return session


def wait_some_time():
    time.sleep(random.randint(3000, 10000) / 1000)


class CovidHttpReq:
    def __init__(self):
        self.session = get_session()
        # 疫苗预约是否完成
        self.success_flag = False
        self.lock = threading.Lock()
        self.count = 0
        self.child_id = self.match_child_id()
        log.basicConfig(level=log.DEBUG,  # 控制台打印的日志级别
                        filename='./logs/error.log',
                        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')

    def change_success_flag(self, flag):
        with self.lock:
            self.success_flag = flag

    def match_child_id(self):
        req_url = get_url(constant.URLS["childId"])
        # 解析响应结果
        result = self.session.get(url=req_url)
        child_id = re.search("(?<=goEvaluation\\(')\\d+(?=',1\\))", result.text).group(0)
        if child_id is None or child_id == 0:
            raise Exception("尝试打开网页失败，请重新运行程序。")
        return child_id

    def match_user_msg(self):
        req_url = get_url(constant.URLS["userMsg"])
        # 解析响应结果
        result = self.session.get(url=req_url)
        userMsg = re.search("(?<=<div class=\"bobyname\">)\\s+(.*)\\s+<div>\\d+</div>", result.text).group(0)
        return re.sub("<(\\S*?)[^>]*>.*?|<.*? />|\\s*", "", userMsg)

    def get_vaccination_msg(self, area):
        """
        获取某个区的疫苗预约列表
        :param area:
        :return:
        """
        params = covid_req_params.get_vaccination_addr_params(area, config.global_config.getConfigSection("stitches"))
        req_url = get_url(constant.URLS["vaccinationAddress"])

        # 解析响应结果
        result = self.session.post(url=req_url, params=urlencode(params))
        try:
            json_result = json.loads(result.text)
        except Exception:
            print("请求失败，请稍后重试！错误信息：" + result.text)
        else:
            return json_result

    def get_hospital_time_range(self, institution_id, date, hospital_name):
        """
        获取某个医院可预约时间段，然后给下一步全部扫描请求预约
        :param hospital_name:
        :param institution_id: 社区医院的唯一标识
        :param date: 需要预约哪一天，格式：yyyy-MM-dd
        :return:
        """
        params = covid_req_params.get_hospital_time_range_params(self.child_id, institution_id, date)
        req_url = get_url(constant.URLS["hospitalTimeRange"])

        # 解析响应结果
        result = self.session.post(url=req_url, params=urlencode(params))
        try:
            json_result = json.loads(result.text)
        except Exception:
            print(" %s ------ 请求失败，请稍后重试！%s" % (hospital_name, result.text))
        else:
            if len(json_result) == 0:
                print(" %s ------ 可预约时段为空，重新获取..." % hospital_name)
                wait_some_time()
                self.get_hospital_time_range(institution_id, date, hospital_name)
            return json_result

    def sec_vaccination(self, date, time_frame_index, institution_id, hospital_id, hospital_name):
        """
        执行预约请求
        :param hospital_name: 医院名称
        :param date:  预约日期
        :param time_frame_index: 哪个时间段
        :param institution_id: 可从某个社区医院的响应信息获取
        :param hospital_id: 医院的 id
        :return: true 预约成功，false 预约失败
        """
        params = covid_req_params.get_sec_vaccination_params(self.child_id, date, time_frame_index, institution_id,
                                                             hospital_id,
                                                             config.global_config.getConfigSection("stitches"))
        req_url = get_url(constant.URLS["secVaccination"])
        # 解析响应结果
        result = self.session.get(url=req_url, params=urlencode(params))
        try:
            json_result = json.loads(result.text)
        except Exception:
            print(" %s ------ 请求失败，请稍后重试！%s" % (hospital_name, result.text))
        else:
            if not json_result["bSucceed"]:
                # 失败可能因为已经预约成功了
                if "您有未完成的预约" in json_result["sMsg"]:
                    self.change_success_flag(True)
                    return True
                print(" %s ------ 预约失败，失败原因：%s" % (hospital_name, json_result["sMsg"]))
            self.change_success_flag(json_result["bSucceed"])

    def sec_vaccination_by_time_ranges(self, time_ranges, date, institution_id, hospital_id, hospital_name):
        """
        遍历日期进行预约
        :param hospital_name:
        :param date:  预约日期
        :param time_ranges 可预约时段
        :param institution_id: 可从某个社区医院的响应信息获取
        :param hospital_id: 医院的 id
        """
        # 优先抢最后的时段
        for time_index in time_ranges[::-1]:
            self.count = self.count + 1
            print(" %s ------ 第 %d 次预约尝试...尝试预约时段：%s %s" % (hospital_name, self.count, date, time_index['timestr']))
            self.sec_vaccination(date, time_index["timerangeid"], institution_id, hospital_id, hospital_name)
            if self.success_flag:
                return

    def sec_hospital_vaccination(self, info, dates):
        """
        预约某个医院希望预约的时段
        :param info: 医院信息
        :param dates: 预约日期
        :return:
        """
        hospital_name = "%s（%s）" % (info["InstitutionName"], info["Address"])
        time_ranges = {}
        while True:
            for date in dates:
                institution_id = info["InstitutionId"]
                hospital_id = info["Id"]
                try:
                    # 该日期下的所有时间段
                    if hospital_id not in time_ranges:
                        time_ranges.update(
                            {hospital_id: self.get_hospital_time_range(institution_id, date, hospital_name)})
                    print(" %s ------ 预约时段获取成功，开始执行疫苗预约..." % hospital_name)
                    # 遍历所有时段，进行疫苗预约
                    self.sec_vaccination_by_time_ranges(time_ranges[hospital_id], date, institution_id, hospital_id,
                                                        hospital_name)
                except Exception as e:
                    log.error(str(e))
                if self.success_flag:
                    return
            print("\n\n %s ------ 所有日期尝试均未预约成功，等待几秒再尝试..." % hospital_name)
            wait_some_time()
            if self.success_flag:
                return

    def execute(self, dates, hospital_sec_infos):
        """
        执行预约
        :param dates: 需要预约的日期
        :param hospital_sec_infos: 选择的医院
        """
        print("\n程序开始执行，将选择医院的所有时段预约，如预约成功则程序停止：")
        with ThreadPoolExecutor(multiprocessing.cpu_count() * 2) as pool:
            # 多线程-遍历所有需要预约的医院
            all_task = [pool.submit(self.sec_hospital_vaccination, info, dates) for info in hospital_sec_infos]
            wait(all_task, return_when=FIRST_COMPLETED)
