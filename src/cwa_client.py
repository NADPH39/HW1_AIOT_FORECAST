import requests
from . import config

class CWAError(Exception):
    pass

def _val(elements, name, i):
    el = elements.get(name)
    if el is None or i >= len(el):
        raise CWAError(f"缺少欄位 {name}")
    return el[i]

def fetch_forecasts():
    """回傳 list[dict]：每個縣市 × 每個 12 小時時段一列。"""
    if not config.API_KEY:
        raise CWAError("未設定 CWA_API_KEY")
    try:
        r = requests.get(config.URL, params={"Authorization": config.API_KEY,
                         "format": "JSON"}, timeout=config.TIMEOUT)
        r.raise_for_status()
        data = r.json()
        locations = data["records"]["location"]
    except (requests.RequestException, ValueError, KeyError) as e:
        raise CWAError(f"取得 CWA 資料失敗：{type(e).__name__}") from None
    rows = []
    for loc in locations:
        try:
            els = {e["elementName"]: e["time"] for e in loc["weatherElement"]}
            for i, t in enumerate(els["Wx"]):
                rows.append(dict(
                    location=loc["locationName"],
                    start=t["startTime"], end=t["endTime"],
                    wx=t["parameter"]["parameterName"],
                    pop=int(_val(els, "PoP", i)["parameter"]["parameterName"]),
                    min_t=int(_val(els, "MinT", i)["parameter"]["parameterName"]),
                    max_t=int(_val(els, "MaxT", i)["parameter"]["parameterName"]),
                    ci=_val(els, "CI", i)["parameter"]["parameterName"],
                ))
        except (KeyError, ValueError, TypeError, CWAError):
            continue  # 略過不完整的單一縣市，不讓整頁崩潰
    if not rows:
        raise CWAError("回應中沒有可用的預報資料")
    return rows
