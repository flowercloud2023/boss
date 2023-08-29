from chat import *

if __name__ == '__main__':
    os.system('taskkill /IM chrome.exe /F')
    driver = get_local_browser()
    for i in range(2):
        try:
            run_chat(driver, i)
        except:
            traceback.print_exc()
    driver.close()
    os.system('taskkill /IM chromedriver.exe /F')