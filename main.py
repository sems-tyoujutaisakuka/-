import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.rinya.maff.go.jp/kanto/apply/publicsale/ippan.html#jump08"
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

def send_line_message(message):
    line_token = os.environ.get('LINE_TOKEN')  # 👈 環境変数から取得
    to_user_id = os.environ.get('TO_USER_ID')  # 👈 環境変数から取得

    headers = {
        "Authorization": f"Bearer {line_token}",
        "Content-Type": "application/json"
    }
    data = {
        "to": to_user_id,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post('https://api.line.me/v2/bot/message/push', headers=headers, json=data)
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

