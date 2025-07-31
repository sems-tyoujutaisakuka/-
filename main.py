import requests
from bs4 import BeautifulSoup
import re
import unicodedata

# ==========================
# 設定
# ==========================
URL = "https://www.rinya.maff.go.jp/kanto/apply/publicsale/ippan.html"
KEYWORDS = ["水沼・桐生地区獣害防護柵点検業務委託（R6明許）", "獣害", "有害鳥獣", "防護柵", "点検", "捕獲"]

LINE_TOKEN = "cB46ZPwtJ5c2dj0zlBAJgU6KnjooopohcXUOb0PUiP9mPQ8evPWdKVVkKYHkwz5xT8Q9Ivg7m1ECOQE7/5Fm/3Ka1PwLAyPjGKhfRnZzYAR5eavFBxQ819jy1ir62vI7guCHMmn+2zEaKDDIralkhwdB04t89/1O/w1cDnyilFU="
TO_USER_ID = "Cf28ceaa64690bf45ad9b0b5ece38d8d6"

# ==========================
# テキスト正規化関数
# ==========================
def normalize(text):
    text = unicodedata.normalize('NFKC', text)  # Unicode正規化（全角→半角など）
    text = re.sub(r"[\s\u3000]", "", text)      # 空白・全角スペースを削除
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
            # 件名（aタグがあればそれを優先）
            a_tag = cols[3].find("a")
            title_raw = a_tag.get_text(strip=True) if a_tag else cols[3].get_text(strip=True)
            title_normalized = normalize(title_raw)
            if any(normalize(kw) in title_normalized for kw in KEYWORDS):
                results.append(title_raw)
    return results

# ==========================
# LINE送信関数
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
# メイン関数
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
