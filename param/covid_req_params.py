"""
@author tuoxie
@desc 定义请求的参数
@date 2021/5/28
"""
from constant import constant


def get_login_params(account, pwd):
    """
    获取登陆参数
    :param account: 账号
    :param pwd: 密码
    :return: 登陆所需参数
    """
    return {
        "account": account,
        "pwd": pwd,
        "device": "Android",
        "pid": 0
    }


def get_vaccination_addr_params(district, stitches):
    """
    获取列表请求
    :param stitches: 第几针
    :param district: 区域。eg: 天河区
    :return:
    """
    return {
        "VaccineType": constant.SEC_TYPE,  # 疫苗类型
        "StepIndex": stitches,
        "Province": "广东省",
        "City": "广州市",
        "District": district,
        "OFFSET": 0,
        "FETCH": 200
    }


def get_hospital_time_range_params(child_id, institution_id, date):
    """
    获取社区医院预约参数
    :param institution_id: 可从某个社区医院的响应信息获取
    :param date: 需要预约哪一天，格式：yyyy-MM-dd
    :param child_id:
    :param institution_id:
    :param work_date:
    :return:
    """
    return {
        "ChildId": child_id,
        "Workdate": date,
        "InstitutionId": institution_id
    }


def get_sec_vaccination_params(child_id, date, time_frame_index, institution_id, hospital_id, stitches):
    """
    执行预约操作
    :param child_id: 固定参数，页面写死
    :param date: 预约哪一天
    :param time_frame_index: 哪一个时段，程序默认全部时段去尝试
    :param institution_id: 可从某个社区医院的响应信息获取
    :param hospital_id: 社区医院的唯一标识
    :param stitches: 第几针
    :return:
    """
    return {
        "ChildId": child_id,
        "RsvDate": date,
        "TimeRangeId": time_frame_index,
        "InstitutionId": institution_id,
        "InstitutionMedicineStockId": hospital_id,
        "StepIndex": stitches
    }
