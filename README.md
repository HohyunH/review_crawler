# review_crawler

본 크롤러는 아이패밀리와 함께하는 "화장품 소비자 분석 시스템 프로젝트"의 일환으로 개발되었습니다.
본 저장소에서는 [네이버 블로그]와 [파우더룸] 사이트에 대한 크롤러를 공유합니다.

db_model_plus_pwd.py를 이용해 RBDMS를 통해 프로젝트 서버에 있는 Database에 연동되어 저장되는 코드입니다.

Local 환경에서 사용은 불가합니다.

## 1. Naver Blog Crawler

#### How to use

<pre>
<code>
python naver_arg_crawler.py --keyword [search keyword] --post_num [num or ALL] --one_week [input num_weeks]
python naver_arg_crawler.py --keyword [search keyword] --post_num [num or ALL] --pose_date [start_time, end_time]
</code>
</pre>

1. 데이터 수집 항목

![image](https://user-images.githubusercontent.com/46701548/139522149-e510f0c4-39c9-4136-a19c-24ff3b7181b2.png)

2. 데이터 수집
- 네이버의 경우 검색된 게시물의 정렬 기준을 관련성과 최신순 기준으로 정렬할 수 있다. 게시물을 관련성 기준으로 정렬할 때 초기에는 유의미한 게시물들이 나 오지만, 후반으로 갈수록 불필요한 게시물들이 많이 섞여 있는 것을 확인할 수 있다.
-  따라서 검색 키워드가 리뷰 게시물의 본문에 들어가 있지 않은 경우가 연속으로 특정 횟수만큼 나타난다면, 크롤링을 종료하도록 코드를 구성했다.

![image](https://user-images.githubusercontent.com/46701548/139522474-f3b8c53f-4abc-4852-a7ac-20d744171eaf.png)


## 2. Powder Room Crawler

#### How to use

<pre>
<code>
python pwd_arg_crawler.py --keyword [search keyword] --sort_type [POPULAR or LATEST] --post_num [num_of_post]
python pwd_arg_crawler.py --keyword [search keyword] --sort_type [POPULAR or LATEST] --pose_date [input_date]
</code>
</pre>

1. 데이터 수집 항목

![image](https://user-images.githubusercontent.com/46701548/139522613-e3d975be-f3b0-40a7-93e9-a4344cec5fee.png)

2. 데이터 수집
- 검색어를 입력하고 나오는 게시글들을 크롤링한다.
-  최신 기준과 관련성 기준으로 정렬하여 나오는 게시물들을 개수기반으로 크롤링하는 방법이 있고, 최신 기준으로 정렬했을 경우 날짜를 선정하여 그 날짜까지의 게시물들을 크롤링 하는 방법으로 코드를 구성했다.

![image](https://user-images.githubusercontent.com/46701548/139522630-c0a3defa-663d-4eec-b867-d699977079ac.png)
