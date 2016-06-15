#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Fang Zhang <thuzhf@gmail.com>

import os
from contextlib import contextmanager
from multiprocessing import Process
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import staleness_of

class Crawler:
    def __init__(self, timeout=10):
        phantomjs_service_args = [
            '--proxy-type=http',
            '--proxy=127.0.0.1:9007',
        ]
        self.timeout = timeout
        self.driver = webdriver.PhantomJS(service_args=phantomjs_service_args)
        self.driver.implicitly_wait(self.timeout)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()
    def close(self):
        self.driver.close()
    @contextmanager
    def wait_for_page_load(self, old_element):
        yield
        WebDriverWait(self.driver, self.timeout).until(staleness_of(old_element))

def scrape(url, scoreboards_dir):
    with Crawler() as crawler:
        d = crawler.driver
        d.get(url)
        title = d.title.replace(' - ', '-').replace(' ', '_')
        outfile = os.path.join(scoreboards_dir, title)
        if os.path.isfile(outfile):
            return
        with open(outfile, 'w') as f:
            f.write('rank\tnationality\tcontestant\tscore\n')
            while True:
                current_range = d.find_element_by_xpath('//*[@id="scb-range-links"]/span').text
                print('current range: {}'.format(current_range))
                table = d.find_element_by_id('scb-table-body')
                trs = table.find_elements_by_xpath('./tr')
                for tr in trs:
                    rank = tr.find_element_by_xpath('./td[1]').text.strip()
                    nationality = tr.find_element_by_xpath('./td[2]/img').get_attribute('title')
                    contestant = tr.find_element_by_xpath('./td[3]').text
                    score = tr.find_element_by_xpath('./td[4]').text
                    f.write('{}\t{}\t{}\t{}\n'.format(rank, nationality, contestant, score))
                next_range = d.find_element_by_xpath('//div[@id="scb-range-links"]/*[last()]')
                if next_range.get_attribute('class') == 'scb-range-active':
                    with crawler.wait_for_page_load(tr):
                        next_range.click()
                else: break

def main():
    urls_file = 'urls.txt'
    scoreboards_dir = './scoreboards'
    with open(urls_file) as urls:
        for url in urls:
            url = url.strip()
            if not url:
                continue
            print('{}'.format(url))
            if not url.startswith('#'):
                p = Process(target=scrape, args=(url, scoreboards_dir))
                p.start()

if __name__ == '__main__':
    main()
