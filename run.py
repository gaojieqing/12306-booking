import os
import time

from dotenv import load_dotenv
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

load_dotenv()
service = Service(executable_path=f'{os.environ.get("WEBDRIVER_PATH")}')
options = ChromeOptions()
# 调试已经存在的Chrome浏览器，否则会新建一个浏览器，导致登录失效
options.debugger_address = '127.0.0.1:19222'
driver = Chrome(options=options, service=service)

# 查票
driver.get(
    f'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs={os.environ.get("FROM_STATION")},'
    f'{os.environ.get("FROM_STATION_PINYIN")}&ts={os.environ.get("TO_STATION")},{os.environ.get("TO_STATION_PINYIN")}'
    f'&date={os.environ.get("TRAIN_DATE")}&flag=N,N,Y')
WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="t-list"]/table/tbody/tr')))
rows = driver.find_elements(By.XPATH, '//*[@id="t-list"]/table/tbody/tr')
travel_list = []
for row in rows:
    if row.get_attribute('style') == 'display: none;':
        continue
    car_number = row.find_element(By.XPATH, './/div/a').text
    start_station = row.find_element(By.XPATH, './td[1]/div/div[2]/strong[1]').text
    to_station = row.find_element(By.XPATH, './td[1]/div/div[2]/strong[2]').text
    start_time = row.find_element(By.XPATH, './td[1]/div/div[3]/strong[1]').text
    to_time = row.find_element(By.XPATH, './td[1]/div/div[3]/strong[2]').text

    is_have = row.find_element(By.XPATH, f'./td[{os.environ.get("SEAT")}]').text
    got_travel = {
        'car_number': car_number,
        'start_station': start_station,
        'to_station': to_station,
        'start_time': start_time,
        'to_time': to_time,
        'is_have': is_have,
    }
    print(got_travel)
    travel_list.append(got_travel)
    # 订票
    if start_station == os.environ.get("FROM_STATION") and to_station == os.environ.get("TO_STATION") and \
            start_time == os.environ.get("START_TIME") and to_time == os.environ.get("TO_TIME") and is_have != '候补':
        row.find_element(By.CLASS_NAME, 'btn72').click()
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="normal_passenger_id"]/li')))
        choices = driver.find_elements(By.XPATH, '//*[@id="normal_passenger_id"]/li')
        for choice in choices:
            person = choice.find_element(By.XPATH, './label').text
            if person in os.environ.get("PASSENGERS"):
                choice.find_element(By.XPATH, './input').click()

        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH,
                                                                          '//*[@id="ticketInfo_id"]/tr')))
        tickets = driver.find_elements(By.XPATH, '//*[@id="ticketInfo_id"]/tr')
        for ticket in tickets:
            seats = ticket.find_elements(By.XPATH, './td[3]/select')
            if seats:
                seat_select = Select(seats[0])
                seat_select.select_by_value('4')

        # 下单
        driver.find_element(By.XPATH, '//a[text()="提交订单"]').click()
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'qr_submit_id')))
        # driver.find_element(By.ID, 'qr_submit_id').click()
        break

time.sleep(12000)
driver.close()
