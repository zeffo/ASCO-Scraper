
import json
import requests
from bs4 import BeautifulSoup as bsoup
target_urls = [] # get these URLs
from selenium import webdriver
import time
import csv
import datefinder
import re
from datetime import datetime

MAIN_URL = 'https://www.asco.org/research-guidelines/quality-guidelines/guidelines'
start = time.time()
errors = [] # log errors just in case
with open('config.json', 'r') as f:
    config = json.load(f)

filepath = config.get('output')
main_data = requests.get(MAIN_URL).text

def find_doi(driver: webdriver.Firefox): # extract UUID and date from page
    try: 
        doi = driver.find_element_by_xpath('//*[contains(translate(text(), "DOI", "doi"), "doi")]').text
        date = [d for d in datefinder.find_dates(doi)][0]
        uuid = 'DOI' + re.compile("doi(.*)$").search(doi.lower()).group(1)
        # print(uuid)
        return date.strftime('%d-%m-%Y'), uuid
    except:
        return None, None

soup = bsoup(main_data, 'html.parser')
t = soup.find('div', class_='menu-tiles three-col')
soup = bsoup(str(t.contents), 'html.parser')
links = [i.get('href') for i in soup.find_all('a')]
f = open(filepath, 'w')
csvw = csv.DictWriter(f, fieldnames=['ASCO guidelines by Clinical Area', 'Guideline Name', 'Publication Date', 'Guideline Status on ASCO website', 'Unique identifier','Script output date'])
csvw.writeheader()
for section in links:
    page = requests.get(f'https://www.asco.org{section}').text
    soup = bsoup(page, 'html.parser')
    labels = soup.find('div', class_='view-inner')
    soup = bsoup(str(labels), 'html.parser')
    articles = [t.get('href') for t in soup.find_all('a')]
    for guideline in articles:
        driver = webdriver.Firefox()
        driver.get(f'https://www.asco.org{guideline}')
        driver.implicitly_wait(config['wait'])
        title = driver.find_element_by_class_name('node-title')
        status = driver.find_element_by_css_selector('li.field-item.even')
        category = driver.find_element_by_id('page-title')
        date, uuid = find_doi(driver)
        if title and status and date and uuid and category:
            data = {'ASCO guidelines by Clinical Area': category.text, 'Guideline Name': title.text, 'Publication Date': date, 'Guideline Status on ASCO website': status.text, 'Unique identifier': uuid, 'Script output date': datetime.now().strftime('%d-%m-%Y')}
            csvw.writerow(data)
            print(f'Successfully Written: {", ".join(k+": "+v for k, v in data.items())}')
        else:
            errors.append(f'https://www.asco.org{guideline}')
            print(f'An error occurred while parsing: Title: {title.text if title else "ERROR"}, Status: {status.text if status else "ERROR"}, Category: {category.text if category else "ERROR"}, Date: {date if date else "ERROR"}, ID: {uuid if uuid else "ERROR"}. Page URL: https://www.asco.org{guideline}')
        
        driver.close()
f.close()
print(f'Finished parsing. Data saved to {filepath}. Time elapsed: {time.time()-start}. ')

with open(config['error_logs'], 'w') as f:
    f.writelines(errors)
        


