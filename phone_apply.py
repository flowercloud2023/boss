import random
from amodel import *
import threading
import time
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
from airtest.core.android import Android
from airtest.core.android.adb import ADB
import re
import configparser
import os
import traceback
import datetime


def get_adbs():
    """
    获取当前所有设备的serialno
    :return:
    """
    adbs = ADB()
    adb_list = [d[0] for d in adbs.devices(state="device")]
    return adb_list


def get_ini():
    # 读取配置文件config.ini ，获取筛选条件
    conn = configparser.ConfigParser()
    conn.read(f'{os.path.dirname(__file__)}\\config.ini', encoding='utf-8')
    grade_filter = conn.get("request", "grade").split(',')
    age_min, age_max = conn.get("request", "age_range").split(',')
    age_filter = [i for i in range(int(age_min), int(age_max) + 1)]
    job_filter = conn.get("request", "job_list").split(',')
    education_filter = conn.get("request", "education_list").split(',')
    location_filter = conn.get("request", "location").split(',')
    return grade_filter, age_filter, job_filter, education_filter, location_filter


def record_data(SQLsession, result={}, style='get'):
    if style == 'get':
        find_all = SQLsession.query(Candidate).all()
        return [i.name for i in find_all]
    else:
        if result.get('name'):
            find_data = SQLsession.query(Candidate).filter_by(name=result.get('name')).first()
            if not find_data:
                SQLsession.add(Candidate(**result))
            else:
                find_data.education = result.get('education', '')
                find_data.age = result.get('age', '')
                find_data.job = result.get('job', '')
                find_data.location = result.get('location', '')
                find_data.grade = result.get('grade', '')
                find_data.chat = result.get('chat', '')
                find_data.firsttime = result.get('firsttime', '')
            SQLsession.commit()



