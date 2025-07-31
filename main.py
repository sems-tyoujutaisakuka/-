import requests
from bs4 import BeautifulSoup
import re
import unicodedata

# ========== 設定 ========== #
URL = "https://www.rinya.maff.go.jp/kanto/apply/publicsale/ippan.html"
KEYWORDS = ["有害鳥獣", "獣害", "防護柵", "捕獲", "点検", "水沼", "桐生", "甲府", "引佐"]

LINE_TOKEN = "cB46ZPwtJ5c2dj0zlBAJgU6KnjooopohcXUOb0PUiP9mPQ8evPWdKVVkKYHkwz5xT8Q9Ivg7m1ECOQE7/5Fm/3Ka1PwLAyPjGKhfRnZzYAR5eavFBxQ819jy1ir62vI7guCHMmn+2zEaKDDIralkhwdB04t89/1O/w1cDnyilFU="
TO_USER_ID = "Cf28ceaa64690bf45ad9b0b5ece38d8d6"

# ========== 正規化関数 ========== #
def normalize(text):
    text = unicodedata.normalize('NFKC', text)  # 全角→半角など統一
    text = re.sub(r"\s+", "", text)             # 改行・空白削除
    return text

# ========== 公告全文検索 ========== #
def fetch_announcements_by_page_text():
    res = requests.get(URL)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    # ページ全文を正規化して1行ずつ分割
    full_text = normalize(soup.get_text())
    lines = full_text.split("。")  # 句点で分割（任意で改行でも可）

    matched_lines = []
    for line in lines:
        if any(normalize(kw) in line for kw in KEYWORDS):
            matched_lines.append(line.strip())

    return matched_lines

# ========== LINE送信 ========== #
def send_line_message(msg):
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": TO_USER_ID,
        "messages": [{"type": "text", "text": msg[:1000]}]  # LINE制限: 1メッセージ 1000文字以内
    }
    res = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=payload)
    print("LINE送信:", res.status_code, res.text)

# ========== メイン処理 ========== #
def main():
    results = fetch_announcements_by_page_text()
    if results:
        msg = "🔔 該当する公告をページ全体から発見：\n"
        for i, line in enumerate(results, 1):
            msg += f"{i}. {line}\n"
    else:
        msg = "本日該当する公告は見つかりませんでした。"

    print(msg)
    send_line_message(msg)

if __name__ == "__main__":
    main()
