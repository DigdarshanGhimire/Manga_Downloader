# from playwright.sync_api import sync_playwright
# import time

# def handler(event):
#     print("Handling")

# def run(playwright):
#     chromium = playwright.chromium
#     browser = chromium.launch()
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto("https://manga4life.com/read-online/Kingdom-chapter-607.html")
#     time.sleep(10)
#     html = page.inner_html('.img-fluid')
#     print(html)
#     page.screenshot(path="screenshot.png")
#     browser.close()

# with sync_playwright() as playwright:
#     run(playwright)


import requests
import ast

def extract(string,find,removes=''):
    start_index = string.find(find)
    end_index = string[start_index:].find(';') + start_index

    string = string[start_index:end_index]
    string = string.replace(removes,'')

    return string

def rem_quotes(string):
    while '"' in string:
        string = string.replace('"','')
    return string


manganame = input("Enter manga name:- ")
manganame = manganame.replace(' ','-')


url = 'https://manga4life.com/read-online/{manganame}-chapter-1-index-1.html'
url = url.format(manganame=manganame)
print(url,'\n')


response = requests.get(url)
print(response.status_code)


with open('test.html','w') as f:
    f.write(response.content.decode())

#Getting the source code of the page as a string
page_source = response.content.decode()

#Getting the url of the manga source images

curpathname = extract(page_source,'vm.CurPathName = "',removes='vm.CurPathName = "')
curpathname = rem_quotes(curpathname)

url = 'https://{curpathname}/manga/{manganame}/{}-{}.png'
url = url.format(curpathname=curpathname,manganame=manganame,directory='')
url = 'https://' + url

print(url)

#Code to get total pages inside the chapter
chapter_data = extract(page_source,'vm.CurChapter = {"Chapter":','vm.CurChapter = ')
chapter_data = ast.literal_eval(chapter_data)
total_pages = chapter_data['Page']

#Code to get total number of chapters of that manga
chapters = extract(page_source,'vm.CHAPTERS = [{"Chapter"','vm.CHAPTERS = ')
print(chapters)

