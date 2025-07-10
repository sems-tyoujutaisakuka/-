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
        cols = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cols) >= 4:
            title = cols[3]
            if any(kw in title for kw in KEYWORDS):
                link_tag = tr.find("a")
                url = link_tag['href'] if link_tag else URL
                results.append({
                    "部署": cols[0],
                    "公告日": cols[1],
                    "入札日": cols[2],
                    "件名": title,
                    "URL": url
                })
    return results

if __name__ == "__main__":
    announcements = fetch_announcements()
    if announcements:
        msg = ""
        for ann in announcements:
            line = f"📢 {ann['部署']} | {ann['件名']} | 入札日: {ann['入札日']} | URL: {ann['URL']}\n"
            print(line)
            msg += line
        import requests as req_line
        LINE_TOKEN = os.getenv("LINE_TOKEN")
        TO_USER_ID = os.getenv("TO_USER_ID")
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
        send_line_message(msg)
    else:
        print("該当する公告はありません。")
        send_line_message("今日の該当する公告はありません。")

