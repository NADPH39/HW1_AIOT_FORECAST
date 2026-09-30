# HW1_AIOT_FORECAST
台灣天氣預報（Streamlit + SQLite + 中央氣象署 F-C0032-001）。以台灣地圖點選縣市。

## 啟動
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # 填入 CWA_API_KEY
streamlit run app.py
```
## 部署（Streamlit Community Cloud）
連結此 GitHub repo，於 App settings → Secrets 加入：
```
CWA_API_KEY = "你的金鑰"
```
金鑰只放 `.env` 或 Secrets，切勿提交。

## 測試
```bash
pip install -r requirements-dev.txt
pytest
```
測試使用模擬的 CWA 回應，涵蓋解析、快取、API 失敗時退回舊資料與缺少金鑰。

## 推送到 GitHub
```bash
git remote add origin https://github.com/<你的帳號>/HW1_AIOT_FORECAST.git
git push -u origin main
```
推送前請執行 `git status` 確認沒有 `.env` 或 `.db` 檔。

## 已知限制
- 資料為 12 小時時段的 36 小時預報，沒有 3 小時間隔。
- 地圖為縣市中心點標記，沒有行政區界線。
