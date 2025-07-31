import requests
from bs4 import BeautifulSoup
import re
import unicodedata

# ========== 設定 ========== #
URL = "https://www.rinya.maff.go.jp/kanto/apply/publicsale/ippan.html"
KEYWORDS = ["有害鳥獣", "獣害", "防護柵", "捕獲", "点検", "水沼", "桐生", "甲府", "引佐"]

LINE_TOKEN = "cB46ZPwtJ5c2dj0zlBAJgU6KnjooopohcXUOb0PUiP9mPQ8evPWdKVVkKYHkwz5xT8Q9Ivg7m1ECOQE7/5Fm/3Ka1PwLAyPjGKhfRnZzYAR5eavFBxQ819jy1ir62vI7guCHMmn+2zEaKDDIralkhwdB04t89/1O/w1cDnyilFU="  # ここにアクセストークンを入力
TO_USER_ID = "Cf28ceaa64690bf45ad9b0b5ece38d8d6"  # ここに送信先ユーザーまたはグループIDを入力

# ========== 正規化 ========== #
def normalize(text):
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r"\s+", "", text)
    return text

# ========== 公告取得 ========== #
def fetch_announcements():
    res = requests.get(URL)
    res.raise_for_status()

    # 保存して中身確認用（オプション）
    with open("downloaded.html", "w", encoding="utf-8") as f:
        f.write(res.text)
    print("HTMLをdownloaded.htmlとして保存しました。")

    soup = BeautifulSoup(res.text, "html.parser")
    announcements = []

    tables = soup.find_all("table")
    for table in tables:
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) >= 4:
                title_tag = cols[3].find("a")
                title = title_tag.get_text(strip=True) if title_tag else cols[3].get_text(strip=True)
                norm_title = normalize(title)
                if any(normalize(kw) in norm_title for kw in KEYWORDS):
                    announcements.append({
                        "部署": cols[0].get_text(strip=True),
                        "公告日": cols[1].get_text(strip=True),
                        "入札日": cols[2].get_text(strip=True),
                        "件名": title
                    })
    return announcements

# ========== LINE送信 ========== #
def send_line_message(msg):
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": TO_USER_ID,
        "messages": [{"type": "text", "text": msg}]
    }
    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print("LINE送信:", res.status_code, res.text)

# ========== メイン処理 ========== #
def main():
    anns = fetch_announcements()
    if anns:
        msg = "🔔 公告が見つかりました：\n"
        for a in anns:
            msg += f"・{a['件名']}（公告日: {a['公告日']} 入札日: {a['入札日']}）\n"
    else:
        msg = "本日該当する公告はありません。"

    print(msg)
    send_line_message(msg)

if __name__ == "__main__":
    main()
