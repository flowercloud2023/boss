import configparser
import time
import random
import traceback
from aunit import get_local_browser
from amodel import *


def record_data(d):
    find_data = SQLsession.query(Candidate).filter_by(name=d.get('name')).first()
    if not find_data:
        SQLsession.add(Candidate(**d))
        SQLsession.commit()


def get_ini():
    conn = configparser.ConfigParser()
    conn.read(f'{os.path.dirname(__file__)}\\config.ini', encoding='utf-8')
    grade = conn.get("request", "grade").split(',')
    age_min, age_max = conn.get("request", "age").split(',')
    age = [i for i in range(int(age_min), int(age_max) + 1)]
    job = conn.get("request", "job").split(',')
    education = conn.get("request", "education").split(',')
    location = conn.get("request", "location").split(',')
    page = int(conn.get("request", "page"))
    return grade, age, job, education, location, page


def data_filter(data):
    num = 0
    # 读取配置文件
    grade, age, job, education, location, page = get_ini()
    d = dict(grade=grade, age=age, job=job, education=education, location=location)
    for i, v in d.items():
        if data.get(i) in v or 'all' in v:
            num += 1
        if i == 'grade':
            r = False
            for j in data.get(i, []):
                for k in v:
                    if k in j:
                        r = True
                if r:
                    num += 1
                    break
    return True if num > 4 else False


def run_recruit(driver, style=0):
    error_index = 0
    driver.switch_to.default_content()
    account = driver.find_element_by_css_selector("[class='nav-item nav-logout']").text.strip()
    # 推荐牛人
    driver.find_element_by_class_name('menu-recommend').click()
    time.sleep(5)
    # 切过去
    driver.switch_to.frame('recommendFrame')
    if style == 1:
        # 选择新牛人
        driver.find_element_by_css_selector("ul[class='tab-list']").find_elements_by_tag_name('li')[2].click()
        time.sleep(5)
    if style == 2:
        # 选择查看我
        js = "arguments[0].setAttribute('style',arguments[1])"
        s = "display:block"
        driver.execute_script(js, driver.find_element_by_css_selector("[class='sub-tab-list']"), s)
        driver.find_element_by_css_selector("[class='sub-tab-list']").find_element_by_tag_name('li').click()
        time.sleep(5)
        s = "display: none;"
        driver.execute_script(js, driver.find_element_by_css_selector("[class='sub-tab-list']"), s)
    # 下拉框选择业务员职位
    driver.find_element_by_css_selector(
        "[class='ui-dropmenu ui-dropmenu-label-arrow ui-dropmenu-drop-arrow job-selecter-wrap']").click()
    time.sleep(5)
    # 随机选择外贸业务员
    r = []
    for i, v in enumerate(
            driver.find_element_by_css_selector("ul[class='job-list']").find_elements_by_tag_name('span')):
        if '外贸' in v.text:
            r.append(i)
    i = random.choice(r)
    driver.find_element_by_css_selector("ul[class='job-list']").find_elements_by_tag_name('span')[i].click()
    time.sleep(5)
    # 往下滚动获取批量简历
    user_list, end = [], False
    for i in range(30):
        for j in range(15):
            try:
                d, c = {}, False
                t = driver.find_element_by_xpath(f'//*[@id="recommend-list"]/div/ul/li[{15 * i + j + 1}]')
                if t.find_elements_by_css_selector('em[class="icon-coop iboss-goutongjindu-xian"]'):
                    continue
                job_location = t.find_element_by_class_name('expect-box').find_elements_by_tag_name('span')[
                    -1].text.split(' ')
                if job_location:
                    d['job'] = job_location[-1]
                    d['location'] = job_location[0]
                t.click()
                c = True
                time.sleep(3)
                info = driver.find_element_by_class_name('resume-item-pop-box')
                d['name'] = info.find_element_by_class_name('geek-name').text
                d['age'] = int(info.find_elements_by_css_selector("span[class='label-text']")[0].text.replace('岁', ''))
                d['education'] = info.find_elements_by_css_selector("span[class='label-text']")[2].text
                d['grade'] = []
                g = info.find_elements_by_css_selector("[class='item-right close']")
                if g:
                    d['grade'] = [v.text for v in g[0].find_elements_by_tag_name('li')]
                des = info.find_elements_by_css_selector("[class='text selfDescription']")
                if des:
                    d['grade'].append(des[0].text)
                # 判断是否合适
                if data_filter(d):
                    # 符合要求的求职者，执行打招呼操作
                    greet = driver.find_elements_by_css_selector("[class='btn btn-greet']")
                    if greet:
                        greet[-1].click()
                        time.sleep(3)
                        user_list.append(d)
                        d['style'] = '新牛人' if style == 1 else '查看我' if style == 2 else '推荐'
                        d['chat'] = '已沟通'
                        d['firsttime'] = datetime.now().strftime('%Y-%m-%d')
                        d['account'] = account
                        d['grade'] = '、'.join(d['grade'])
                        driver.switch_to.default_content()
                        sc = SQLsession.query(Candidate).filter_by(account=account,
                                                                   firsttime=datetime.now().strftime('%Y-%m-%d')).all()
                        if 0 <= int(datetime.now().strftime('%H')) < 12 and len(sc) >= 100:
                            return True
                        if 12 <= int(datetime.now().strftime('%H')) <= 23 and len(sc) >= 200:
                            return True
                        if driver.find_elements_by_css_selector('[class="business-block-content"]'):
                            return True
                        record_data(d)
                        driver.switch_to.frame('recommendFrame')
                        time.sleep(1)
            except:
                traceback.print_exc()
                time.sleep(3)
                error_index += 1
                if error_index == 10:
                    return False
            finally:
                try:
                    # 关闭简历框
                    if c:
                        driver.find_element_by_class_name('iboss-iconguanbi').click()
                        time.sleep(5)
                except:
                    pass

        # 滑动翻下一页
        d = driver.find_element_by_id('recommend-list').find_elements_by_tag_name('li')
        driver.execute_script("arguments[0].scrollIntoView();", d[-1])
        time.sleep(10)

