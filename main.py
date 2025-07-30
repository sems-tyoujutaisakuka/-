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
        cols = [td.get_text(strip=True).replace('\u3000', '').replace(' ', '') for td in tr.find_all("td")]
        if len(cols) >= 4:
            title = cols[3]
            if any(kw in title for kw in KEYWORDS):
                link_tag = tr.find("a")
                url = URL  # デフォルトページURL
                if link_tag and link_tag.has_attr('href'):
                    href = link_tag['href']
                    if href.startswith('http'):
                        url = href
                    else:
                        url = URL.rsplit('/', 1)[0] + '/' + href
                results.append({
                    "部署": cols[0],
                    "公告日": cols[1],
                    "入札日": cols[2],
                    "件名": cols[3],
                    "URL": url
                })
    return results

# LINE送信用
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
        msg = ""
        for ann in announcements:
            line = f"📢 {ann['部署']} | 公告日: {ann['公告日']} | 入札日: {ann['入札日']} | 件名: {ann['件名']} | URL: {ann['URL']}\n"
            print(line)
            msg += line
        send_line_message(msg)
    else:
        print("該当する公告はありません。")
        send_line_message("今日の該当する公告はありません。")
