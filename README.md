# Aralia-OpenRAG


## Python虛擬環境
- 建立虛擬環境：`python3 -m virtualenv .venv`
- 進入虛擬環境：`source .venv/bin/activate`
- 離開虛擬環境：`deactivate`

## Python套件
- 安裝必要套件：`pip3 install -r requirements.txt`
- 開發者更新requirements.txt：`pip3 freeze > requirements.txt`


## 環境變數設定
- 複製.env.sample：`cp .env.sample .env`
- 修改.env
    1. OPENAI_API_KEY：openai的金鑰，通常是sk開頭，用於使用openai的api服務。
    2. ARALIA_ENDPOINT：數據星球的URL，後綴包含/api。
    3. ARALIA_TOKEN：數據星球的Bareer認證Token。