import requests
from bs4 import BeautifulSoup
import re

# ==========================
# 設定
# ==========================
URL = "https://www.rinya.maff.go.jp/kanto/apply/publicsale/ippan.html"
KEYWORDS = ["有害鳥獣", "捕獲", "防護柵", "点検", "獣害", "水沼・桐生地区獣害防護柵点検業務委託（R6明許）"]

# LINE Messaging API トークンと送信先
LINE_TOKEN = "cB46ZPwtJ5c2dj0zlBAJgU6KnjooopohcXUOb0PUiP9mPQ8evPWdKVVkKYHkwz5xT8Q9Ivg7m1ECOQE7/5Fm/3Ka1PwLAyPjGKhfRnZzYAR5eavFBxQ819jy1ir62vI7guCHMmn+2zEaKDDIralkhwdB04t89/1O/w1cDnyilFU="         # ←自分のMessaging APIチャネルアクセストークンを入力
TO_USER_ID = "Cf28ceaa64690bf45ad9b0b5ece38d8d6"        # ←送信先のuserIdやgroupIdを入力

# ==========================
# 正規化関数（テキストの比較用）
# ==========================
def normalize(text):
    # 全角スペース・改行・タブなど除去 + strip()
    text = re.sub(r"[\u3000\s]", "", text)
    return text.strip()

# ==========================
# 公告取得関数
# ==========================
def fetch_announcements():
    resp = requests.get(URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("table tr")

    results = []
    for tr in rows:
        cols = tr.find_all("td")
        if len(cols) >= 4:
            # 件名列（aタグが中にある場合を考慮）
            a_tag = cols[3].find("a")
            title_raw = a_tag.get_text(strip=True) if a_tag else cols[3].get_text(strip=True)
            title = normalize(title_raw)
            # キーワードがタイトルに含まれていれば保存
            if any(kw in title for kw in KEYWORDS):
                results.append(title_raw)  # 通知では元の件名を使う
    return results

# ==========================
# LINE メッセージ送信関数
# ==========================
def send_line_message(message):
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": TO_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print("LINE送信結果:", response.status_code, response.text)

# ==========================
# メイン処理
# ==========================
def main():
    announcements = fetch_announcements()
    if announcements:
        msg = "🔔 該当の公告があります：\n" + "\n".join(f"・{title}" for title in announcements)
    else:
        msg = "本日該当する公告はありません。"
    print(msg)
    send_line_message(msg)

if __name__ == "__main__":
    main()
