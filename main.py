import requests
from bs4 import BeautifulSoup
import re
import os

# 通知対象のキーワード（部分一致）
KEYWORDS = ["獣害防護柵", "捕獲", "点検業務"]

# 林野庁公告ページURL
URL = "https://www.rinya.maff.go.jp/kanto/apply/nyusatsu/nyusatsu_ichiran.html"

# LINE通知用トークン（GitHub Secretsなどに入れてください）
LINE_TOKEN = os.getenv("cB46ZPwtJ5c2dj0zlBAJgU6KnjooopohcXUOb0PUiP9mPQ8evPWdKVVkKYHkwz5xT8Q9Ivg7m1ECOQE7/5Fm/3Ka1PwLAyPjGKhfRnZzYAR5eavFBxQ819jy1ir62vI7guCHMmn+2zEaKDDIralkhwdB04t89/1O/w1cDnyilFU=")

# 正規化処理：空白除去＋全角記号などの統一（簡易）
def normalize(text):
    return re.sub(r"[\u3000\s]", "", text).strip()

# 公告を抽出
def fetch_announcements():
    resp = requests.get(URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("table tr")

    results = []
    for tr in rows:
        cols = tr.find_all("td")
        if len(cols) >= 4:
            a_tag = cols[3].find("a")
            title = a_tag.get_text(strip=True) if a_tag else cols[3].get_text(strip=True)
            norm_title = normalize(title)
            if any(keyword in norm_title for keyword in KEYWORDS):
                results.append(title)
    return results

# LINE通知
def notify_line(message):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {LINE_TOKEN}"}
    data = {"message": message}
    response = requests.post(url, headers=headers, data=data)
    print("LINE送信結果:", response.status_code, response.text)

# メイン処理
def main():
