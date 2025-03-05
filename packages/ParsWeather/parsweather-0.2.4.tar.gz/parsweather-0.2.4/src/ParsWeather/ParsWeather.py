import requests
from bs4 import BeautifulSoup
import random
import time
from urllib.parse import urljoin


class WeatherForecast:
    
    air = {
    "آذربایجان شرقی": "https://www.accuweather.com/fa/ir/tabriz/207308/air-quality-index/207308",
    "آذربایجان غربی": "https://www.accuweather.com/fa/ir/urmia/207147/air-quality-index/207147",
    "اردبیل": "https://www.accuweather.com/fa/ir/ardabil/206976/air-quality-index/206976",
    "اصفهان": "https://www.accuweather.com/fa/ir/isfahan/208194/air-quality-index/208194",
    "البرز": "https://www.accuweather.com/fa/ir/karaj/211367/air-quality-index/211367",
    "ایلام": "https://www.accuweather.com/fa/ir/ilam/208937/air-quality-index/208937",
    "بوشهر": "https://www.accuweather.com/fa/ir/bandar-bushehr/207502/air-quality-index/207502",
    "تهران": "https://www.accuweather.com/fa/ir/tehran/210841/air-quality-index/210841",
    "چهارمحال و بختیاری": "https://www.accuweather.com/fa/ir/shahr-e-kord/207539/air-quality-index/207539",
    "خراسان جنوبی": "https://www.accuweather.com/fa/ir/birjand/209740/air-quality-index/209740",
    "خراسان رضوی": "https://www.accuweather.com/fa/ir/mashhad/209737/air-quality-index/209737",
    "خراسان شمالی": "https://www.accuweather.com/fa/ir/bojnurd/209467/air-quality-index/209467",
    "خوزستان": "https://www.accuweather.com/fa/ir/ahvaz/210047/air-quality-index/210047",
    "زنجان": "https://www.accuweather.com/fa/ir/zanjan/211728/air-quality-index/211728",
    "سمنان": "https://www.accuweather.com/fa/ir/semnan/210904/air-quality-index/210904",
    "سیستان و بلوچستان": "https://www.accuweather.com/fa/ir/zahedan/211207/air-quality-index/211207",
    "فارس": "https://www.accuweather.com/fa/ir/shiraz/208538/air-quality-index/208538",
    "قزوین": "https://www.accuweather.com/fa/ir/qazvin/210816/air-quality-index/210816",
    "قم": "https://www.accuweather.com/fa/ir/qom/210842/air-quality-index/210842",
    "کردستان": "https://www.accuweather.com/fa/ir/sanandaj/210185/air-quality-index/210185",
    "کرمان": "https://www.accuweather.com/fa/ir/kerman/209375/air-quality-index/209375",
    "کرمانشاه": "https://www.accuweather.com/fa/ir/kermanshah/209439/air-quality-index/209439",
    "کهگیلویه و بویراحمد": "https://www.accuweather.com/fa/ir/yasuj/210096/air-quality-index/210096",
    "گلستان": "https://www.accuweather.com/fa/ir/gorgan/208708/air-quality-index/208708",
    "گیلان": "https://www.accuweather.com/fa/ir/rasht/208612/air-quality-index/208612",
    "لرستان": "https://www.accuweather.com/fa/ir/khorramabad/210291/air-quality-index/210291",
    "مازندران": "https://www.accuweather.com/fa/ir/sari/210584/air-quality-index/210584",
    "مرکزی": "https://www.accuweather.com/fa/ir/arak/210434/air-quality-index/210434",
    "هرمزگان": "https://www.accuweather.com/fa/ir/bandar-abbas/208929/air-quality-index/208929",
    "همدان": "https://www.accuweather.com/fa/ir/hamedan/208760/air-quality-index/208760",
    "یزد": "https://www.accuweather.com/fa/ir/yazd/211668/air-quality-index/211668"
    }

    weather_urls = {
    "آذربایجان شرقی": "https://www.accuweather.com/fa/ir/tabriz/207308/weather-forecast/207308",
    "آذربایجان غربی": "https://www.accuweather.com/fa/ir/urmia/207147/weather-forecast/207147",
    "اردبیل": "https://www.accuweather.com/fa/ir/ardabil/206976/weather-forecast/206976",
    "اصفهان": "https://www.accuweather.com/fa/ir/isfahan/208194/weather-forecast/208194",
    "البرز": "https://www.accuweather.com/fa/ir/karaj/211367/weather-forecast/211367",
    "ایلام": "https://www.accuweather.com/fa/ir/ilam/208937/weather-forecast/208937",
    "بوشهر": "https://www.accuweather.com/fa/ir/bandar-bushehr/207502/weather-forecast/207502",
    "تهران": "https://www.accuweather.com/fa/ir/tehran/210841/weather-forecast/210841",
    "چهارمحال و بختیاری": "https://www.accuweather.com/fa/ir/shahr-e-kord/207539/weather-forecast/207539",
    "خراسان جنوبی": "https://www.accuweather.com/fa/ir/birjand/209740/weather-forecast/209740",
    "خراسان رضوی": "https://www.accuweather.com/fa/ir/mashhad/209737/weather-forecast/209737",
    "خراسان شمالی": "https://www.accuweather.com/fa/ir/bojnurd/209467/weather-forecast/209467",
    "خوزستان": "https://www.accuweather.com/fa/ir/ahvaz/210047/weather-forecast/210047",
    "زنجان": "https://www.accuweather.com/fa/ir/zanjan/211728/weather-forecast/211728",
    "سمنان": "https://www.accuweather.com/fa/ir/semnan/210904/weather-forecast/210904",
    "سیستان و بلوچستان": "https://www.accuweather.com/fa/ir/zahedan/211207/weather-forecast/211207",
    "فارس": "https://www.accuweather.com/fa/ir/shiraz/208538/weather-forecast/208538",
    "قزوین": "https://www.accuweather.com/fa/ir/qazvin/210816/weather-forecast/210816",
    "قم": "https://www.accuweather.com/fa/ir/qom/210842/weather-forecast/210842",
    "کردستان": "https://www.accuweather.com/fa/ir/sanandaj/210185/weather-forecast/210185",
    "کرمان": "https://www.accuweather.com/fa/ir/kerman/209375/weather-forecast/209375",
    "کرمانشاه": "https://www.accuweather.com/fa/ir/kermanshah/209439/weather-forecast/209439",
    "کهگیلویه و بویراحمد": "https://www.accuweather.com/fa/ir/yasuj/210096/weather-forecast/210096",
    "گلستان": "https://www.accuweather.com/fa/ir/gorgan/208708/weather-forecast/208708",
    "گیلان": "https://www.accuweather.com/fa/ir/rasht/208612/weather-forecast/208612",
    "لرستان": "https://www.accuweather.com/fa/ir/khorramabad/210291/weather-forecast/210291",
    "مازندران": "https://www.accuweather.com/fa/ir/sari/210584/weather-forecast/210584",
    "مرکزی": "https://www.accuweather.com/fa/ir/arak/210434/weather-forecast/210434",
    "هرمزگان": "https://www.accuweather.com/fa/ir/bandar-abbas/208929/weather-forecast/208929",
    "همدان": "https://www.accuweather.com/fa/ir/hamedan/208760/weather-forecast/208760",
    "یزد": "https://www.accuweather.com/fa/ir/yazd/211668/weather-forecast/211668"
    }

    health_activities = {
    "آذربایجان شرقی": "https://www.accuweather.com/fa/ir/tabriz/207308/health-activities/207308",
    "آذربایجان غربی": "https://www.accuweather.com/fa/ir/urmia/207147/health-activities/207147",
    "اردبیل": "https://www.accuweather.com/fa/ir/ardabil/206976/health-activities/206976",
    "اصفهان": "https://www.accuweather.com/fa/ir/isfahan/208194/health-activities/208194",
    "البرز": "https://www.accuweather.com/fa/ir/karaj/211367/health-activities/211367",
    "ایلام": "https://www.accuweather.com/fa/ir/ilam/208937/health-activities/208937",
    "بوشهر": "https://www.accuweather.com/fa/ir/bandar-bushehr/207502/health-activities/207502",
    "تهران": "https://www.accuweather.com/fa/ir/tehran/210841/health-activities/210841",
    "چهارمحال و بختیاری": "https://www.accuweather.com/fa/ir/shahr-e-kord/207539/health-activities/207539",
    "خراسان جنوبی": "https://www.accuweather.com/fa/ir/birjand/209740/health-activities/209740",
    "خراسان رضوی": "https://www.accuweather.com/fa/ir/mashhad/209737/health-activities/209737",
    "خراسان شمالی": "https://www.accuweather.com/fa/ir/bojnurd/209467/health-activities/209467",
    "خوزستان": "https://www.accuweather.com/fa/ir/ahvaz/210047/health-activities/210047",
    "زنجان": "https://www.accuweather.com/fa/ir/zanjan/211728/health-activities/211728",
    "سمنان": "https://www.accuweather.com/fa/ir/semnan/210904/health-activities/210904",
    "سیستان و بلوچستان": "https://www.accuweather.com/fa/ir/zahedan/211207/health-activities/211207",
    "فارس": "https://www.accuweather.com/fa/ir/shiraz/208538/health-activities/208538",
    "قزوین": "https://www.accuweather.com/fa/ir/qazvin/210816/health-activities/210816",
    "قم": "https://www.accuweather.com/fa/ir/qom/210842/health-activities/210842",
    "کردستان": "https://www.accuweather.com/fa/ir/sanandaj/210185/health-activities/210185",
    "کرمان": "https://www.accuweather.com/fa/ir/kerman/209375/health-activities/209375",
    "کرمانشاه": "https://www.accuweather.com/fa/ir/kermanshah/209439/health-activities/209439",
    "کهگیلویه و بویراحمد": "https://www.accuweather.com/fa/ir/yasuj/210096/health-activities/210096",
    "گلستان": "https://www.accuweather.com/fa/ir/gorgan/208708/health-activities/208708",
    "گیلان": "https://www.accuweather.com/fa/ir/rasht/208612/health-activities/208612",
    "لرستان": "https://www.accuweather.com/fa/ir/khorramabad/210291/health-activities/210291",
    "مازندران": "https://www.accuweather.com/fa/ir/sari/210584/health-activities/210584",
    "مرکزی": "https://www.accuweather.com/fa/ir/arak/210434/health-activities/210434",
    "هرمزگان": "https://www.accuweather.com/fa/ir/bandar-abbas/208929/health-activities/208929",
    "همدان": "https://www.accuweather.com/fa/ir/hamedan/208760/health-activities/208760",
    "یزد": "https://www.accuweather.com/fa/ir/yazd/211668/health-activities/211668"
    }

    daily_weather = {
    "آذربایجان شرقی": "https://www.accuweather.com/fa/ir/tabriz/207308/daily-weather-forecast/207308",
    "آذربایجان غربی": "https://www.accuweather.com/fa/ir/urmia/207147/daily-weather-forecast/207147",
    "اردبیل": "https://www.accuweather.com/fa/ir/ardabil/206976/daily-weather-forecast/206976",
    "اصفهان": "https://www.accuweather.com/fa/ir/isfahan/208194/daily-weather-forecast/208194",
    "البرز": "https://www.accuweather.com/fa/ir/karaj/211367/daily-weather-forecast/211367",
    "ایلام": "https://www.accuweather.com/fa/ir/ilam/208937/daily-weather-forecast/208937",
    "بوشهر": "https://www.accuweather.com/fa/ir/bandar-bushehr/207502/daily-weather-forecast/207502",
    "تهران": "https://www.accuweather.com/fa/ir/tehran/210841/daily-weather-forecast/210841",
    "چهارمحال و بختیاری": "https://www.accuweather.com/fa/ir/shahr-e-kord/207539/daily-weather-forecast/207539",
    "خراسان جنوبی": "https://www.accuweather.com/fa/ir/birjand/209740/daily-weather-forecast/209740",
    "خراسان رضوی": "https://www.accuweather.com/fa/ir/mashhad/209737/daily-weather-forecast/209737",
    "خراسان شمالی": "https://www.accuweather.com/fa/ir/bojnurd/209467/daily-weather-forecast/209467",
    "خوزستان": "https://www.accuweather.com/fa/ir/ahvaz/210047/daily-weather-forecast/210047",
    "زنجان": "https://www.accuweather.com/fa/ir/zanjan/211728/daily-weather-forecast/211728",
    "سمنان": "https://www.accuweather.com/fa/ir/semnan/210904/daily-weather-forecast/210904",
    "سیستان و بلوچستان": "https://www.accuweather.com/fa/ir/zahedan/211207/daily-weather-forecast/211207",
    "فارس": "https://www.accuweather.com/fa/ir/shiraz/208538/daily-weather-forecast/208538",
    "قزوین": "https://www.accuweather.com/fa/ir/qazvin/210816/daily-weather-forecast/210816",
    "قم": "https://www.accuweather.com/fa/ir/qom/210842/daily-weather-forecast/210842",
    "کردستان": "https://www.accuweather.com/fa/ir/sanandaj/210185/daily-weather-forecast/210185",
    "کرمان": "https://www.accuweather.com/fa/ir/kerman/209375/daily-weather-forecast/209375",
    "کرمانشاه": "https://www.accuweather.com/fa/ir/kermanshah/209439/daily-weather-forecast/209439",
    "کهگیلویه و بویراحمد": "https://www.accuweather.com/fa/ir/yasuj/210096/daily-weather-forecast/210096",
    "گلستان": "https://www.accuweather.com/fa/ir/gorgan/208708/daily-weather-forecast/208708",
    "گیلان": "https://www.accuweather.com/fa/ir/rasht/208612/daily-weather-forecast/208612",
    "لرستان": "https://www.accuweather.com/fa/ir/khorramabad/210291/daily-weather-forecast/210291",
    "مازندران": "https://www.accuweather.com/fa/ir/sari/210584/daily-weather-forecast/210584",
    "مرکزی": "https://www.accuweather.com/fa/ir/arak/210434/daily-weather-forecast/210434",
    "هرمزگان": "https://www.accuweather.com/fa/ir/bandar-abbas/208929/daily-weather-forecast/208929",
    "همدان": "https://www.accuweather.com/fa/ir/hamedan/208760/daily-weather-forecast/208760",
    "یزد": "https://www.accuweather.com/fa/ir/yazd/211668/daily-weather-forecast/211668"
    }

    @classmethod
    def get_supported_cities(cls):
        """دریافت لیست شهرهای پشتیبانی‌شده"""
        return list(cls.weather_urls.keys())


    @classmethod
    def get_daily_weather_info(cls,city_name, target_date):
        """دریافت اطلاعات آب و هوایی یک شهر"""
        url = cls.daily_weather.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return "خطا در دریافت اطلاعات از سایت"

        soup = BeautifulSoup(response.text, "html.parser")

        daily_cards = soup.find_all("div", class_="daily-wrapper")

        for card in daily_cards:
            date_element = card.find("span", class_="module-header sub date")
            if date_element and date_element.text.strip() == target_date:
                high_temp = card.find("span", class_="high").text.strip()
                low_temp = card.find("span", class_="low").text.strip()
                precip = card.find("div", class_="precip").text.strip()
                condition = card.find("div", class_="phrase").text.strip()

                wind_speed = "نامشخص"
                panel_items = card.find_all("p", class_="panel-item")

                for item in panel_items:
                    if "باد" in item.text:
                        wind_speed = item.text.replace("باد", "").strip()
                        break


                return {
                    "تاریخ": target_date,
                    "دمای بالا": high_temp,
                    "دمای پایین": low_temp,
                    "احتمال بارش": precip,
                    "وضعیت هوا": condition,
                    "سرعت باد": wind_speed
                }

        return "تاریخ موردنظر یافت نشد."


    @classmethod
    def get_temperature(cls, city_name):
        """دریافت دمای کنونی یک شهر"""
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            temp_tag = soup.find(class_='temp')
            return temp_tag.text.strip() if temp_tag else "دما یافت نشد."
        else:
            return f"خطا در دریافت صفحه: {response.status_code}"

    @classmethod
    def get_realfeel(cls, city_name):
        """دریافت دمای احساسی (RealFeel) یک شهر"""
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            return f"⚠️ خطا در دریافت صفحه: {e}"

        soup = BeautifulSoup(response.text, 'html.parser')

        realfeel_div = soup.find('div', class_='real-feel')
    
        if realfeel_div:
            realfeel_text = realfeel_div.get_text(strip=True)  
            realfeel_value = realfeel_text.replace("RealFeel®", "").strip()  
            return f"{realfeel_value}"
    
        return "⚠️ اطلاعات دمای احساسی یافت نشد."    
    @classmethod
    def get_wind(cls,city_name):
        '''دریافت سرعت باد یک شهر'''
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            wind_label = soup.find('span', class_='label', string='باد')
            if wind_label:
                value_tag = wind_label.find_next('span', class_='value')
                if value_tag:
                    return value_tag.text.strip()
                else:
                    return "نمیدونم"
            else:
                return "نمیدونم"
        else:
            return f"خطا در دریافت صفحه: {response.status_code}"
    
    @classmethod
    def get_air_quality(cls,city_name):
        '''دریافت کیفیت هوا یک شهر'''
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            air_quality_label = soup.find('span', class_='label', string='کیفیت هوا')
            if air_quality_label:
                value_tag = air_quality_label.find_next('span', class_='value')
                if value_tag:
                    return value_tag.text.strip()
                else:
                    return "مقدار کیفیت هوا پیدا نشد."
            else:
                return "برچسب 'کیفیت هوا' پیدا نشد."
        else:
            return f"خطا در دریافت صفحه: {response.status_code}"


    @classmethod
    def get_radar_image_link(cls,city_name):
        """دریافت لینک تصویر رادار یک شهر"""
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            radar_link_tag = soup.find("a", class_="base-map-cta card static-radar-map-recommended")
            if radar_link_tag:
                img_tag = radar_link_tag.find("img")
                if img_tag:
                    image_url = img_tag.get("data-src")
                    if image_url:
                        random_param = f"?t={int(time.time())}_{random.randint(1000, 9999)}"
                        return image_url + random_param 
                    else:
                        return "مقدار data-src یافت نشد."
                else:
                    return "تگ <img> یافت نشد."
            else:
                return "تگ <a> مورد نظر یافت نشد."
        else:
            return f"خطا در بارگذاری صفحه: {response.status_code}"

    @classmethod
    def get_sun_times(cls,city_name):
        '''دریافت زمان خروج و ورود خورشید و ماه یک شهر'''
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()   

            soup = BeautifulSoup(response.text, 'html.parser')

            items = soup.find_all('div', class_='sunrise-sunset__item')

            sun_times = {}

            for item in items:
                phrase = item.find('span', class_='sunrise-sunset__phrase').text.strip() 
            
                if "ساعت" in phrase:  
                    times = item.find('div', class_='sunrise-sunset__times')

                    if times:
                        time_items = times.find_all('div', class_='sunrise-sunset__times-item')
                        time_dict = {}

                        for time_item in time_items:
                            label = time_item.find('span', class_='sunrise-sunset__times-label').text.strip()
                            value = time_item.find('span', class_='sunrise-sunset__times-value').text.strip()
                            time_dict[label] = value

                        sun_times[phrase] = time_dict

            return sun_times

        except requests.exceptions.RequestException as e:
            return f"خطا در دریافت صفحه: {e}"

    @classmethod
    def get_weather_forecast(cls,city_name):
        '''دریافت اب هوا برای چند روز'''
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
    
        headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0"
        }

        response = requests.get(url,headers=headers)
        response.raise_for_status() 

        soup = BeautifulSoup(response.text, 'html.parser')

        daily_list = soup.find('div', class_='daily-list content-module')

        daily_items = daily_list.find_all('a', class_='daily-list-item')

        forecast_data = []   

        for item in daily_items:
            date = item.find('div', class_='date').get_text(strip=True)
            temp_hi = item.find('span', class_='temp-hi').get_text(strip=True)
            temp_lo = item.find('span', class_='temp-lo').get_text(strip=True)
            icon_url = item.find('img', class_='icon')['src']
        
            forecast_data.append({
                "تاریخ": date,
                "دمای بالا": temp_hi,
                "دمای پایین": temp_lo,
                "آیکن وضعیت آب و هوا": icon_url
            })

        return forecast_data

    @classmethod
    def get_dust_dander_data(cls,city_name):
        '''دریافت اطلاعات گرد و غبار و درمان آن'''
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
        response = requests.get(url, headers=headers)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            dust_dander_section = soup.find('a', {'data-slug': 'dust-dander'})
        
            if dust_dander_section:
                name = dust_dander_section.find('span', class_='health-activities__item__name').text.strip()
                category = dust_dander_section.find('span', class_='health-activities__item__category').text.strip()
                unsupported_category = dust_dander_section.find('span', class_='health-activities__item__category__unsupported').text.strip()

                return {
                    'name': name,
                    'category': category,
                    'unsupported_category': unsupported_category
                }
            else:
                return "داده‌ها پیدا نشدند"
        else:
            return f"خطا در بارگذاری صفحه: {response.status_code}"

    @classmethod
    def get_title(cls,city_name):
        '''دریافت عنوان شهر'''
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
        response = requests.get(url, headers=headers)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
        
            title = soup.find("title")

            if title:
                return title.text
            else:
                return "نمیدونم"
        else:
            return f"خطا در دریافت صفحه: {response.status_code}"
  
    @classmethod    
    def get_forecast_details(cls,city_name):
        '''دریافت پیش بینی اب هوا'''
        url = cls.weather_urls.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            forecast_link = soup.find("a", class_="local-forecast-summary")
            
            if forecast_link:
                forecast_title = forecast_link.find("h2").text if forecast_link.find("h2") else "عنوان پیدا نشد"
                forecast_description = forecast_link.find("p").text if forecast_link.find("p") else "توضیح پیدا نشد"
                
                return forecast_title, forecast_description
            else:
                return "خبر ندارم", ""
        else:
            return "درخواست ناموفق بود", ""


    @classmethod
    def get_air_quality_aqi(cls,city_name):
        '''دریافت اطلاعات میزان شاخص الودگی هوا'''
        url = cls.air.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            air_quality_div = soup.find('div', class_='aq-number-wrapper')
            air_quality_details = soup.find('h3', class_='air-quality-data')

            if air_quality_div and air_quality_details:
                air_quality_value = air_quality_div.find('div', class_='aq-number').text.strip()
                unit = air_quality_div.find('div', class_='aq-unit').text.strip()

                category_text = air_quality_details.find('p', class_='category-text').text.strip()
                statement = air_quality_details.find('p', class_='statement').text.strip()

                return air_quality_value, unit, category_text, statement
            else:
                return None, None, "شاخص کیفیت هوا یافت نشد", "توضیحات یافت نشد"
        else:
            return None, None, f"خطا در دریافت داده‌ها: {response.status_code}", "توضیحات یافت نشد"

    @classmethod
    def get_weather_forecast_air_aqi(cls,city_name):
        '''دریافت اطلاعات الودگی برای چند روز'''
        url = cls.air.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        daily_forecast = soup.find_all('div', class_='air-quality-content')

        forecast_data = []

        for day in daily_forecast:
            day_of_week = day.find('p', class_='day-of-week').text.strip()
            date = day.find('p', class_='date').text.strip()
            aqi = day.find('div', class_='aq-number').text.strip()

            forecast_data.append({
                'day_of_week': day_of_week,
                'date': date,
                'aqi': aqi
            })

        return forecast_data    
    
    @classmethod    
    def get_health_activities(cls,city_name):
        url = cls.health_activities.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)
    
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            health_cards = soup.find_all('a', class_='index-list-card')

            if not health_cards:
                return "هیچ اطلاعاتی یافت نشد."

            results = []
            for card in health_cards:
                title_tag = card.find('div', class_='index-name')
                status_tag = card.find('div', class_='index-status-text')

                if title_tag and status_tag:
                    title = title_tag.text.strip()
                    status = status_tag.text.strip()
                    results.append(f"{title}: {status}")

            return results
    
        else:
            return f"خطا در دریافت صفحه: {response.status_code}"

    @classmethod
    def download_specific_image(cls,url = "https://www.havajanah.ir/"):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url,headers=headers)
            response.raise_for_status()  

            soup = BeautifulSoup(response.text, 'html.parser')

            img_tag = soup.find('img', alt="تصویر ماهواره ای متحرک")

            if img_tag and 'src' in img_tag.attrs:
                gif_url = img_tag['src']
                gif_url = urljoin(url, gif_url)    
                return gif_url
            else:
                return "تگ img یا لینک src یافت نشد."
            
        except requests.exceptions.RequestException as e:
            print(f"Erorr: {e}")

    @classmethod
    def get_pollutant_info(cls, city_name):
        '''دریافت اطلاعات گوگرد دی اکسید و گوگرد دی اکسید'''
        url = cls.air.get(city_name)
        if not url:
            return "شهر مورد نظر پیدا نشد."
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            pollutants = soup.find_all('div', class_='air-quality-pollutant')
            
            pollutant_info = {}
            
            for pollutant in pollutants:
                pollutant_name = pollutant.find('h3').text.strip()
                
                concentration = pollutant.find('div', class_='pollutant-concentration').text.strip()
                
                statement = pollutant.find('div', class_='statement').text.strip()
                
                pollutant_info[pollutant_name] = {
                    'concentration': concentration,
                    'statement': statement
                }
                
            return pollutant_info
        else:
            return f"خطا در درخواست: {response.status_code}"

    @classmethod
    def get_earth_satellite_image_url(cls):
        url = 'https://www.havajanah.ir/sat-pic/%d8%aa%d8%b5%d9%88%db%8c%d8%b1-%d8%a8%d8%a7%da%a9%db%8c%d9%81%db%8c%d8%aa-%d9%88-%d9%88%d8%a7%d9%82%d8%b9%db%8c-%da%a9%d8%b1%d9%87-%d8%b2%d9%85%db%8c%d9%86/'  
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            image_div = soup.find('div', class_='wp-caption aligncenter')

            if image_div:  
                image_tag = image_div.find('img')
                if image_tag:
                    return image_tag['src']
                else:
                    return "تصویر پیدا نشد"
            else:
                return "تگ div با کلاس 'wp-caption aligncenter' پیدا نشد"
        else:
            return f"خطا در درخواست: {response.status_code}"
