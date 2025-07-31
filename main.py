import requests
from bs4 import BeautifulSoup
import re
import unicodedata

URL = "https://www.rinya.maff.go.jp/kanto/apply/publicsale/ippan.html"

# キーワード（完全一致を避け、部分一致を想定）
KEYWORDS = [
    "獣害", "有害鳥獣", "防護柵", "点検", "捕獲",
    "水沼", "桐生", "獣害防護柵点検業務", "R6明許"
]

LINE_TOKEN = "cB46ZPwtJ5c2dj0zlBAJgU6KnjooopohcXUOb0PUiP9mPQ8evPWdKVVkKYHkwz5xT8Q9Ivg7m1ECOQE7/5Fm/3Ka1PwLAyPjGKhfRnZzYAR5eavFBxQ819jy1ir62vI7guCHMmn+2zEaKDDIralkhwdB04t89/1O/w1cDnyilFU="
TO_USER_ID = "Cf28ceaa64690bf45ad9b0b5ece38d8d6"

def normalize(text):
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r"\s+", "", text)  # 改行・全角スペース含む全空白を除去
    return text.strip()

def fetch_announcements():
    resp = requests.get(URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("table tr")
    
    results = []
    for tr in rows:
        cols = tr.find_all("td")
        if len(cols) >= 4:
            # 件名取得（リンク付き対応）
            link_tag = cols[3].find("a")
            raw_title = link_tag.get_text(strip=True) if link_tag else cols[3].get_text(strip=True)
            norm_title = normalize(raw_title)
            if any(normalize(kw) in norm_title for kw in KEYWORDS):
                results.append({
                    "部署": cols[0].get_text(strip=True),
                    "公告日": cols[1].get_text(strip=True),
                    "入札日": cols[2].get_text(strip=True),
                    "件名": raw_title
                })
    return results

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
    print("LINE送信:", response.status_code, response.text)

def main():
    announcements = fetch_announcements()
    if announcements:
        msg = "🔔 公告が見つかりました：\n"
        for ann in announcements:
            msg += f"・{ann['件名']}（{ann['公告日']} 入札: {ann['入札日']}）\n"
    else:
        msg = "本日該当する公告はありません。"
    print(msg)
    send_line_message(msg)

if __name__ == "__main__":
    main()
