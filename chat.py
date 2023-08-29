import time
from amodel import *
import traceback
import os
from aunit import setClipboard, read_txt, read_img, get_local_browser
from selenium.webdriver.common.keys import Keys


def send_message(driver, file_name):
    """发送3张图片和一段话术"""
    all_files = os.listdir(f'{os.path.dirname(__file__)}\\chat')

    for i in all_files:
        if file_name == i:
            setClipboard(read_txt(f'{os.path.dirname(__file__)}\\chat\\{file_name}'), 'text')
        elif 'png' in i:
            setClipboard(read_img(f'{os.path.dirname(__file__)}\\chat\\{i}'), 'img')
        else:
            continue
        msg = driver.find_element_by_css_selector("[class='bosschat-chat-input chat-global-message']")
        msg.click()
        time.sleep(2)
        msg.send_keys(Keys.CONTROL, 'v')
        time.sleep(2)
        msg.send_keys(Keys.ENTER)
        time.sleep(2)


def record_data(SQLsession, result={}):
    """写入数据库"""
    find_data = SQLsession.query(Candidate).filter_by(name=result.get('name')).first()
    if not find_data:
        SQLsession.add(Candidate(**result))
    else:
        if result.get('secondtime', ''):
            find_data.secondtime = result.get('secondtime', '')
    SQLsession.commit()

def run_chat(driver, sty, num=0):
    """
    :param driver: 浏览器对象
    :param sty: 牛人管理：等于0则选择新招呼，等于1选择我发起
    :param num: 牛人管理：页数
    :return:
    """
    driver.switch_to.default_content()
    account = driver.find_element_by_css_selector("[class='nav-item nav-logout']").text.strip()
    # 牛人管理
    driver.find_element_by_class_name('menu-geek-manage').click()
    time.sleep(3)
    # 我发起或新招呼
    driver.find_element_by_class_name('reset-btn').click()
    time.sleep(3)
    driver.find_element_by_class_name('condition-filter').find_elements_by_class_name("single-checkbox")[
        sty].find_elements_by_css_selector("span")[0].click()
    time.sleep(3)
    # 获取总页数
    num = num if num else driver.find_element_by_class_name("options-pages").find_elements_by_tag_name('a')[-2].text
    for p in range(int(num)):
        for s in range(
                len(driver.find_element_by_class_name('ui-tablepro-fixed-right').find_elements_by_css_selector(
                    "[class='operate-item']"))):
            try:
                job = driver.find_element_by_css_selector("[class='ui-tablepro-wrapper']").find_element_by_class_name(
                    'ui-tablepro-tbody').find_elements_by_tag_name('tr')[s].find_elements_by_tag_name('td')[5].text
                if "外贸" in job:
                    # 点击沟通按钮
                    t = driver.find_element_by_class_name('ui-tablepro-fixed-right').find_elements_by_css_selector(
                        "[class='operate-item']")[s]
                    if s > 7:
                        driver.execute_script("arguments[0].scrollIntoView();", t)
                    else:
                        driver.execute_script("arguments[0].scrollIntoView(false);", t)
                    t.click()
                    time.sleep(3)
                    # 名字
                    name = driver.find_element_by_css_selector("span[class='chatview-name']").text
                    if sty:
                        # # 聊天记录
                        bosschat = driver.find_element_by_class_name(
                            "chat-global-conversation").find_element_by_css_selector(
                            "ul.chat-message-ul")
                        time.sleep(3)
                        # 状态
                        status_all = ''
                        bos = bosschat.find_elements_by_css_selector("li")
                        for cha in bos:
                            status = cha.get_attribute('class')
                            status_all = status_all + ' ' + status
                        if 'item-friend' not in status_all and status_all.count(
                                'item-myself status-read') == 1 and status_all.count('item-myself') == 1:
                            send_message(driver, 'chat.txt')
                            time.sleep(3)
                            # 二次打招呼写入数据库
                            d = dict(secondtime=str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), name=name,
                                     account=account)
                            print(d)
                            record_data(SQLsession, d)
                    else:
                        send_message(driver, 'reply.txt')
                        # driver.find_element_by_css_selector("[class='iboss-editor-resume toolbar-btn']").click()
                        # time.sleep(3)
                        # driver.find_element_by_css_selector(
                        #     "[class='dialog-wrap resume dialog-around-default dialog-top-default']").find_element_by_css_selector(
                        #     "[class='btn btn-primary btn-sure']").click()
                        time.sleep(3)
                        # 新招呼写入数据库
                        d = dict(firsttime=str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), name=name,
                                 account=account,
                                 style='新招呼', chat='已回复并索要简历')
                        print(d)
                        record_data(SQLsession, d)
                    # 退出X号
                    driver.find_element_by_css_selector("[class='iboss iboss-close']").click()
                    time.sleep(3)
            except:
                traceback.print_exc()
        # # 下一页
        driver.find_element_by_css_selector("i[class='ui-icon-arrow-right']").click()
        time.sleep(5)

if __name__ == '__main__':
    os.system('taskkill /IM chrome.exe /F')
    window, driver = get_local_browser()
    run_chat(driver, 1, 1)
    driver.close()
    window.close()
    os.system('taskkill /IM chromedriver.exe /F')