import requests, datetime, re, os, math, shutil
from collections import OrderedDict
from rest_framework import status
from rest_framework.response import Response
from PIL import Image

from sms_middleground.settings import MEDIA_URL, REGEX_MOBILE, REGEX_MAIL


def my_response_data(data=None, status='success', msg='获取成功'):
    """
    添加返回数据字段
    """
    dict = OrderedDict()
    dict["status"] = status
    dict["msg"] = msg
    dict["results"] = data

    # 压缩图片
    compress_img_by_data(data)

    return data

def my_response_page_data(count, next, previous, data=None, status='success', msg='获取成功'):
    """
    返回分页后的数据
    :param count: 数据总条数
    :param next: 下一页的链接
    :param previous: 上一页的链接
    :param data: 数据
    :param status: 状态
    :param msg: 提示信息
    :return:
    """
    dict = OrderedDict()

    dict['count'] = count
    dict['next'] = next
    dict['previous'] = previous
    # dict["status"] = status
    # dict["msg"] = msg
    dict["results"] = data

    # 压缩图片
    compress_img_by_data(data)

    return dict

def get_access_token():
    """
    获取微信的access_token
    :return:
    """
    param = {
        'grant_type': 'client_credential',
        'app_id': 'wxc15b18db450cac2b',
        'secret': '6af4b3c135238ed7c71582b2b1be8433',
    }

    access_token_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=%s&appid=%s&secret=%s' % (
        param['grant_type'], param['app_id'], param['secret'])

    response = requests.get(access_token_url)
    resp_json = response.json()
    access_token = resp_json.get('access_token')
    if not access_token: return None
    return access_token

def get_js_api_ticket(access_token=''):
    """
    获取微信ticket
    :param access_token:
    :return:
    """
    ticket_url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi'
    if not access_token: return None

    ticket_url = ticket_url % access_token
    response = requests.get(ticket_url)
    resp_json = response.json()
    if resp_json.get('errcode') != 0: return None
    ticket = resp_json.get('ticket')
    return ticket

def compress_img(path, high_path='', width=1376):
    """
    图片压缩
    :param path: 图片存储路径
    :param width: 图片限制宽度
    """
    img = Image.open(path)
    w, h = img.size
    if not os.path.exists(high_path):
        shutil.copy(path, high_path)
    if w > width:
        new_img = img.resize((width, math.floor(h * width / w)), Image.ANTIALIAS)
        new_img.save(path, quality=95)

def del_file(path, file_name):
    """
    删除指定路径下的所有该名称的文件
    :param path: 文件夹路径
    :param file_name: 要删除的文件名称
    :return:
    """
    try:
        file_path = os.path.join(path, file_name)
        os.remove(file_path)
    except Exception as e:
        print('-' * 5, '删除图片出错：', e)
    for file in os.listdir(path):
        try:
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                del_file(file_path, file_name)
        except Exception as e:
            print('-'*5, '删除图片出错：', e)

def del_useless_file(path, file_list):
    """
    删除path下无用的文件
    :param path: 文件夹路径
    :param file_list: 有效文件名列表
    :return:
    """
    dir_file_set = set(os.listdir(path))
    file_set = set(file_list)
    diff_list = list(dir_file_set.difference(file_set))

    for file in diff_list:
        try:
            file_path = os.path.join(path, file)
            if os.path.isdir(file_path):
                del_useless_file(file_path, file_list)
            else:
                os.remove(file_path)
        except Exception as e:
            print('-'*5, '删除图片出错：', e)

def compress_img_by_data(data):
    """
    从数据中获取图片的路径
    :param data: 对象
    """
    img_list = re.findall(
        r'(media/.*?(bmp|jpg|png|tif|gif|pcx|tga|exif|fpx|svg|psd|cdr|pcd|dxf|ufo|eps|ai|raw|WMF|webp|jpeg))', str(data))

    for path, type in img_list:
        if os.path.exists(path):
            path_list = re.split(r'[/|\\]', path)
            high_path = '/'.join(path_list[:-1]) + '/high/'
            if not os.path.exists(high_path):
                os.mkdir(high_path)
            high_path += path_list[-1]

            compress_img(path, high_path=high_path)

