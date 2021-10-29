# -*- coding:utf-8 -*-
import re
import time
import db_model
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver as wd
from webdriver_manager.chrome import ChromeDriverManager

class navercrawler():

    def __init__(self, keyword, start_time, end_time):

        self.post_list = []
        self.comment_list = []
        self.db_model = db_model.DB_model()
        self.keyword = keyword
        self.startdate = start_time
        self.enddate = end_time
        # self.keyword = input('검색어를 입력하세요: ')
        # self.startdate = input('검색 시작 날짜를 입력하세요(YYYY-MM-DD): ')
        # self.enddate = input('검색 종료 날짜를 입력하세요(YYYY-MM-DD): ')
        self.stop_crawling = 0

    def get_post_info(self, post_num):

        row_id = self.db_model.set_daily_log(self.keyword, 3)
        first_url = f"https://section.blog.naver.com/Search/Post.nhn?pageNo=1&rangeType=PERIOD&orderBy=sim&startDate=" \
                    f"{self.startdate}&endDate={self.enddate}&keyword={self.keyword}"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(ChromeDriverManager(version="87.0.4280.88").install(),
                            #executable_path="/usr/bin/chromedriver"
                            chrome_options=chrome_options)
        driver.get(first_url)
        time.sleep(1.5)  # 안하면 못불러옴
        gunsu = driver.find_element_by_css_selector(
            '#content > section > div.category_search > div.search_information > span > span > em').text

        # num = int(input('가져올 게시글 수를 입력하세요: '))
        if type(post_num)==int:
            print('{}에 대한 검색 결과 {}개를 크롤링 합니다. '.format(self.keyword, post_num))
            num = option
        else :
            print('{}에 대한 검색 결과 입니다. '.format(self.keyword), gunsu)
            num = gunsu.replace("건","")
            num = int(num.replace(",",""))
        breaker = False
        get_post_num = 0
        # 검색 게시글 수 입력 -> 개수 맞게 페이지수 넘김 -> 해당 포스팅 링크 수집
        for i in range(num // 7 + 1):
            loop_url = f"https://section.blog.naver.com/Search/" \
                       f"Post.nhn?pageNo={i+1}&rangeType=PERIOD&orderBy=sim&startDate=" \
                       f"{self.startdate}&endDate={self.enddate}&keyword={self.keyword}"
            driver.get(loop_url)
            time.sleep(3)
            elems = driver.find_elements_by_css_selector("a.desc_inner")
            post_urls = [elem.get_attribute('href') for elem in elems]

            ## 조건 충족 시 반복문 종료
            if breaker == True:
                break

            for j, jj in enumerate(post_urls):
                get_post_num += 1
                print(jj)
                blogno = jj.split("/")[-1]
                blogid = re.compile(".blog.me").sub('', jj.split("/")[-2])
                post_url = f"https://blog.naver.com/PostView.nhn?blogId={blogid}&logNo={blogno}" \
                           f"&redirect=Dlog&widgetTypeCall=true&directAccess=false"
                driver.get(post_url)
                time.sleep(5)

                # 좋아요 기능이 없고 댓글만 있는 경우는 통과
                try:
                    comment_click = driver.find_elements_by_css_selector(
                        '#printPost1 > tbody > tr > td.bcc > div.post-btn.post_btn2 >'
                        ' div.wrap_postcomment > div > a')[1]
                except IndexError:
                    continue

                comment_click.click()
                time.sleep(5)
                html_source = driver.page_source
                soup = BeautifulSoup(html_source, 'lxml')

                follow_res = requests.get("https://section.blog.naver.com/connect/ViewMoreFollowers.nhn",
                                          params={"blogId": blogid})
                time.sleep(2)
                follow_soup = BeautifulSoup(follow_res.content, 'lxml')

                # 블로그 종류 다른 경우
                try:
                    comment_count = int(
                        soup.find("div", {"class": "area_comment pcol3"}).find("a").find("em").get_text(strip=True))
                except AttributeError:
                    comment_count = 0
                # 블로그 종류 다른 경우
                try:
                    user_follower = int(follow_soup.select(
                        "body > div.bg_main > div.container > div > div.content_box > "
                        "div > div.function_box.buddy_cnt_admin > p > strong")[0].text)
                except (AttributeError, IndexError):
                    user_follower = 0
                # 블로그 종류 다른 경우
                try:
                    title = soup.find("div", {"class": "se-module se-module-text se-title-text"}).get_text(strip=True)
                except AttributeError:
                    try:
                        title = soup.find("span", {"class": "pcol1 itemSubjectBoldfont"}).get_text(strip=True)
                    except AttributeError:
                        title = soup.find("h3", {"class": "se_textarea"}).get_text(strip=True)
                # 블로그 종류 다른 경우
                try:
                    user_name = soup.find("span", {"class": "nick"}).find("a").text
                except AttributeError:
                    try:
                        user_name = soup.find("strong", {"id": "nickNameArea"}).text
                    except AttributeError:
                        user_name = soup.find("a", {"class": "link pcol2"}).text

                # 블로그 종류 다른 경우
                try:
                    posting_date = self.db_model.conv_date_naver(
                        soup.find("span", {"class": "se_publishDate pcol2"}).text)
                except AttributeError:
                    try:
                        posting_date = self.db_model.conv_date_naver(
                            soup.find("p", {"class": "date fil5 pcol2 _postAddDate"}).text)
                    except AttributeError:
                        posting_date = self.db_model.conv_date_naver(
                            soup.find("span", {"class": "se_publishDate pcol2"}).text)

                # 블로그 종류 다른 경우
                try:
                    contents = re.compile("\\u200b").sub(' ', soup.find("div", {"class": "se-main-container"}).get_text(
                            strip=True))
                except AttributeError:
                    try:
                        contents = re.compile("\\u200b").sub(' ', soup.find("div", {"id": "postViewArea"}).get_text(
                            strip=True))
                    except AttributeError:
                        contents = re.compile("\\u200b").sub(' ', soup.find(
                            "div", {"class": "se_component_wrap sect_dsc __se_component_area"}).get_text(strip=True))
                # 값 없는 경우
                try:
                    like_count = int(soup.find("em", {"class": "u_cnt _count"}).text)
                except ValueError:
                    like_count = 0

                post_dict = {
                    'unique_id': blogno,
                    'keyword': self.keyword,
                    'title': self.db_model.addslashes(title),
                    'user_id': blogid,
                    'user_name': user_name,
                    'posting_date': posting_date,
                    'view_count': 0,
                    'like_count': like_count,
                    'dislike_count': 0,
                    'contents': self.db_model.addslashes(contents),
                    'user_follow': 0,
                    'user_follower': user_follower,
                    'user_medias': int(
                        soup.select("#category-list > div > ul > li.allview > span")[0].text.replace("(", '').replace(
                            ")", '')),
                    'comment_count': comment_count
                }
                time.sleep(1)

                condition_keyword = self.keyword.replace("추천","").strip()

                if condition_keyword in title:
                    self.stop_crawling = 0
                    body_is_new = self.db_model.set_data_body(3, post_dict)

                    for k in range(len(soup.find_all("span", {"class": "u_cbox_nick"}))):
                        try :
                            comments = self.db_model.addslashes(soup.find_all("span", {"class": "u_cbox_contents"})[k].text)
                        except :
                            comments = None

                        comment_dict = {
                            "unique_id": blogno,
                            "keyword": self.keyword,
                            "user_name": soup.find_all("span", {"class": "u_cbox_nick"})[k].text,
                            "comment_date": datetime.strptime(soup.find_all("span", {"class": "u_cbox_date"})[k].text,
                                                              '%Y.%m.%d. %H:%M').strftime("%Y-%m-%d %H:%M:%S"),
                            "comment": comments,
                            "comment_like": 0
                        }
                        time.sleep(1)

                        # 쿼리 / body_is_new여부에 따라
                        if soup.find_all("span", {"class": "u_cbox_nick"})[k].text != user_name:
                            self.db_model.set_data_comment(3, comment_dict, body_is_new['is_new'],
                                                           body_is_new['last_time_update'])


                    comm_page_path = driver.find_elements_by_class_name("u_cbox_page")

                    for k in range(len(comm_page_path) - 1):

                        comm_page_path = driver.find_elements_by_class_name("u_cbox_page")
                        comm_page_path[k].click()
                        time.sleep(1)
                        html_source = driver.page_source
                        soup = BeautifulSoup(html_source, 'lxml')

                        for l in range(len(soup.find_all("span", {"class": "u_cbox_nick"}))):

                            comment_dict = {
                                "unique_id": blogno,
                                "keyword": self.keyword,
                                "user_name": soup.find_all("span", {"class": "u_cbox_nick"})[l].text,
                                "comment_date": datetime.strptime(soup.find_all("span", {"class": "u_cbox_date"})[l].text,
                                                                  '%Y.%m.%d. %H:%M').strftime("%Y-%m-%d %H:%M:%S"),
                                "comment": self.db_model.addslashes(
                                    soup.find_all("span", {"class": "u_cbox_contents"})[l].text),
                                "comment_like": 0
                            }
                            time.sleep(1)

                            # 쿼리 / body_is_new여부에 따라 / 게시자의 댓글은 제외
                            if soup.find_all("span", {"class": "u_cbox_nick"})[l].text != user_name:
                                self.db_model.set_data_comment(3, comment_dict, body_is_new['is_new'],
                                                               body_is_new['last_time_update'])
                else :
                    self.stop_crawling += 1
                ## 5번 연속으로 키워드가 제목안에 없으면 크롤링 종료 2중 for문 break
                if self.stop_crawling == 5:
                    breaker = True
                    break


        print("Complete crawling of {} posts out of {} total post".format(get_post_num, num))
        self.db_model.set_daily_log('', '', row_id)
        driver.quit()

        return self.post_list , self.comment_list


if __name__ == "__main__":

    import time
    import argparse
    import db_model
    import naver_crawler
    from datetime import datetime, timedelta

    parser = argparse.ArgumentParser(description="Naver blog crawler")
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-w', '--one_week', action='store_true', help='Crawling post in the last week.')
    group.add_argument('-d', '--post_date', action='store_true', help='Crawling based on the post date.')

    parser.add_argument('keyword', type=str, help='Enter the keyword.')
    parser.add_argument('post_num', help='Enter the post number or ALL')
    parser.add_argument('option', help='Enter a date to crawl or crawl the last week.', nargs = "+")

    arg = parser.parse_args()
    keyword = arg.keyword
    post_num = arg.post_num

    if arg.one_week:
        start_time = (datetime.today() - timedelta(int(arg.option[0]))).strftime("%Y-%m-%d")
        end_time = datetime.today().strftime("%Y-%m-%d")

    elif arg.post_date:
        start_time = arg.option[0]
        end_time = arg.option[1]

    else :
        print('Please enter the argument option.')
        sys.exit()

    start = time.time()

    crawler = naver_crawler.navercrawler(keyword, start_time, end_time)

    post_list, comment_list = crawler.get_post_info(post_num)

    print("time :", time.time() - start)