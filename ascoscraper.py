import json
import requests
from bs4 import BeautifulSoup as bsoup
from selenium import webdriver
import csv
import datefinder
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

results = []

class Data:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

def get_metadata(url):
    driver = webdriver.Firefox()
    driver.get(url)
    title = driver.find_element_by_class_name('node-title')
    status = driver.find_element_by_css_selector('li.field-item.even')
    category = driver.find_element_by_id('page-title')
    try:
        metadata = driver.find_element_by_xpath("//div[@class='field-item even' and @property='content:encoded']//*[contains(translate(text(), 'doi', 'DOI'), 'DOI')]").text
    except:
        metadata = '-'
        print(url)
    print(metadata, '\n')
    results.append(Data(title=title.text, metadata=metadata, status=status, category=category, url=url))
    driver.close()

def sections():
    parser = bsoup(requests.get('https://www.asco.org/research-guidelines/quality-guidelines/guidelines').text, 'html.parser')
    for tag in parser.find('div', 'menu-tiles three-col'):
        if tag.name == 'a':
            yield 'https://www.asco.org' + tag.get('href')

def articles(url):
    parser = bsoup(requests.get(url).text, 'html.parser')
    sidebar = parser.find('div', 'view-inner')
    for tag in sidebar.find_all('a'):
        yield 'https://www.asco.org' + tag.get('href')

for url in sections():
    for article in articles(url):
        get_metadata(article)


