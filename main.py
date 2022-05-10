import ddddocr
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from os.path import exists
import json
import datetime
import time
from discord import Webhook, RequestsWebhookAdapter # Importing discord.Webhook and discord.RequestsWebhookAdapter

print('臺大醫院掛號預約程式啟動中')

configPath = "config.json"
if not exists(configPath):
    print("請先設定掛號資料再開啟此程式")
    exit()

with open(configPath, newline='') as jsonfile:
    config = json.load(jsonfile)

chrome_options = Options() 
chrome_options.add_argument('--headless')  # 啟動無頭模式
chrome_options.add_argument('--disable-gpu')#規避google bug
url = config["pageURL"]
executable_path = 'chromedriver.exe'#自行設定路徑
driver = webdriver.Chrome(executable_path=executable_path,
chrome_options=chrome_options)
driver.get(url)
while True:
    link = None
    while not link:
        try:
            link = driver.find_element_by_link_text('掛號') # driver.find_elements_by_link_text('掛號')[-1] 從最後一個開始找
        except:
            print(('目前沒有可掛號時間，現在時間：%s       ' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), end='\r')
            driver.get(url)
            time.sleep(5)

    try:
        link.click()
        print('開始預約以下時段')
        idShowTime=driver.find_element_by_id('ShowTime')
        idShowDept=driver.find_element_by_id('ShowDept')
        idShowClinic=driver.find_element_by_id('ShowClinic')
        idShowDt=driver.find_element_by_id('ShowDt')
        idShowLoc=driver.find_element_by_id('ShowLoc')

        print("時間：" + idShowTime.text)
        print("科別：" + idShowDept.text)
        print("診別：" + idShowClinic.text)
        print("醫事人員：" + idShowDt.text)
        print("看診地點：" + idShowLoc.text)

        # 勾選身分證
        driver.find_element_by_css_selector("input[type='radio'][value='0']").click()

        # 身分證
        idText=driver.find_element_by_id('txtIuputID')
        idText.send_keys(config["id"])

        # 出生年
        selectYear = Select(driver.find_element_by_id('ddlBirthYear'))
        selectYear.select_by_visible_text(config["birthYear"])

        # 出生月
        selectYear = Select(driver.find_element_by_id('ddlBirthMonth'))
        selectYear.select_by_visible_text(config["birthMonth"])

        # 出生日
        selectYear = Select(driver.find_element_by_id('ddlBirthDay'))
        selectYear.select_by_visible_text(config["birthDay"])

        #驗證碼
        ocr = ddddocr.DdddOcr()
        imageUrl = driver.find_element_by_id("imgVlid").get_attribute("src")
        img = urlopen(imageUrl).read()
        res = ocr.classification(img)
        idText=driver.find_element_by_id('txtVerifyCode')
        idText.send_keys(res)

        btnSubmit = driver.find_element_by_css_selector("input[name='btnOK'][type='submit']")
        btnSubmit.click()

        idLabelTwoYearNote=driver.find_element_by_id('LabelTwoYearNote')
        if idLabelTwoYearNote.text == "您已取號完成，為了您的健康、方便醫師診治、以及節省您的看診時間、請您務必正確填寫以下資料！":
            print("預約成功")
            webhook = Webhook.from_url("https://discord.com/api/webhooks/843017164360515584/j5AV7rN5mOUTAGa77sDZ5IfcVhb6iAX-OnJEgCn0VEraEJNoPwjtQ8fan5tCPRgZEKvO", adapter=RequestsWebhookAdapter()) # Initializin webhook
            webhook.send(content="預約成功")
            break
        else:
            raise Exception("預約失敗")

    except Exception as e:
        print("預約失敗，重新進行預約")
        webhook = Webhook.from_url("https://discord.com/api/webhooks/843017164360515584/j5AV7rN5mOUTAGa77sDZ5IfcVhb6iAX-OnJEgCn0VEraEJNoPwjtQ8fan5tCPRgZEKvO", adapter=RequestsWebhookAdapter()) # Initializin webhook
        webhook.send(content="預約失敗")
        driver.get(url)

#關閉瀏覽器 
driver.quit()
