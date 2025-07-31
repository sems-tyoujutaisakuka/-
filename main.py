import requests
from bs4 import BeautifulSoup

URL = "https://www.rinya.maff.go.jp/kanto/apply/publicsale/ippan.html"
KEYWORDS = ["有害鳥獣", "捕獲", "防護柵", "点検"]

def fetch_announcements():
    resp = requests.get(URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("table tr")
    results = []
    for tr in rows:
        title = ""
        a_tag = tr.find("a")
        if a_tag:
            title = a_tag.get_text(strip=True)
        else:
            cols = tr.find_all("td")
            if len(cols) >= 4:
                title = cols[3].get_text(strip=True)

        if any(kw in title for kw in KEYWORDS):
            results.append(title)
    return results

# LINE送信用
import requests as req_line

LINE_TOKEN = "cB46ZPwtJ5c2dj0zlBAJgU6KnjooopohcXUOb0PUiP9mPQ8evPWdKVVkKYHkwz5xT8Q9Ivg7m1ECOQE7/5Fm/3Ka1PwLAyPjGKhfRnZzYAR5eavFBxQ819jy1ir62vI7guCHMmn+2zEaKDDIralkhwdB04t89/1O/w1cDnyilFU="
TO_USER_ID = "Cf28ceaa64690bf45ad9b0b5ece38d8d6"

def send_line_message(message):
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "to": TO_USER_ID,
        "messages": [{"type": "text", "text": message}]
    }
    response = req_line.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)
    print("LINE送信結果:", response.status_code, response.text)

if __name__ == "__main__":
    announcements = fetch_announcements()
    if announcements:
        msg = "📢該当する公告:\n" + "\n".join(f"・{a}" for a in announcements)
    else:
        msg = "今日の該当する公告はありません。"
    print(msg)
    send_line_message(msg)
