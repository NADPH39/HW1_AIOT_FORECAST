import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src import config
from src.weather_service import get_forecast

st.set_page_config(page_title="台灣天氣預報", page_icon="🌤️", layout="wide")

# 縣市中心座標（用於地圖標記，非行政界線）
CITIES = {
 "基隆市":(25.13,121.74),"臺北市":(25.04,121.56),"新北市":(25.01,121.47),
 "桃園市":(24.99,121.30),"新竹市":(24.81,120.97),"新竹縣":(24.70,121.13),
 "苗栗縣":(24.56,120.82),"臺中市":(24.15,120.68),"彰化縣":(24.05,120.52),
 "南投縣":(23.83,120.98),"雲林縣":(23.71,120.43),"嘉義市":(23.48,120.45),
 "嘉義縣":(23.45,120.57),"臺南市":(23.00,120.21),"高雄市":(22.63,120.30),
 "屏東縣":(22.55,120.55),"宜蘭縣":(24.70,121.74),"花蓮縣":(23.75,121.35),
 "臺東縣":(22.99,121.10),"澎湖縣":(23.57,119.58),"金門縣":(24.45,118.32),
 "連江縣":(26.16,119.95)}

st.session_state.setdefault("loc", config.DEFAULT_LOCATION)
st.title("🌤️ 台灣天氣預報")
st.caption("資料來源：中央氣象署 一般天氣預報—今明 36 小時（預報，非即時觀測）")

df = pd.DataFrame([{"city": k, "lat": v[0], "lon": v[1],
       "size": 22 if k == st.session_state["loc"] else 12} for k, v in CITIES.items()])
fig = px.scatter_map(df, lat="lat", lon="lon", hover_name="city", size="size",
        size_max=22, custom_data=["city"], zoom=6.2, center={"lat": 23.7, "lon": 120.9},
        height=520)
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
ev = st.plotly_chart(fig, on_select="rerun", key="map", use_container_width=True)
pts = ev.selection.points if ev and ev.selection else []
pick = pts[0]["customdata"][0] if pts else None
if pick and pick != st.session_state.get("_last_pick"):
    st.session_state["loc"] = pick
st.session_state["_last_pick"] = pick

with st.sidebar:
    st.selectbox("縣市", list(CITIES), key="loc")
    n = st.selectbox("預報時段數（每段 12 小時）", [1, 2, 3], index=2)
    force = st.button("重新整理")

loc = st.session_state["loc"]
with st.spinner("載入中…"):
    rows, fetched, status, msg = get_forecast(loc, force=force)

if status == "empty":
    st.error(f"目前無法取得 {loc} 的資料：{msg}。請稍後按「重新整理」重試。")
    st.stop()
if status == "stale":
    st.warning(f"更新失敗（{msg}），以下為 {fetched:%Y-%m-%d %H:%M} 取得的舊資料。")
if not rows:
    st.info("查無此地點的預報資料。")
    st.stop()

rows = rows[:n]
st.subheader(f"{loc}")
st.caption(f"最近擷取時間：{fetched:%Y-%m-%d %H:%M}（台灣時間）")
for col, r in zip(st.columns(len(rows)), rows):
    with col, st.container(border=True):
        st.markdown(f"**{r['start_time'][5:16]} → {r['end_time'][5:16]}**")
        st.markdown(f"### {r['wx']}")
        st.metric("氣溫 (°C)", f"{r['min_t']} ~ {r['max_t']}")
        st.metric("降雨機率", f"{r['pop']}%")
        st.caption(r["ci"])

t = pd.DataFrame(rows)
f2 = go.Figure()
f2.add_bar(x=t["start_time"], y=t["pop"], name="降雨機率 (%)", opacity=.3, yaxis="y2")
f2.add_scatter(x=t["start_time"], y=t["max_t"], name="最高溫", mode="lines+markers")
f2.add_scatter(x=t["start_time"], y=t["min_t"], name="最低溫", mode="lines+markers")
f2.update_layout(height=320, yaxis_title="°C",
    yaxis2=dict(overlaying="y", side="right", range=[0, 100], title="%"))
st.plotly_chart(f2, use_container_width=True)
