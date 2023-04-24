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

'" Код для ручного ввода по запросу аргуменетов в терминале'''

def validate_date(date):
    try:
        datetime.strptime(date, '%d.%m.%Y')
        return True
    except ValueError:
        return False
def get_user_settings():
    settings = {}
    print('Выберите один из пяти фильтров по датам:')
    print('1. Выписка за сегодня')
    print('2. Выписка за вчера')
    print('3. Выписка за последние 7 дней')
    print('4. Выписка за предыдущий месяц')
    print('5. Выписка за период: с ... по ...')
    settings["date_filter"] = int(input())

    if settings["date_filter"] == 5:
        print('Введите дату начала периода (дд.мм.гггг):')
        settings["date_from"] = input()
        print('Введите дату окончания периода (дд.мм.гггг):')
        settings["date_to"] = input()

    # print('Как вы хотите отсортировать?')
    # print('1. Если по сумме (в рамках одного дня)')
    # print('2. Если по дате и времени операции')
    # print('3. Если по сумме (за весь период)')
    # settings["sort_order"] = int(input())

    print('Введите адрес папки на вашем компьютере куда будет отправлен отчет:')
    settings["path_comp"] = input()
    download_folder = settings["path_comp"]



    return settings, download_folder
settings, download_folder = get_user_settings()

chrome_options = Options()
prefs = {
    "download.default_directory": download_folder,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)

def Param_filter(driver, settings):
    wait = WebDriverWait(driver, 10)
    driver.save_screenshot('screenshot.png')

    if settings["date_filter"] == 1:
        period_filter = wait.until(EC.presence_of_element_located((By.XPATH, '(//input[@id="Periods_Today"])[1]')))
    elif settings["date_filter"] == 2:
        period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Yesterday"])[1]')
    elif settings["date_filter"] == 3:
        period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Week"])[1]')
    elif settings["date_filter"] == 4:
        period_filter = driver.find_element(By.XPATH, '(//input[@id="Periods_Month"])[1]')
    elif settings["date_filter"] == 5:
        period_filter = driver.find_element(By.XPATH, '//span[@class="nowrap"][contains(text(),"за период")]')
        date_from_input = driver.find_element(By.XPATH, '//input[@id="DateFrom"]')
        date_to_input = driver.find_element(By.XPATH, '//input[@id="DateTo"]')
        date_from_input.send_keys(settings["date_from"])
        date_to_input.send_keys(settings["date_to"])

    period_filter.click()
    # sort_dropdown = driver.find_element(By.XPATH, '//span[@class="k-input"]')
    # sort_dropdown.click()
    #
    # if settings["sort_order"] == 1:
    #     sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по сумме (в рамках одного дня)")])[1]')
    # elif settings["sort_order"] == 2:
    #     sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по дате и времени операции")])[1]')
    # elif settings["sort_order"] == 3:
    #     sort_option = driver.find_element(By.XPATH, '(//li[contains(text(),"по сумме (за весь период)")])[1]')
    #
    # sort_option.click()
driver = webdriver.Chrome()

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

driver.get('https://st.bnb.by/')

username_input = driver.find_element(By.CSS_SELECTOR, 'input[name="UserName"]')
password_input = driver.find_element(By.CSS_SELECTOR, 'input[name="Password"]')
username_input.send_keys(USERNAME)
password_input.send_keys(PASSWORD)
captcha_image = driver.find_element(By.CSS_SELECTOR, '#divRefresh')
captcha_image.screenshot("captcha.png")
captcha_solution = solve_captcha(API_KEY, "captcha.png")
captcha_input = driver.find_element(By.CSS_SELECTOR, '#Captcha_Text')
captcha_input.send_keys(captcha_solution)
login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
login_button.click()
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.header__client-name'))
)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.header__client-name'))
)
statement_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#"]//i[@class="fa fa-inbox"]')))
statement_button.click()

statement_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//a[@href="#"]//span[@class="menu-item-parent"][contains(text(),"Выписка")]')))
statement_button.click()
time.sleep(5)
period_statement_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//span[contains(text(),"Выписка за период")]')))
period_statement_button.click()
time.sleep(5)
Param_filter(driver, settings)


# Кликнуть на кнопку "Применить"
apply_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(),'Применить')])[1]")))
apply_button.click()
# Переход на другую страницу, делаем паузу 3 сек
time.sleep(5)
# Кликаем
dropdown_toggle = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "(//a[@class='bia-grid-menu-action-items-group dropdown-toggle enabled'])[1]")))
dropdown_toggle.click()
# Затем кликаем "Экспорт СЭП"
export_sep = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "(//span[contains(text(),'Экспорт СЭП')])[1]")))
export_sep.click()
time.sleep(5)

print(f"Ваш отчет готов, проверьте вашу папку по адресу = {settings['path_comp']}")
driver.quit()
