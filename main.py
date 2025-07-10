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
        text = tr.get_text()
        if any(kw in text for kw in KEYWORDS):
            cols = [td.get_text(strip=True) for td in tr.find_all("td")]
            link_tag = tr.find("a")
            url = link_tag['href'] if link_tag else URL
            results.append({
                "部署": cols[0] if len(cols) > 0 else "",
                "公告日": cols[1] if len(cols) > 1 else "",
                "入札日": cols[2] if len(cols) > 2 else "",
                "件名": cols[3] if len(cols) > 3 else "",
                "URL": url
            })
    return results

if __name__ == "__main__":
    announcements = fetch_announcements()
    if announcements:
        for ann in announcements:
            print(f"📢 {ann['部署']} | {ann['件名']} | 入札日: {ann['入札日']} | URL: {ann['URL']}")
    else:
        print("該当する公告はありません。")
import requests as req_line

# LINE設定
LINE_TOKEN = 'epg02OQhEYt7fBYFILNh/aAFiOPF/un2eieXCcdgLWQQjwt2f+jEAtbxCnbJaMOZT8Q9Ivg7m1ECOQE7/5Fm/3Ka1PwLAyPjGKhfRnZzYATyFBh+6yj3tok+yJhj3nzA7dl/LwkZF+dTWl953OXCtgdB04t89/1O/w1cDnyilFU='
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
        msg = ""
        for ann in announcements:
            line = f"📢 {ann['部署']} | {ann['件名']} | 入札日: {ann['入札日']} | URL: {ann['URL']}\n"
            print(line)
            msg += line
        send_line_message(msg)
    else:
        print("該当する公告はありません。")
        send_line_message("今日の該当する公告はありません。")
