import requests
import os
import time
import sys
from urllib.parse import quote

# --- Configuration ---
TOKEN = '8366323813:AAEjGQjQmcNuM74DFeh86cnQRni1_ITk7Vw'
CHAT_ID = '-1003794694855'
FILENAME = 'watchlist.txt'

def get_watchlist():
    # מוודא שהקובץ קיים בתיקייה של הסקריפט (מותאם ל-GitHub Actions)
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    file_path = os.path.join(script_dir, FILENAME)
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def perform_check(keyword):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    try:
        search_url = f'https://www.megalean.co.il/site/search/?caller=ac&w={quote(keyword)}'
        response = session.get(search_url, timeout=20)
        response.encoding = 'utf-8'
        html = response.text

        count = html.count(keyword)
        no_results = "לא נמצאו תוצאות" in html

        if count > 1 and not no_results:
            display_count = count - 1
            return f"🎯 **נמצאו כרטיסים ל{keyword}!**\nנמצאו {display_count} תוצאות.\n🔗 {search_url}"
        else:
            return f"🔍 לא נמצאו כרטיסים ל-`{keyword}`."
    except Exception as e:
        return f"⚠️ שגיאה בבדיקת {keyword}: {e}"

def main():
    print("--- Starting Scheduled Megalean Check ---")
    names = get_watchlist()
    
    if not names:
        print("Watchlist is empty or file missing.")
        return

    for item in names:
        print(f"Checking: {item}...")
        message = perform_check(item)
        
        # שליחה לטלגרם
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)
        
        # הפסקה קצרה למניעת חסימות
        time.sleep(2)

    # --- השורה שהוספה ---
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": "✅ סבב החיפוש הסתיים בהצלחה."})
    # ---------------------

    print("--- All checks completed. Closing. ---")

if __name__ == '__main__':
    main()
