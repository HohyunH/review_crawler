from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import time
import re
from tqdm import tqdm
from datetime import datetime
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import requests
import json
from webdriver_manager.chrome import ChromeDriverManager
from konlpy.tag import Okt



class powder_crawler():

    def __init__(self, keyword, option, sort_type):

        self.post_list = []
        self.comment_list = []
        self.db_model = db_model.DB_model()
        # self.keyword = input("키워드를 입력하시오 : ")
        self.keyword = keyword
        self.post_url = []
        self.count = 0
        self.option = option
        self.sort_type = sort_type
        # self.board_type = board_type
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(ChromeDriverManager(version="87.0.4280.88").install(),
        #executable_path="/usr/bin/chromedriver",
                                       chrome_options=chrome_options)

    def get_post_info(self):

        self.driver.get('https://www.powderroom.co.kr/')



        def get_post_url(offset: int):


            self.driver.get('https://www.powderroom.co.kr/')
            post = []
            date = []
            api_url = 'https://api.powderroom.co.kr/powderroom/search/board?limit=4&boardTypes=REVIEW&sort={}&order=DESC&query={}'.format(
                self.sort_type, self.keyword) if offset < 4 \
                else 'https://api.powderroom.co.kr/powderroom/search/board?offset={}&limit=4&boardTypes=REVIEW&sort={}&order=DESC&query={}'.format(
                offset, self.sort_type, self.keyword)

            print(api_url)
            self.driver.execute_script('''
                function loadXMLDoc() {
                  var xhttp = new XMLHttpRequest();
                  xhttp.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                      document.write('<div id="find_me">'+this.responseText+'</div>');
                    }
                  };
                  xhttp.open("GET", "%s", true);
                  xhttp.send()
                }
                return loadXMLDoc()''' % (api_url))

            time.sleep(2)
            main = self.driver.find_element_by_css_selector('html').text
            # print(main)
            raw_json = json.loads(main, strict=False)

            for i in range(4):
                post.append("https://www.powderroom.co.kr/board/" + str(raw_json['data'][i]['boardId']))
                date.append(raw_json['data'][i]['createdAt'])

            return post, date

        if type(self.option) == int :
            for j in range(self.option // 4 + 1):
                url, p_date = get_post_url(4 * j)
                self.post_url.extend(url)

            self.post_url = self.post_url[:self.option]

        else :
            k = 0
            a = 1
            while a!=0:
                url, p_date = get_post_url(4 * k)
                for url_, time_ in zip(url,p_date):
                    self.post_url.append(url_)
                    if self.option > time_:
                        a=0
                k+=1

        print('Total review url count: ', len(self.post_url))
        print(self.post_url)

        self.driver.maximize_window()
        self.driver.implicitly_wait(3)

        def remove_emoji(string):
            # 이모티콘 제거
            emoji_pattern = re.compile("["
                                       u"\U0001F600-\U0001F64F"  # emoticons
                                       u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                       u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                       u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                       "]+", flags=re.UNICODE)

            # 분석에 어긋나는 불용어구 제외 (특수문자, 의성어)
            han = re.compile('[ㄱ-ㅎㅏ-ㅣ]+')
            url = re.compile('(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
            special = re.compile('[^\w\s#]')
            email = re.compile('([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')

            tmp = emoji_pattern.sub('', string)
            tmp = han.sub('', tmp)
            tmp = url.sub('', tmp)
            tmp = special.sub('', tmp)
            tmp = email.sub('', tmp)

            return tmp

        def return_tags(content):
            okt = Okt()
            token_content = okt.morphs(content)
            tag_word = []
            for token in token_content:
                if token.startswith("#"):
                    tag_word.append(token)
            tag_word= " ".join(tag_word)

            return tag_word

        for url_ in self.post_url:

            tmp_cnts = []
            tmp_cmts = []

            self.driver.get(url_)
            time.sleep(5)

            cnts = self.driver.find_element_by_css_selector("div[class='content-body']")
            tmp_cnts.append(cnts.text)
            self.post_list.append(tmp_cnts)

            post = cnts.text

            if '\n' in post:
                post = re.sub("\n", " ", post)

            post = remove_emoji(post)

            tags = return_tags(post)


            like = self.driver.find_element_by_css_selector("#q-app > div > div > div > div > main > div.board-detail-review > div.block.status > div > div > div:nth-child(1) > span")
            like_count = like.text

            id = self.driver.find_element_by_css_selector("div[class='col-auto nickname ellipsis']")
            user_id = id.text

            view = self.driver.find_element_by_css_selector("#q-app > div > div > div > div > main > div.board-detail-review > div.block.status > div > div > div:nth-child(3) > span")
            view_count = int(view.text)

            html_source = self.driver.page_source
            soup = BeautifulSoup(html_source, 'lxml')

            time_ = soup.select("#q-app > div > div > div > div > main > div.board-detail-review > div.block.content > div.user-box.row.justify-start.items-end > div.col-auto > span")[0].text
            time_ = re.sub("\.", "-", time_)

            try:
                post_time = datetime.strptime(time_, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, IndexError) :
                post_time = self.db_model.conv_date_pdr(time_)

            title = self.driver.find_element_by_css_selector("#q-app > div > div > div > div > main > div.board-detail-review > div.block.content > div.title-box.ellipsis-2-lines").text

            try :
                brand = self.driver.find_element_by_css_selector("#q-app > div > div > div > div > main > div.board-detail-review > div.block.review-rate > div.cursor-pointer.relative-position > div.product-item > div > div.content.col > div.brand-name").text
            except :
                brand = None

            try :
                price = self.driver.find_element_by_css_selector("#q-app > div > div > div > div > main > div.board-detail-review > div.block.review-rate > div.cursor-pointer.relative-position > div.product-item > div > div.content.col > div.price").text
            except :
                price = 0
            try :
                tag = self.driver.find_element_by_css_selector("#q-app > div > div > div > div > main > div.board-detail-review > div.block.content > div.user-box.row.justify-start.items-end > div.col > div > div > div.col.middle > div > div.col-12.tag.ellipsis > span").text
                print(type(tag))
                split_tags = tag.split("#")
                tone = split_tags[1]
                skin_type = split_tags[2]
                cosmetic_number = split_tags[3]
                face_color = split_tags[4]
            except :
                tag, tone, skin_type, cosmetic_number, face_color = None, None, None, None, None


            try :
                ratio = self.driver.find_element_by_css_selector("#q-app > div > div > div > div > main > div.board-detail-review > div.block.review-rate > div.rating-box > div > div > div.col.text.self-end > div").text
            except :
                ratio = 0

            try :
                product_name = self.driver.find_element_by_css_selector("#q-app > div > div > div > div > main > div.board-detail-review > div.block.review-rate > div.cursor-pointer.relative-position > div.product-item > div > div.content.col > div.product-name.ellipsis").text
                if brand in product_name:
                    product_name = product_name.replace(brand, "")
                    product_name = product_name.replace("[] ", "")
                else :
                    None
            except :
                product_name = None

            try :
                advert = self.driver.find_element_by_css_selector(
                    "#q-app > div > div > div > div > main > div.board-detail-review > div.block.content > div.label-box > span").text
                if advert == '제품제공' or advert == '체험단':
                    title = "[광고] " + title
                else :
                    None
            except :
                None

            try :
                self.count = int(self.driver.find_element_by_css_selector(
                    "#boardDetailComment > div > div > div.col-auto.text-left.title.undefined"
                ).text[3:])
            except :
                None

            post_dict = {
                'unique_id': url_[-8:],
                'keyword': self.keyword,
                'title': title,
                'user_name': user_id,
                'like_count': like_count,
                'comment_count': self.count,
                'contents': post,
                'user_id' : 0,
                'posting_date': post_time,
                'view_count': view_count,
                'dislike_count': 0,
                'user_follow': 0,
                'user_follower': 0,
                'user_medias': 0,
                'additional_data': [
                    {'data_key': 'brand',
                     'data_value': brand},
                    {'data_key': 'volume',
                     'data_value': None},
                    {'data_key': 'price',
                     'data_value': price},
                    {'data_key': 'sellers',
                     'data_value': None},
                    {'data_key': 'tone',
                     'data_value': tone},
                    {'data_key': 'skin_type',
                     'data_value': skin_type},
                    {'data_key': 'cosmetic_number',
                     'data_value': cosmetic_number},
                    {'data_key': 'face_color',
                     'data_value': face_color},
                    {'data_key': 'tags',
                     'data_value': tags},
                    {'data_key' : 'product_name',
                     'data_value' : product_name},
                    {'data_key': 'star_score',
                     'data_value': ratio}
                ]
            }

            body_is_new = self.db_model.set_data_body(5, post_dict)
            self.db_model.set_data_body_info(5, body_is_new['is_new'], post_dict)

            self.driver.get(url_ + '/comment')
            time.sleep(5)
            num = self.driver.find_element_by_css_selector(
                '#q-app > div > div > div > div > main > div.logo-header.sticky > div > div.col.title > div'
            )
            cmt_num = num.text
            cmt_num = re.sub("[^0-9]", "", cmt_num)
            cmt_num = int(cmt_num)
            print(self.driver.current_url, "댓글 개수: ", cmt_num)

            time.sleep(2)

            if cmt_num > 20:
                extention = (cmt_num - 20) // 10 + 1

                for i in range(extention):
                    self.driver.find_element_by_tag_name('body').send_keys(Keys.END)
                    time.sleep(2)

                self.driver.find_element_by_tag_name('body').send_keys(Keys.HOME)
                time.sleep(3)

            for i in range(1, cmt_num + 1):
                try :
                    cmts = self.driver.find_element_by_css_selector(
                        '#q-app > div > div > div > div > main > div.q-infinite-scroll > span > div:nth-child(%s) > div > div > div.col.text > span:nth-child(2)' % i
                    )
                    comment = cmts.text
                    comment = remove_emoji(comment)
                except :
                    cmts = None
                    comment = None

                tmp_cmts.append(comment)
                time.sleep(3)
                cmt_date = self.driver.find_element_by_css_selector(
                    "#q-app > div > div > div > div > main > div.q-infinite-scroll > span > div:nth-child(%s) > div > div > div.col.text > div" % i
                )

                try :
                    cmt_id = self.driver.find_element_by_css_selector(
                        "#q-app > div > div > div > div > main > div.q-infinite-scroll > span > div:nth-child(%s) > div > div > div.col.text > span.nickname" % i
                    )

                    cmt_id = cmt_id.text
                except :
                    cmt_id = None

                try:
                    comment_date = self.db_model.conv_date_pdr(cmt_date.text[:-5])
                except ValueError:
                    comment_date = self.db_model.conv_date_pdr(cmt_date.text)

                comment_dict = {
                    "unique_id": url_[-8:],
                    "keyword": self.keyword,
                    "user_name": cmt_id,
                    "comment": comment,
                    "comment_date": comment_date,
                    "comment_id": 0,
                    "comment_like": 0
                }

                self.db_model.set_data_comment(5, comment_dict, body_is_new['is_new'], body_is_new['last_time_update'])

            self.comment_list.append(tmp_cmts)
            time.sleep(2)

        row_id = self.db_model.set_daily_log(self.keyword, 5)
        self.db_model.set_daily_log('', '', row_id)
        # self.driver.quit()

        return self.post_list, self.comment_list


if __name__ == "__main__":
    import db_model
    import time
    import pwd_arg_crawler
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Powderroom crawler")
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-n', '--post_num', action='store_true', help='Crawling based on the post number.')
    group.add_argument('-d', '--post_date', action='store_true', help='Crawling based on the post date.')

    parser.add_argument('keyword', type=str, help='Enter the keyword.')
    # parser.add_argument('type', type=str, help='Enter type -> REVIEW or MOTD')
    parser.add_argument('sort_type', type=str, help='Enter type -> POPULAR or LATEST')
    parser.add_argument('option', help='Enter the post number or date of the post.')

    arg = parser.parse_args()
    keyword = arg.keyword
    # board_type = arg.type
    sort_type = arg.sort_type

    if arg.post_num:
        try:
            option = int(arg.option)
        except ValueError:
            print("Please enter '-d' or '--post_date' argument option.")
            sys.exit()
    elif arg.post_date:
        try:
            option = int(arg.option)
            print("Please enter '-n' or '--post_num' argument option.")
            sys.exit()
        except ValueError:
            option = arg.option
    else:
        print('Please enter the argument option.')
        sys.exit()

    start = time.time()

    crawler = powder_crawler(keyword, option, sort_type)

    contents, comments = crawler.get_post_info()

    print("time :", time.time() - start)




