import os
import re
from datetime import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from python3_anticaptcha import ImageToTextTask
import shutil
from selenium.webdriver.chrome.options import Options
import bank_statement_downloader
import argparse
from selenium.webdriver.common.keys import Keys

'" Код для автоматического ввода с командной строки '''
''' Вводится команда: python bank_statement_downloader.py --sort_order 2 --date_filter 5 --date_from 19.04.2023 --date_to 20.04.2023 --path_comp C:/ <адрес получения отчета>
'''
''' Три вида сортировки --sort_order '''
'''Пять видов фильтров  --date_filter'''
''' При вводе фильтра номер 5, вводится  даты в таком формате: --date_from 19.04.2023 --date_to 20.04.2023  '''





def validate_date(date):
    try:
        datetime.strptime(date, '%d.%m.%Y')
        return True
    except ValueError:
        return False

def parse_arguments():
    parser = argparse.ArgumentParser(description='Download bank statement with specified filters and sorting.')
    parser.add_argument('--sort_order', type=int, required=True, choices=[1, 2, 3], help='Sorting option (1-3)')
    parser.add_argument('--date_filter', type=int, required=True, choices=[1, 2, 3, 4, 5],
                        help='Date filter option (1-5)')
    parser.add_argument('--date_from', type=str, help='Starting date for period filter (format: dd.mm.yyyy)')
    parser.add_argument('--date_to', type=str, help='Ending date for period filter (format: dd.mm.yyyy)')
    parser.add_argument('--path_comp', type=str, required=True,
                        help='Destination folder path for downloaded statement')


    args = parser.parse_args()
    sort = {'sort_order': args.sort_order}

    if args.date_filter == 5:
        if not args.date_from or not args.date_to:
            parser.error('Both --date_from and --date_to should be provided when --date_filter is set to 5.')

    return args, sort
def Param_filter(driver, sort, args):
    sort_order = int(sort['sort_order'])
    sort_dropdown = driver.find_element(By.XPATH,
                                        '//span[@class="k-dropdown-wrap k-state-default"]//span[@aria-label="select"]')
    sort_dropdown.click()
    time.sleep(1)

    if sort_order == 1:
        sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по сумме (в рамках одного дня)")])[1]')
    elif sort_order == 2:
        sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по дате и времени операции")])[1]')
    elif sort_order == 3:
        sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по сумме (за весь период)")])[1]')
    else:
        raise ValueError(f"Invalid sort option: {sort_order}")

    sort_option.click()


    if args.date_filter == 1:
        period_filter = wait.until(EC.presence_of_element_located((By.XPATH, '(//input[@id="Periods_Today"])[1]')))
        period_filter.click()
    elif args.date_filter == 2:
        period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Yesterday"])[1]')
        period_filter.click()
    elif args.date_filter == 3:
        period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Week"])[1]')
        period_filter.click()
    elif args.date_filter == 4:
        period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Month"])[1]')
        period_filter.click()
    elif args.date_filter == 5:
        period_filter = driver.find_element(By.XPATH, '//input[@id="Periods_Period"]')
        period_filter.click()
        time.sleep(5)

        date_from_input = driver.find_element(By.XPATH, '//input[@id="DateFrom"]')
        date_from_input.clear()
        date_from_input.click()
        date_from_input.send_keys(Keys.HOME + args.date_from)
        time.sleep(5)

        date_to_input = driver.find_element(By.XPATH, '//input[@id="DateTo"]')
        date_to_input.clear()
        date_to_input.click()
        date_to_input.send_keys(Keys.HOME + args.date_to)
        time.sleep(5)

def solve_captcha(api_key, image_path):
    anticaptcha_client = ImageToTextTask.ImageToTextTask(anticaptcha_key=api_key)
    captcha_response = anticaptcha_client.captcha_handler(captcha_file=image_path)
    return captcha_response.get("solution").get("text")

load_dotenv()
API_KEY = os.getenv("ANTICAPTCHA_API_KEY")
USERNAME = 'u'
PASSWORD = 'q'
CHROME_DRIVER_PATH = '"C:\WebDriver\chromedriver.exe"'
chrome_service = Service(executable_path=CHROME_DRIVER_PATH)

if __name__ == '__main__':
    args, sort = parse_arguments()

    # Initialize the Chrome WebDriver with custom settings
    chrome_options = Options()
    prefs = {
        "download.default_directory": args.path_comp,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to the website and log in
    driver.get('https://st.bnb.by/')
    username_input = driver.find_element(By.CSS_SELECTOR, 'input[name="UserName"]')
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="Password"]')
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)
    captcha_solved = False
    attempts = 0

    while not captcha_solved and attempts < 3:
        captcha_image = driver.find_element(By.CSS_SELECTOR, '#divRefresh')
        captcha_image.screenshot("captcha.png")
        captcha_solution = solve_captcha(API_KEY, "captcha.png")
        captcha_input = driver.find_element(By.CSS_SELECTOR, '#Captcha_Text')
        captcha_input.clear()
        captcha_input.send_keys(captcha_solution)



        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()
        try:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.k-window-actions')))
            close_buttons = driver.find_elements(By.CSS_SELECTOR, '.k-window-actions')
            close_buttons[0].click()
            captcha_solved = True
        except:
            try:
                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.header__client-name')))
                captcha_solved = True
            except:
                attempts += 1
                print("Неверная капча, попробуйте еще раз.")
                captcha_solved = False

    if attempts >= 3:
        print("Превышено количество попыток решения капчи. Завершение работы.")
        driver.quit()

    statement_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//a[@href="#"]//i[@class="fa fa-inbox"]')))
    statement_button.click()
    statement_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#"]//span[@class="menu-item-parent"][contains(text(),"Выписка")]')))
    statement_button.click()
    time.sleep(5)
    period_statement_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Выписка за период")]')))
    period_statement_button.click()
    time.sleep(5)



    # Apply user-specified filters
    Param_filter(driver, sort, args)

    # Apply filters, download the statement, and exit
    apply_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(),'Применить')])[1]")))
    apply_button.click()

    # Переход на другую страницу, делаем паузу 3 сек
    time.sleep(5)

    # Кликаем
    dropdown_toggle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
        (By.XPATH, "(//a[@class='bia-grid-menu-action-items-group dropdown-toggle enabled'])[1]")))
    dropdown_toggle.click()

    # Затем кликаем "Экспорт СЭП"
    export_sep = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[1]")))
    export_sep.click()

    time.sleep(5)

    print(f"Ваш отчет готов, проверьте вашу папку по адресу = {args.path_comp}")
    driver.quit()

