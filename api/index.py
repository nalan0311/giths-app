import requests
from flask import Flask, render_template, request
from datetime import datetime, timedelta
import re

def find(grade, class_num, start_date, end_date):
    API_KEY = "2610b8ff5d1c4c8e9a10121c64cae8d7"
    ATPT_CODE = "J10"      
    SD_SCH_CODE = "7530989"  
    URL = "https://open.neis.go.kr/hub/hisTimetable"

    params = {
        "KEY": API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ATPT_CODE,
        "SD_SCHUL_CODE": SD_SCH_CODE,
        "TI_FROM_YMD": start_date,  
        "TI_TO_YMD": end_date,                    
        "GRADE": grade,
        "CLASS_NM": class_num
    }

    try:
        response = requests.get(URL, params=params)
        data = response.json()
        return data
    except Exception as e:
        print(f"API 요청 오류: {e}")
        return None

def get_lunch(date) :
    API_KEY = "5953dab680c944669c36fe4e51fd5920"
    ATPT_CODE = "J10"
    SD_SCHUL_CODE = "7530989"
    URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"


    params = {
        "KEY": API_KEY,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ATPT_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,
        "TI_FROM_YMD": date
    }
    response = requests.get(URL, params=params)
    data = response.json()
    return data

app = Flask(__name__, template_folder='../templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_time_table', methods=["POST", "GET"])
def getTimeTable():
    base_date = datetime.now()  # 여기 날짜 집어넣으면 바뀜 datetine.now() >> "20251111" 이런식으로
    monday_obj = base_date - timedelta(days=base_date.weekday())
    
    week_dates = []
    day_to_week = {}
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    
    for i in range(5):
        date_str = (monday_obj + timedelta(days=i)).strftime("%Y%m%d")
        week_dates.append(date_str)
        day_to_week[date_str] = day_names[i]

    grade = request.form.get('grade')
    class_num = request.form.get('class_num')

    data = find(grade, class_num, week_dates[0], week_dates[4])

    content = {}

    for d in day_names:
        for p in range(1, 8):
            content[f"{d}{p}"] = ""

    if data and 'hisTimetable' in data:
        for lesson in data['hisTimetable'][1]['row']:
            day_key = day_to_week.get(lesson['ALL_TI_YMD']) 
            period = lesson['PERIO']
            subject = lesson['ITRT_CNTNT']
            subject = re.sub(r"[0123456789.*]", '', subject)
            
            if day_key:
                content[f"{day_key}{period}"] = subject
    today = datetime.now()
    data = get_lunch(today)
    menu = next((item for item in data['mealServiceDietInfo'][1]['row'] if item['MLSV_YMD'] == today), None)

    if menu:
        print(f"[{today}] 메뉴: {menu['DDISH_NM']}")
        Menu = menu['DDISH_NM']
        clean_menu = Menu.replace('<br/>', '\n')
        clean_menu = re.sub(r"[0123456789.*]", '', clean_menu)
        return render_template('index.html', lunch_of_today = clean_menu, **content, selected_grade=grade, selected_class=class_num)
    else:
        print("데이터없")
    return render_template('index.html', lunch_of_today = "오늘은 급식이 없습니다", **content, selected_grade=grade, selected_class=class_num)

if __name__ == "__main__":

    app.run(debug=True)