def complement_img_path(path, request):
    """
    补全图片路径
    :param path: 数据库保存路径
    :return: 完整路径
    """
    return request.META['wsgi.url_scheme'] + '://' + request.META['HTTP_HOST'] + MEDIA_URL + path if path != '/' else path[1:]

def validate_mobile(mobile):
     """
     验证手机号码的合法性
     :param mobile:
     :return:
     """
     ret = True
     if not re.match(REGEX_MOBILE, mobile): ret = False
     return ret

def validate_email(email):
    """
    验证邮箱的合法性
    :param mobile:
    :return:
    """
    ret = True
    if not re.match(REGEX_MAIL, email): ret = False
    return ret

def str_remove_duplicates(str,  separator=r';|；', sep=';', start=0, end=-1, flag=True):
    """
    对字符串进行分割去重  返回新字符串
    :param str: 目标字符串
    :param separator: 正则
    :param sep: 分隔符
    :param start: 切片开始位置
    :param end: 切片结束位置
    :param flag: 有序标识
    :return: 字符串
    """
    old_list = list_str_2_list(str, separator, start, end)
    old_list = [i for i in old_list if i != '']
    new_list = list(set(old_list))
    new_list.sort(key=old_list.index)
    return sep.join(new_list) + sep

def get_model_fields(model_obj, exclude_list=['create_time', 'update_time', 'is_delete']):
    """
    获取目标模型的所有字段
    :param model_obj: 目标模型
    :param exclude_list: 排除字段列表
    :return: 字段列表
    """
    field_list = [field.name for field in model_obj._meta.fields if field.name not in exclude_list]
    return field_list

def list_str_2_list(data, exp_sep=r'[;；]', start=0, end=-1):
    """
    字符串转列表
    :param data: 数据
    :param exp_sep: 分隔符正则
    :param start: 切片开始
    :param end: 切片结束
    :return:
    """
    if re.match(r'.*?[;；]$', data):
        return re.split(exp_sep, data)[start:end]
    return re.split(exp_sep, data)

def getWeekDate(type='day', default_date=None):
    """
    获取指定日期
    :param type: 类别
    :return:
    """
    if not default_date:
        now = datetime.datetime.now()
    else:
        now = default_date
    _year = now.year
    if type == 'mouth':
        start_mouth_list = ['%d-%d-1' % (_year, i) for i in range(1, 13)]
        end_mouth_list = ['%d-%d-1' % (_year, i) for i in range(2, 13)] + ['%d-1-1' % (_year+1)]
        mouth_list = zip(start_mouth_list, end_mouth_list)
        return mouth_list

    # 周
    # w_start = now - timedelta(days=now.weekday())  # 本周第一天
    # w_end = now + timedelta(days=6 - now.weekday())  # 本周最后一天

    day_list = []
    start_day_list = []
    end_day_list = []

    for i in range(now.weekday(), -1, -1):
        star_time = now - datetime.timedelta(days=i)
        end_time = now - datetime.timedelta(days=i-1)
        start_day_list.append(star_time.strftime('%Y-%m-%d'))  # 追加日期
        end_day_list.append(end_time.strftime('%Y-%m-%d'))  # 追加日期

    return zip(start_day_list, end_day_list)

def getRandomList(size=30, total=100, big_num=5, random_range=20):
    """
    获取一个随机的数组
    :param size: 数组大小
    :param total: 数据总和
    :param big_num: 大数数量
    :param random_range: 随机范围
    :return: list
    """
    import random
    # 随机数数组
    r_list = []
    # 返回数组
    ret_list = []
    # 获取size个随机数
    for i in range(big_num):
        num = random.randint(random_range*3, random_range*4)
        r_list.append(num)
    for i in range(size - big_num):
        num = random.randint(1, random_range)
        r_list.append(num)
    # 求和
    num_sum = sum(r_list)
    # 生成要返回的列表
    for index,num in enumerate(r_list[:]):
        if len(ret_list) < size - 1:
            ret_list.append(round(round(num / num_sum, 4) * 100 * total, 2))
        # 最后一个数单独计算
        else:
            ret_list.append(total*100 - sum(ret_list))
    ret_list = [int(i)/100 for i in ret_list]
    # 调试
    # print(ret_list, sum(ret_list), len(ret_list))
    return ret_list
