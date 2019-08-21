import datetime
from datetime import timedelta

def getDate(type):
    """
    获取指定日期
    :param type:
    :return:
    """
    now = datetime.datetime.now()

    # 周
    # w_start = now - timedelta(days=now.weekday())  # 本周第一天
    # w_end = now + timedelta(days=6 - now.weekday())  # 本周最后一天

    day_list = []
    for i in range(now.weekday(), -1, -1):
        time = now - timedelta(days=i)
        day_list.append(time.strftime('%Y-%m-%d'))  # 追加日期
    return day_list

if __name__ == '__main__':
    print(getDate(''))