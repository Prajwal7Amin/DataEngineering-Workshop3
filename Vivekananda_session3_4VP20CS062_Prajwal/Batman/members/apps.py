from django.apps import AppConfig
import psycopg2
import requests
import re
from bs4 import BeautifulSoup, element
import datetime
from dateutil.parser import parse


db_name = 'member_db2'
db_user = 'postgres'
db_pass = '123456'
db_host = 'psql-db2.0'
db_port = '5432'

conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_pass, host=db_host, port=db_port)


def add_row_to_blog(title, author, date, time):
    sql = """INSERT INTO members_blog (title, release_date, blog_time, author, created_date) VALUES (%s, %s::DATE, %s::TIME, %s, NOW())"""

    with conn:
        with conn.cursor() as curs:
            curs.execute(sql, (title, date, time, author, content, recommended, html))


def truncate_table():
    print("Truncating contents all the tables")
    with conn:
        with conn.cursor() as curs:
            curs.execute("TRUNCATE members_blog CASCADE;")


def start_extraction(start_date=None, end_date=None, no_of_articles=None, start_id=None):
    print("Extraction started")
    url = "https://blog.python.org/"

    data = requests.get(url)
    page_soup = BeautifulSoup(data.text, 'html.parser')

    if start_date:
        start_date = parse(start_date)
    if end_date:
        end_date = parse(end_date)

    blogs = page_soup.select('div.date-outer')
    truncate_table()
    article_count = 0
    counter = 1
    for blog in blogs:
        article_count += 1
        if start_id and article_count < int(start_id):
            continue
        if no_of_articles and counter > int(no_of_articles):
            continue
        date = blog.select('.date-header span')[0].get_text()

        converted_date = parse(date)

        if start_date and converted_date < start_date:
            continue
        if end_date and converted_date > end_date:
            continue

        post = blog.select('.post')[0]

        title = ""
        title_bar = post.select('.post-title')
        if len(title_bar) > 0:
            title = title_bar[0].text
        else:
            title = post.select('.post-body')[0].contents[0].text

        # getting the author and blog time
        post_footer = post.select('.post-footer')[0]

        author = post_footer.select('.post-author span')[0].text

        time = post_footer.select('abbr')[0].text

        post_header = post.select('.post-header')[0]
        
        '''contents = page_soup.find_all('div',class_='date-posts')
        #print(contents)
        for con in contents:'''
        content = post.select('.post-body')[0].text
        html = 'S:\web_scapping\python_blogs.html'
        with open(html, 'w', encoding='utf-8') as f:
            f.write(data.text)
        
       
        #con = content.find('p', class_='post-body entry-content').p.text
 
        #contents =post_header.select('div', class_='post-body entry-content')
        google = page_soup.find_all('div', class_='widget LinkList', id='LinkList1')
        # print(google)
        for gg in google:
           recommended = gg.select('.widget-content')[0].li.a['href']
            #rem2 = gg.find('div', class_='widget-content')
            #print(rem2)
        
        #print(rem2)
        # Inserting data into database
        add_row_to_blog(title, date, time, author, content, recommended, html)
        print("\nTitle:", title.strip('\n'))
        print(f'''Posted date: {date}
        Posted time: {time}
        Author: {author}
        Content: {content}
        Recommended this on google: {recommended}
        HTML saved to: {html}''')

        # print("Number of blogs read:", count)
        print(
            "\n---------------------------------------------------------------------------------------------------------------\n")
        counter += 1


if __name__ == "__main__":
    start_extraction()


class MembersConfig(AppConfig):
    name = 'members'