import os
import time

from dotenv import load_dotenv
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from webdriver_manager.chrome import ChromeDriverManager


def book():
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
        train_number = row.find_element(By.XPATH, './/div/a').text
        start_station = row.find_element(By.XPATH, './td[1]/div/div[2]/strong[1]').text
        to_station = row.find_element(By.XPATH, './td[1]/div/div[2]/strong[2]').text
        start_time = row.find_element(By.XPATH, './td[1]/div/div[3]/strong[1]').text
        to_time = row.find_element(By.XPATH, './td[1]/div/div[3]/strong[2]').text

        is_have = row.find_element(By.XPATH, f'./td[{os.environ.get("SEAT")}]').text
        got_travel = {
            'train_number': train_number,
            'start_station': start_station,
            'to_station': to_station,
            'start_time': start_time,
            'to_time': to_time,
            'is_have': is_have,
        }
        print(got_travel)
        travel_list.append(got_travel)
        # 订票
        if train_number == os.environ.get("TRAIN_NUM"):
            if is_have == '*':
                print('未开售')
                driver.find_element(By.ID, 'login_user').click()
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'center-welcome')))
                return False
            elif is_have == '候补':
                print('候补')
                row.find_element(By.XPATH, f'./td[{os.environ.get("SEAT")}]').click()
                try:
                    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, 'hbSubmit')))
                    driver.find_element(By.ID, 'hbSubmit').click()
                except TimeoutException:
                    driver.find_element(By.ID, 'login_user').click()
                    WebDriverWait(driver, 5).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, 'center-welcome')))
                    return False

                WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'is_open')))
                is_open = driver.find_element(By.ID, 'is_open')

                if is_open.find_element(By.XPATH, './span[2]').text == '已开启':
                    print('已开启无座候补')
                    is_open.find_element(By.XPATH, './span[1]/span').click()
                    print('已关闭无座候补')
                else:
                    print('已关闭无座候补')

                choices = driver.find_elements(By.XPATH, '//*[@class="passenger-list-box"]/ul/li')
                for choice in choices:
                    person = choice.find_element(By.XPATH, './label').text
                    if person in os.environ.get("PASSENGERS"):
                        choice.find_element(By.XPATH, './label/div/ins').click()

                WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, 'btn-primary')))
                driver.find_element(By.CLASS_NAME, 'btn-primary').click()
                WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, 'modal-ft')))
                driver.find_element(By.CLASS_NAME, 'modal-ft').find_element(By.XPATH, './a[2]').click()
                return True
            else:
                print(f'还有{is_have}张票')
                row.find_element(By.CLASS_NAME, 'btn72').click()

                try:
                    WebDriverWait(driver, 2).until(
                        EC.visibility_of_element_located((By.ID, 'login_close')))
                    if driver.find_elements(By.ID, 'login_close'):
                        driver.find_element(By.ID, 'login_close').click()
                        driver.find_element(By.ID, 'login_user').click()
                        WebDriverWait(driver, 5).until(
                            EC.visibility_of_element_located((By.CLASS_NAME, 'center-welcome')))
                        return False
                except TimeoutException:
                    pass

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
                        try:
                            seat_select.select_by_value('4')
                        except NoSuchElementException:
                            continue

                # 下单
                driver.find_element(By.XPATH, '//a[text()="提交订单"]').click()
                WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'qr_submit_id')))
                driver.find_element(By.ID, 'qr_submit_id').click()
                return True


if __name__ == '__main__':
    load_dotenv()
    service = Service(executable_path=f'{os.environ.get("WEBDRIVER_PATH")}')
    options = ChromeOptions()
    # 调试已经存在的Chrome浏览器，否则会新建一个浏览器，导致登录失效
    options.debugger_address = '127.0.0.1:19222'
    # driver = Chrome(options=options, service=service)
    driver = Chrome(options=options, service=Service(ChromeDriverManager().install()))

    while True:
        if book():
            break

    time.sleep(12000)
    driver.close()
