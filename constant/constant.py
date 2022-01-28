# 请求成功
RESPONSE_OK = 200

# 请求所需的URL地址
URLS = {
    # 主机地址
    "hostUrl": "https://m.r.umiaohealth.com/",
    # 获取疫苗接种列表地址；POST
    "vaccinationAddress": "/InstitutionMedicineStock/GetBykeyword_InstitutionMedicineStock",
    # 获取某个社区医院的某一天可预约的时间段
    "hospitalTimeRange": "/Reservation/GetByWorkDate_Rsv_TimeRange",
    # 执行疫苗预约请求 url；GET
    "secVaccination": "/Reservation/Reservation_Create",
    # 获取 childId
    "childId": "/Adult/Index",
    # 获取用户信息
    "userMsg": "/Home/My"
}

# 区域名称
AREAS = [
    "天河区",
    "白云区",
    "黄埔区",
    "荔湾区",
    "越秀区",
    "海珠区",
    "番禺区",
    "花都区",
    "南沙区",
    "增城区",
    "从化区"
]

# 所有疫苗类型
VACCINE_TYPES = {
    "veroCell": 5601,  # 新冠疫苗（Vero细胞）
    "adenovirusVector": 5602  # 新冠疫苗（腺病毒载体）
    # etc...
}

# 需要预约的疫苗类型
SEC_TYPE = VACCINE_TYPES["veroCell"]
