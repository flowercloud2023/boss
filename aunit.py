import subprocess
import time
import win32api, win32con
from selenium import webdriver
import win32clipboard as w
from PIL import Image
from io import BytesIO
from selenium.webdriver.chrome.options import Options

def setClipboard(aString, style='text'):
    # 将文字或图片写入电脑的剪切板
    w.OpenClipboard()
    w.EmptyClipboard()
    if style == 'text':
        w.SetClipboardText(aString)
    else:
        w.SetClipboardData(win32con.CF_DIB, aString)
    w.CloseClipboard()

def read_img(iamge_path):
    # 读取图片的数据
    img = Image.open(iamge_path)
    output = BytesIO()
    img.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    return data


def read_txt(file_path):
    # 读取txt的数据
    f = open(file_path, 'r', encoding='utf-8')
    text = f.read().strip()
    f.close()
    return text



def get_local_browser():
    # 通过CMD打开浏览器，使用selenium连接
    chrome = f'"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9999'
    subprocess.Popen(chrome)
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9999")
    driver = webdriver.Chrome(options=options)
    driver.get('https://www.zhipin.com/web/boss/recommend')
    driver.maximize_window()
    time.sleep(10)
    return driver


def get_user_browser():
    # 使用selenium打开浏览器
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')  # run Chrome use root
    options.add_argument('--disable-setuid-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    driver.get('https://login.zhipin.com/?ka=header-login')
    r = win32api.MessageBox(0, f"请登录账号", "消息框标题", win32con.MB_OKCANCEL)
    if r == 2:
        return None
    time.sleep(5)
    return driver




