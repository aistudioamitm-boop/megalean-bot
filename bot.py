import requests
import os
import time
import sys
from urllib.parse import quote

# --- Configuration ---
TOKEN = '8366323813:AAEjGQjQmcNuM74DFeh86cnQRni1_ITk7Vw'
CHAT_ID = '-1003794694855'

# Google Sheet Configuration
SHEET_ID = '1QQvyCfaNoLjr1YkMgUCsI9mj0CAn4PyFWPNAfChuTHY'
SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv'

def get_watchlist_from_sheets():
    try:
        # משיכת הנתונים מהגיליון כפורמט CSV
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        response.encoding = 'utf-8'
        
        # פיצול לשורות וניקוי רווחים/שורות ריקות
        lines = response.text.splitlines()
        # לוקח רק את העמודה הראשונה מכל שורה
        names = [line.split(',')[0].strip() for line in lines if line.strip()]
        
        # הסרת כותרת אם קיימת (למשל אם כתבת "שם המופע" בשורה הראשונה)
        # אם השורה הראשונה היא כבר שם לחיפוש, אפשר להוריד את ה-if הבא
        if names and (names[0] == "שם" or names[0] == "Name"):
            names = names[1:]
            
        print(f"✅ Fetched {len(names)} items from Google Sheets.")
        return names
    except Exception as e:
        print(f"❌ Error fetching from Sheets: {e}")
        return []

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
    print("--- Starting Remote Megalean Check via Google Sheets ---")
    names = get_watchlist_from_sheets()
    
    if not names:
        print("Watchlist is empty.")
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

    # הודעת סיום בטלגרם
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": "✅ סבב החיפוש הסתיים בהצלחה."})

    print("--- All checks completed. ---")

if __name__ == '__main__':
    main()
