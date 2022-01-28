"""
@author tuoxie
@desc 主程序
@date 2021/5/28
"""
import datetime
import re
import os

from config import config
from constant import constant
from util import message_util
from util.covid_util import CovidHttpReq


def get_dates():
    """
    从配置文件中读取预约疫苗的日期
    :return: 大于等于今天，且不重复的日期
    """
    filter_dates = []
    # 去掉空格，替换中文逗号为英文逗号，后根据英文逗号切分日期，最后去重
    space_pattern = re.compile("\\s+")
    config_dates = config.global_config.getConfigSection("date").__str__()
    for config_date in set(re.sub(space_pattern, "", config_dates).replace(
            "，", ",").split(",")):
        if int(config_date.replace("-", "")) < int(datetime.datetime.now().strftime("%Y%m%d")):
            continue
        filter_dates.append(config_date)
    return filter_dates


def valid_config_and_get_dates():
    """
    校验配置文件的参数，并返回配置文件的预约疫苗日期
    :return:
    """
    if config.global_config.getConfigSection("cookie") == "":
        raise Exception("请先配置登陆后的 cookie，查看方式请查看 README.MD")
    if config.global_config.getConfigSection("date") == "":
        raise Exception("请先配置登陆后的 预约日期")
    valid_dates = get_dates()
    if len(valid_dates) == 0:
        raise Exception("预约日期未配置或配置不正确（预约日期需要大于等于今天），请重新配置预约日期")
    return valid_dates


def choose_hospital_msg(inner_hospital_infos):
    """
    选择社区医院
    :param inner_hospital_infos: 医院完整信息
    :return:
    """
    for j, info in enumerate(inner_hospital_infos["aaData"], start=1):
        print("%d.\t疫苗余量：%d\t医院名称：【%s（%s）】\t疫苗厂家：%s - %s" % (
            j, info["SeqNo"], info["InstitutionName"], info["Address"], info["Corp_Name"], info["VaccineName"]))

    print("\n请输入医院前数字按回车确定选择（即使余量为 0 也可以选择，说不定捡漏了呢  []~（￣▽￣）~*）")
    print("多个可以使用逗号隔开如 1,2,3 。")
    choose_hospital_str = input("请选择需要预约疫苗的区域按回车确定选择（输入数字）：")
    if "0" == choose_hospital_str:
        return inner_hospital_infos["aaData"]

    # 根据选择筛选医院
    choose_hospital_indexes = choose_hospital_str.replace(" ", "").replace("，", ",").split(",")
    inner_hospital_sec_infos = []
    for choose_hospital_index in choose_hospital_indexes:
        if int(choose_hospital_index) >= len(inner_hospital_infos["aaData"]):
            raise Exception("输入医院错误")
        # 保存选择的医院信息
        inner_hospital_sec_infos.append(inner_hospital_infos["aaData"][int(choose_hospital_index) - 1])
    return inner_hospital_sec_infos


if __name__ == "__main__":
    try:
        dates = valid_config_and_get_dates()
        for i in range(len(constant.AREAS)):
            print(str((i + 1)) + ".\t" + constant.AREAS[i])
        chooseArea = constant.AREAS[int(input("请选择需要预约疫苗的区域按回车确定选择（输入数字）：")) - 1]

        covid = CovidHttpReq()
        user_msg = covid.match_user_msg()
        print("\n当前用户信息：『 %s 』\n" % user_msg)

        print("正在获取 %s 的医院信息..." % chooseArea)
        # 可以预约的医院信息
        hospital_infos = covid.get_vaccination_msg(chooseArea)
        if hospital_infos is None:
            raise Exception("获取社区医院信息失败...")

        if len(hospital_infos["aaData"]) == 0:
            print("医院信息为空，服务器信息《%s》，请尝试重新登陆" % hospital_infos["ret_msg"])
        else:
            hospital_sec_infos = choose_hospital_msg(hospital_infos)
            covid.execute(dates, hospital_sec_infos)
            if covid.success_flag:
                message_util.send_wechat("疫苗预约成功，请登录 App 查看预约结果！")

            # 保存医院信息到配置文件，以便下次直接请求
            with open(chooseArea + ".txt", "w", encoding="utf-8") as fp:
                fp.write(str(hospital_infos["aaData"]))
        print("程序结束。。。")
    except Exception as e:
        print(str(e))
        os.system("pause")
