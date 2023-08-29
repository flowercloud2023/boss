from greet import *
from chat import *

if __name__ == '__main__':
    grade, age, job, education, location, page = get_ini()
    os.system('taskkill /IM chrome.exe /F')
    driver = get_local_browser()
    try:
        for style in range(3):
            if run_recruit(driver, style) is True:
                driver.refresh()
                time.sleep(5)
                break
        run_chat(driver, 1, int(page))
    except:
        traceback.print_exc()
    driver.close()
    os.system('taskkill /IM chromedriver.exe /F')