def run(device, poco, style):
    engine = create_engine(database)
    DBSession = sessionmaker(bind=engine)
    SQLsession = DBSession()
    # 读取配置文件
    grade_filter, age_filter, job_filter, education_filter, location_filter = get_ini()
    # 开启程序
    device.stop_app('com.hpbr.bosszhipin')
    device.start_app('com.hpbr.bosszhipin')
    time.sleep(10)
    # 获取当前账号信息
    poco(text='我的').click()
    time.sleep(5)
    poco(name='com.hpbr.bosszhipin:id/rl_boss_base_info').click()
    time.sleep(5)
    account = poco(name='com.hpbr.bosszhipin:id/tv_name').get_text()
    time.sleep(3)
    device.keyevent('KEYCODE_BACK')
    time.sleep(5)
    # 点开消息
    if style == 'view':
        poco(text='消息').click()
        time.sleep(10)
        # 往下滑20次内查找“查看了您”
        for r in range(100):
            status = False
            for h in poco(name='com.hpbr.bosszhipin:id/tv_name'):
                if "查看了您" in h.get_text():
                    h.click()
                    time.sleep(3)
                    status = True
                    break
            if status:
                break
            poco.swipe([0.5, 0.8], [0.5, 0.3], duration=0.4)
            time.sleep(10)
    if style == 'recommend':
        poco(text='牛人').click()
        time.sleep(5)
        ly_menu = poco(name='com.hpbr.bosszhipin:id/ly_menu')
        if len(ly_menu.child()) > 1:
            ly_menu.child()[0].click()
            time.sleep(2)
            t = []
            for i, v in enumerate(poco(name='com.hpbr.bosszhipin:id/tv_job_name')):
                if '外贸' in v.get_text():
                    t.append(i)
            choice = random.sample(t, 1)[0] if t else 0
            if choice:
                poco(name='com.hpbr.bosszhipin:id/iv_sort_icon')[choice].drag_to(
                    poco(name='com.hpbr.bosszhipin:id/title_view'), duration=1)
                time.sleep(2)
                poco(text='保存').click()
                time.sleep(5)
                # 开启程序
                device.stop_app('com.hpbr.bosszhipin')
                device.start_app('com.hpbr.bosszhipin')
            else:
                device.keyevent('KEYCODE_BACK')
            time.sleep(10)

    # 在界面滑动次数
    for w in range(200):
        name_list = record_data(SQLsession)
        if poco(textMatches='我是有底线的.*').exists():
            break
        # usename为一页的用户名
        usename = poco(name='com.hpbr.bosszhipin:id/tv_geek_name')
        for l in usename:
            x, y = l.get_position()
            if y > 0.7:
                break
            # 如果不在列表name_list就点击他的主页。
            if l.get_text() not in name_list:
                name_list.append(l.get_text())
                info_dict = {}
                try:
                    l.click()
                    # 用户名加到用户信息列表people_list
                    info_dict['name'] = l.get_text()
                    certificate_list = []  # 学历列表
                    for q in range(20):
                        # 学历
                        education = poco(name='com.hpbr.bosszhipin:id/tv_geek_degree')
                        if education.exists():
                            if education.get_text() in education_filter:
                                info_dict['education'] = education.get_text()

                        # 年龄
                        age = poco(name='com.hpbr.bosszhipin:id/tv_geek_age')
                        if age.exists():
                            agenum = re.sub("\D", "", age.get_text())  # 获取的为：n岁，只要数字部分sub
                            if int(agenum) in age_filter:
                                info_dict['age'] = agenum

                        # 简介里的资格证书
                        introduce = poco(name='com.hpbr.bosszhipin:id/tv_geek_description')
                        if introduce.exists():
                            for gra in grade_filter:
                                if gra in introduce.get_text():
                                    certificate_list.append(gra)

                        # 查看是否有以下元素，无则往下滑。如果滑到“教育经历”就停止滑动
                        if poco(name='com.hpbr.bosszhipin:id/tv_job_and_city').exists():
                            job, location = poco(name='com.hpbr.bosszhipin:id/tv_job_and_city').get_text().split("，")
                            # 求职岗位
                            for job_l in job_filter:
                                if job_l in job or 'all' in job_l.lower():
                                    info_dict['job'] = job
                            # 求职工作地
                            for locations in location_filter:
                                if location in locations or 'all' in locations.lower():
                                    info_dict['location'] = location
                        # 小框里的资格证书
                        qualifi = poco(name='com.hpbr.bosszhipin:id/tv_skill_word')
                        if qualifi.exists():
                            for skill in qualifi:
                                for skilla in grade_filter:
                                    if skilla in skill.get_text():
                                        certificate_list.append(skilla)

                        qualification_list = poco(name='com.hpbr.bosszhipin:id/txt_content')
                        if qualification_list.exists():
                            for qua in qualification_list:
                                for quali in grade_filter:
                                    if qua.get_text() in quali:
                                        certificate_list.append(qua.get_text())
                                        break
                        if poco(text='教育经历').exists() or (
                                not poco(name='com.hpbr.bosszhipin:id/iv_back').exists() and style == 'recommend') or (
                                poco(text='看过我').exists() and style == 'view'):
                            break
                        poco.swipe([0.5, 0.7], [0.5, 0.3], duration=0.7)
                        time.sleep(3)

                    info_dict['grade'] = " ".join(list(set(certificate_list)))  # 证书加到用户信息列表
                    # 判断符合条件的个数，名字占一个，符合就沟通
                    if len([vv for ii, vv in info_dict.items() if vv != '']) > 5:
                        if poco(text='立即沟通').exists():
                            poco(text='立即沟通').click()
                            info_dict['chat'] = '已沟通'
                            print(f"{info_dict['name']}_立即沟通")
                            time.sleep(2)
                            if poco(text='购买聊天加油包').exists():
                                return
                        else:
                            info_dict['chat'] = '符合条件但之前已沟通'
                    else:
                        info_dict['chat'] = '不符合沟通条件'
                    info_dict['style'] = '查看我' if style == 'view' else '推荐'
                    info_dict['firsttime'] = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    info_dict['account'] = account
                    print(info_dict)
                    record_data(SQLsession, info_dict, 'post')
                except:
                    traceback.print_exc()
                finally:
                    time.sleep(3)
                    for z in range(5):
                        if poco(name='com.hpbr.bosszhipin:id/iv_back').exists() and style == 'recommend':
                            # 退出用户主页
                            device.keyevent('KEYCODE_BACK')
                            time.sleep(3)
                        elif not poco(text='看过我').exists() and style == 'view':
                            device.keyevent('KEYCODE_BACK')
                            time.sleep(3)
                        else:
                            break
        poco.swipe([0.5, 0.7], [0.5, 0.3], duration=0.7)
        time.sleep(5)


def runs(serialno):
    device = Android(serialno)
    poco = AndroidUiautomationPoco(device)
    for s in ['recommend', 'view', ]:
        run(device, poco, s)


def main():
    adbs = get_adbs()
    all_task = []
    for serialno in adbs:
        t = threading.Thread(target=runs, args=(serialno,))
        t.setDaemon(True)
        t.start()
        all_task.append(t)
    # 等待线程执行结果
    for t in all_task:
        t.join()  # 设置主线程等待子线程结束
        print("in main: get page success")


if __name__ == '__main__':
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    try:
        main()
    except Exception as e:
        print(e)
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
