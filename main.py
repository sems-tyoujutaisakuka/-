import requests
from bs4 import BeautifulSoup

# 対象ページとキーワード
URL = "https://www.rinya.maff.go.jp/kanto/apply/publicsale/ippan.html"
KEYWORDS = ["有害鳥獣", "捕獲", "防護柵", "点検"]

from bs4 import BeautifulSoup
import requests

URL = "https://www.rinya.maff.go.jp/kanto/apply/publicsale/ippan.html"
KEYWORDS = ["有害鳥獣", "捕獲", "防護柵", "点検"]

def fetch_announcements():
    resp = requests.get(URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("table tr")
    results = []

    for tr in rows:
        cols = tr.find_all("td")
        if len(cols) >= 4:
            raw_title_html = cols[3]
            title_text = raw_title_html.get_text(strip=True).replace('\u3000', '').replace(' ', '')

            if any(kw in title_text for kw in KEYWORDS):
                results.append({
                    "部署": cols[0].get_text(strip=True),
                    "公告日": cols[1].get_text(strip=True),
                    "入札日": cols[2].get_text(strip=True),
                    "件名": title_text
                })
    return results

# LINE送信用（LINE公式Botを使用）
import requests as req_line

LINE_TOKEN = 'cB46ZPwtJ5c2dj0zlBAJgU6KnjooopohcXUOb0PUiP9mPQ8evPWdKVVkKYHkwz5xT8Q9Ivg7m1ECOQE7/5Fm/3Ka1PwLAyPjGKhfRnZzYAR5eavFBxQ819jy1ir62vI7guCHMmn+2zEaKDDIralkhwdB04t89/1O/w1cDnyilFU='
TO_USER_ID = 'Cf28ceaa64690bf45ad9b0b5ece38d8d6'

def send_line_message(message):
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": TO_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    response = req_line.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
    print("LINE送信結果:", response.status_code, response.text)

if __name__ == "__main__":
    announcements = fetch_announcements()
    if announcements:
        msg = "📢 本日の公告（キーワード一致）:\n"
        for ann in announcements:
            msg += f"- {ann['件名']}\n"
        send_line_message(msg)
    else:
        print("該当する公告はありません。")
        send_line_message("📭 本日該当する公告はありません。")
