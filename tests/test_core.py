import tempfile, pathlib
from unittest import mock
from src import config, cwa_client, repository as repo, weather_service as svc

def _el(name, vals):
    return {"elementName": name, "time": [
        {"startTime": f"2099-01-0{i+1} 06:00:00", "endTime": f"2099-01-0{i+1} 18:00:00",
         "parameter": {"parameterName": str(v)}} for i, v in enumerate(vals)]}

def fake_json():
    loc = lambda n: {"locationName": n, "weatherElement": [
        _el("Wx", ["多雲", "晴", "陰"]), _el("PoP", [10, 20, 30]),
        _el("MinT", [22, 23, 24]), _el("MaxT", [30, 31, 32]), _el("CI", ["舒適"] * 3)]}
    bad = {"locationName": "壞資料", "weatherElement": []}
    return {"records": {"location": [loc("臺中市"), loc("臺北市"), bad]}}

def setup(tmp):
    config.DB_PATH = pathlib.Path(tmp) / "t.db"
    config.API_KEY = "x"

def resp():
    r = mock.Mock(); r.json.return_value = fake_json(); r.raise_for_status = lambda: None
    return r

def test_parse_skips_bad_location():
    setup(tempfile.mkdtemp())
    with mock.patch("requests.get", return_value=resp()):
        rows = cwa_client.fetch_forecasts()
    assert len(rows) == 6 and {r["location"] for r in rows} == {"臺中市", "臺北市"}

def test_service_fresh_cache_stale():
    setup(tempfile.mkdtemp())
    with mock.patch("requests.get", return_value=resp()) as g:
        rows, _, st, _ = svc.get_forecast("臺中市"); assert st == "fresh" and len(rows) == 3
        _, _, st, _ = svc.get_forecast("臺中市"); assert st == "cache" and g.call_count == 1
    with mock.patch("requests.get", side_effect=__import__("requests").Timeout()):
        rows, _, st, msg = svc.get_forecast("臺中市", force=True)
        assert st == "stale" and rows and "失敗" in msg
        _, _, st, _ = svc.get_forecast("不存在", force=True); assert st == "empty"

def test_missing_key():
    config.API_KEY = ""
    try: cwa_client.fetch_forecasts(); assert False
    except cwa_client.CWAError: pass
