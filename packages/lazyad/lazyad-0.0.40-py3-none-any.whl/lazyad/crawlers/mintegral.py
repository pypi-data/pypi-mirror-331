from lazysdk import lazyrequests
from lazysdk import lazytime
import copy


"""
官网：https://adv.mintegral.com/cn/login
"""
default_headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflated",
        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": "",
        "Host": "ss-api.mintegral.com",
        "Origin": "https://adv.mintegral.com",
        "Pragma": "no-cache",
        "Referer": "https://adv.mintegral.com/cn/login",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Sec-GPC": "1",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0"
    }


def auth(
        cookie: str
):
    """
    验证cookie是否有效
    需要登录：{'code': 400, 'msg': 'Please login first', 'data': None}
    验证成功：{'code': 200, 'msg': 'success', 'data': {}

    """
    url = "https://ss-api.mintegral.com/api/v1/auth"
    headers = copy.deepcopy(default_headers)
    headers["Cookie"] = cookie
    return lazyrequests.lazy_requests(
        method="GET",
        url=url,
        headers=headers
    )


def options(
        cookie: str
):
    """
    获取系统的基本选项
    需要登录：{'code': 400, 'msg': 'Please login first', 'data': None}
    验证成功：
        {
            'code': 200,
            'msg': 'success',
            'data': {
                'offer': ...,
                'campaign': ...,
                ...
                }
        }
    """
    scheme = "https"
    host = "ss-api.mintegral.com"
    filename = "/api/v1/options/_batch"
    params = {
        "query": "offer,campaign,offer-status,billing-type,country,timezone,country-region-city"
    }
    url = f"{scheme}://{host}{filename}"
    headers = copy.deepcopy(default_headers)
    headers["Cookie"] = cookie
    return lazyrequests.lazy_requests(
        method="GET",
        params=params,
        url=url,
        headers=headers
    )


def offers(
        cookie: str,
        offer_id: int = None,
        method: str = "GET",
        put_data: dict = None,
        page: int = 1,
        page_size: int = 50
):
    """
    获取广告单元列表
    需要登录：{'code': 400, 'msg': 'Please login first', 'data': None}
    验证成功：{'code': 200, 'msg': 'success', 'data': {}
    """
    scheme = "https"
    host = "ss-api.mintegral.com"
    if not offer_id:
        filename = "/api/v1/offers"
        params = {
            "limit": page_size,
            "page": page,
            "order": "DESC",
            "sort": "id"
        }
    else:
        filename = f"/api/v1/offers/{offer_id}"
        if method == "PUT":
            params = put_data
        else:
            params = {}

    url = f"{scheme}://{host}{filename}"
    headers = copy.deepcopy(default_headers)
    headers["Cookie"] = cookie
    return lazyrequests.lazy_requests(
        method=method,
        params=params,
        url=url,
        headers=headers
    )


def performance(
        cookie: str,
        page: int = 1,
        page_size: int = 50,
        timezone: int = 8,
        start_time: str = None,
        end_time: str = None,
        show_calendar_day: int = 2,
        total: bool = False,
        breakdowns: list = None,
        metrics: list = None
):
    """
    获取广告单元列表
    需要登录：{'code': 400, 'msg': 'Please login first', 'data': None}
    验证成功：{'code': 200, 'msg': 'success', 'data': {}
    """
    scheme = "https"
    host = "ss-api.mintegral.com"
    filename = "/api/v1/reports/performance"
    filename_total = "/api/v1/reports/performance-total"
    if not start_time:
        start_time = lazytime.get_date_string(days=0)
    if not end_time:
        end_time = lazytime.get_date_string(days=0)
    if not breakdowns:
        breakdowns = ["date", "adv_offer_id"]
    if not metrics:
        metrics = [
            "adv_impression",
            "adv_click",
            "adv_install",
            "ecpm",
            "ecpc",
            "ecpi",
            "ctr",
            "ivr",
            "cvr",
            "adv_original_money",
            "iaa_d0_ad_revenue",
            "iaa_d0_roas"
        ]
    params = {
        "limit": page_size,
        "page": page,
        "timezone": timezone,
        "start_time": start_time,
        "end_time": end_time,
        "order": "DESC",
        "breakdowns": ",".join(breakdowns),
        "metrics": ",".join(metrics),
        "show_calendar_day": show_calendar_day
    }
    url = f"{scheme}://{host}{filename}"
    url_total = f"{scheme}://{host}{filename_total}"
    headers = copy.deepcopy(default_headers)
    headers["Cookie"] = cookie
    if total:
        return lazyrequests.lazy_requests(
            method="GET",
            params=params,
            url=url_total,
            headers=headers
        )
    else:
        return lazyrequests.lazy_requests(
            method="GET",
            params=params,
            url=url,
            headers=headers
        )
