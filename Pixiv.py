from requests.exceptions import RequestException
import requests
import time
import json
import sys
import re
import os


# Session会话维持
session = requests.Session()
headers = {
            'origin': 'https://accounts.pixiv.net',
            'referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/69.0.3497.100 Safari/537.36',
        }
session.headers = headers


def do_login(pixiv_id, pw):
    """模拟登陆"""
    try:
        # ---------- GET相关 ----------
        # GET获取登录页面
        login_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
        # GET参数
        params = {
            'lang': 'zh',
            'source': 'pc',
            'view_type': 'page',
            'ref': 'wwwtop_accounts_index'
        }
        # 获取登录页面
        response = session.get(login_url, params=params)

        # ---------- POST相关 ----------
        # 建立匹配规则
        pattern = re.compile(r'name="post_key" value="(.*?)">')
        # 提取POST中KEY值
        post_key = pattern.findall(response.text)[0]
        # POST提交网址
        post_url = 'https://accounts.pixiv.net/api/login?lang=zh'
        # POST参数
        data = {
            'captcha': '',
            'g_reaptcha_response': '',
            'password': pw,
            'pixiv_id': pixiv_id,
            'post_key': post_key,
            'source': 'pc',
            'ref': 'wwwtop_accounts_index',
            'return_to': 'https://www.pixiv.net/',

        }
        pos = session.post(url=post_url, data=data)
        pos_json = json.loads(pos.content.decode('utf-8'))
        p = pos_json['body']
        if pos.status_code == 200:
            if "success" in p:
                print("登陆成功!")
                print("-"*50)
            else:
                print("登陆失败! 警告:", p['validation_errors'])
                raise RequestException
        else:
            print("登陆失败! 状态码：", pos.status_code)
            raise RequestException
    except RequestException as Err:
        print("登陆失败!")
        print(Err)


def get_page(uid):
    """获取Ajax网页:all"""
    url = 'https://www.pixiv.net/ajax/user/' + uid + '/profile/all'
    member_url = "https://www.pixiv.net/member_illust.php?id=" + uid
    try:
        res = session.get(url)
        member_html = session.get(member_url).content.decode('unicode_escape')
        if res.status_code == 200:
            html = res.content.decode('utf-8')
            # 提取pid
            res_json = json.loads(html)
            res_illusts = res_json['body']['illusts']
            # 提取画师名字
            member_pat = 'name":"(.*?)"'
            res_member = re.findall(member_pat, member_html)[0]
            pid_dict = re.split(',', str(res_illusts))
            return pid_dict,  res_member
        else:
            print("获取Ajax网页失败, 状态:", res.status_code)
            raise RequestException
    except RequestException:
        print("获取Ajax网页失败")
        return None


def parse_page(html):
    """解析网页:all"""
    try:
        url_list = list()
        for voo in html:
            r = re.findall('\\d+', voo)[0]
            url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=' + str(r)
            # 构建url列表
            url_list.append(url)
        return url_list
    except RequestException:
        return None


def save_img(url, name):
    """保存图片"""
    whole_img_url = str()
    try:
        path = './pic/' + str(name) + '/'
        # 创建目录
        if not os.path.exists(path):
            os.makedirs(path)
        # 提取图片网址
        res = session.get(url).text
        pat = '"original":"(.*?)"'
        img_url = re.findall(pat, res)[0]
        split_img_url = re.split('\\\\', img_url)
        for voo in split_img_url:
            whole_img_url += voo
        # 提取图片名字
        pic_name = re.split('/', str(img_url))
        img_name = path + pic_name[len(pic_name) - 1]
        # 下载图片
        print(whole_img_url)
        img_req = session.get(whole_img_url)
        with open(img_name, 'wb') as outfile:
            outfile.write(img_req.content)
            outfile.close()
        time.sleep(3)
    except Exception as E:
        print("下载失败...图片URL:\n", whole_img_url, E)


def main():
    """主函数"""
    try:
        uid = input("请输入作者ID: ")
        pixiv_id = input("请输入PixivID: ")
        pixiv_pw = input("请输入Pixiv密码: ")
        print("登陆中...")
        do_login(pixiv_id, pixiv_pw)
        time.sleep(2)
        html, member = get_page(uid)
        url_list = parse_page(html)
        for voo in url_list:
            save_img(voo, member)
        os.system("pause")
    except OSError:
        print("Unexpected error:", sys.exc_info())
        os.system("pause")


if __name__ == '__main__':
    main()
