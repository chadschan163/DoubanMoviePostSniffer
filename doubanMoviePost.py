# -*- coding: utf-8 -*-

import requests
import random
import string
from lxml import html as xhtml
from selenium import webdriver

douban_dict = {
    'search_url': 'https://movie.douban.com/subject_search?search_text=',
    'search_result_page_filter': '//div[starts-with(@class, "sc-bZQynM")][1]/div/a/@href',
    'movie_profile_page_filter': '//a[@class="nbgnbg"]/@href',
    'post_grid_page_filter': '//div[@class="cover"][1]/a/@href',
    'post_page_filter': '//img[@src]/@src'
}


def read_from_file(file_name):
    file = open(file_name, 'r', encoding='utf-8')
    name_list = []
    for line in file:
        if line != '\n':
            # print(line)
            line = line.strip('\n')
            name_list.append(line)
    file.close()
    print('成功获取到电影列表, 共计', len(name_list), '条')
    return name_list


def construct_douban_cookie():
    url = 'https://www.douban.com'
    bid_value = ''.join(random.sample(string.ascii_letters + string.digits, 11))
    cookie = requests.get(url).cookies
    cookie.pop('bid')
    c = requests.cookies.RequestsCookieJar()
    c.set('bid', bid_value, path='/', domain='.douban.com')
    cookie.update(c)
    return cookie


def init_web_driver():
    options = webdriver.ChromeOptions()
    options.set_headless()
    options.add_argument('--disable-gpu')
    options.add_argument('lang=zh_CN.UTF-8')
    options.add_argument(
        'user-agent="Mozilla/5.0 (X11; Linux x86_64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3080.5 Safari/537.36"')

    driver = webdriver.Chrome(options=options)
    return driver


def pars_static_page(url, xpath_filter):
    response = requests.get(url, cookies=construct_douban_cookie())
    page = xhtml.fromstring(response.content)
    parsed_url = page.xpath(xpath_filter)
    return parsed_url


def pars_dynamic_page(driver, url, xpath_filter):
    driver.get(url)
    page = xhtml.fromstring(driver.page_source)
    parsed_url = page.xpath(xpath_filter)
    return parsed_url


def join_douban_url(movie_name):
    return douban_dict['search_url'] + movie_name


def output_result(file_name, url_dict):
    if not url_dict:
        print('未写入文件。')
        return
    str = ''
    for key, url in url_dict.items():
        str += key + '\n' + url + '\n\n'
    file = open(file_name, 'w', encoding='utf-8')
    file.write(str)
    file.close()


def crawl(input_file, output_file):
    name_post_dict = {}
    driver = init_web_driver()
    name_list = read_from_file(input_file)
    success_count = 0
    failure_count = 0

    for name in name_list:
        try:
            profile_url = pars_dynamic_page(driver, join_douban_url(name), douban_dict['search_result_page_filter']).pop(0)
            post_grid_url = pars_static_page(profile_url, douban_dict['movie_profile_page_filter']).pop(0)
            post_page_url = pars_static_page(post_grid_url, douban_dict['post_grid_page_filter']).pop(0)
            img_url = pars_static_page(post_page_url, douban_dict['post_page_filter']).pop(0)
            name_post_dict[name] = img_url
            print('%-28s' % name, '获取成功：', img_url)
            success_count += 1

        except:
            print('%-20s' % name, '获取失败！')
            failure_count += 1
    print('获取成功总计：', success_count)
    print('获取失败总计：', failure_count)
    output_result(output_file, name_post_dict)


if __name__ == '__main__':
    crawl('test.txt', 'result.txt')
