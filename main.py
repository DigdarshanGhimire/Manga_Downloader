import requests
from PIL import Image
import os
import ast
from bs4 import BeautifulSoup

class MangaScrapper:
    def __init__(self,manganame):
        #Assignments
        self.manganame = manganame.replace(' ','-')

        self.chap1url = f'https://manga4life.com/read-online/{self.manganame}-chapter-1-index-1.html'
        self.chapurl = 'https://manga4life.com/read-online/{manganame}-chapter-{chapternumber}-index-{index}.html'
        
        self.mainurlportion = 'https://{curpathname}/manga/{manganame}{directory}'
        self.chappageportion = '{chapternumber}-{pagenumber}.png'

        #Checking if the directories required exists
        self.checkdir('manga_pages')
        self.checkdir('manga_chapters_pdf')
        self.checkdir ('onedownloads')

        r = self.get_pagescript(self.chap1url)
        if r!=True:
            self.__chapters = None
            return

        #Finding domain of the image
        self.__chapters = self.extract_pagedata(self.page_source,'vm.CHAPTERS = [{"Chapter"','vm.CHAPTERS = ')

    
    def fill_url(self,curpathname,manganame,directory):
        if directory!='':
            directory = '/' + directory

        mainurlportion = self.mainurlportion.format(curpathname=curpathname,manganame=manganame,directory=directory)
        return mainurlportion

    @property
    def chapters(self):
        return self.__chapters


    def manage_chap_url(self):
        self.chapurl


    def get_pagescript(self,url):
        try:
            response = requests.get(url)
            page_source = response.content.decode()

            soup = BeautifulSoup(page_source,'html.parser')
            if soup.title.string == '404 Page Not Found':
                print("Either the manga doesn't exists or it is just not included in the manga4life site")
                return "404"

            self.page_source = page_source
            return True

        except requests.exceptions.ConnectionError:
            return "Internet Error"
        


    def merge_into_pdf(self,chaptername,savedir='manga_chapters_pdf'):
        images = []
        pages = os.listdir('manga_pages')
        for page in pages:
            imgsrc = f'manga_pages//{page}'
            # print(imgsrc)
            img = Image.open(imgsrc)
            img_rgb = img.convert('RGB')
            images.append(img_rgb)
            os.remove(imgsrc)

        try:
            first_image = images[0]
            first_image.save(f'{savedir}//{chaptername}.pdf',save_all=True,append_images=images[1:])
        
        except IndexError:
            pass
        
        

    def download_one(self, chapternumber,savedir='onedownloads'):
        page = 1
        while True:
            r = self.download_one_page(chapternumber,page)
            if r=='breaktime':
                break

            page += 1

        self.merge_into_pdf(self.arrange_no(chapternumber,chapter=True))


    def download_one_page(self,chapternumber,pagenumber,savedir='onedownloads'):
        url = self.url(chapternumber,pagenumber)
        response = self.request(url)
        if response[0] == False:
            return 'breaktime'
        print(url)

        with open(f'{savedir}/{self.arrange_no(chapternumber)}-{self.arrange_no(pagenumber)}.png','wb') as f:
            f.write(response[1].content)


    def extract_pagedata(self,string,find,remove):
        start_index = string.find(find)
        end_index = string[start_index:].find(';') + start_index

        string = string[start_index:end_index]
        string = string.replace(remove,'')

        return string    
    

    def rem_quotes(self,string):
        if '"' in string[0] and '"' in string[-1]:
            return string[1:-1]


    def download_many(self, chapterstart, chapterend):
        for chapter in range(chapterstart,chapterend+1):
            self.download_one(chapter)
    
    @staticmethod
    def arrange_no(no,chapter=False,page=False):
        no = str(no)
        if chapter:
            n = 4
        else:
            n = 3

        while len(no)<n:
            no = '0'+no

        return no

    @staticmethod
    def request(url):
        try:
            response = requests.get(url)
            if response.status_code == 404:
                return False,'Page not found'
            return True,response

        except requests.exceptions.ConnectionError:
            return False,"No Connection"

    @staticmethod
    def checkdir(dirname):
        try:
            os.mkdir(dirname)
        except FileExistsError:
            return True

    def url(self,chapter,page):
        return self.chappageportion.format(chapternumber=self.arrange_no(chapter,chapter=True),pagenumber=self.arrange_no(page,page=True))
                                

if __name__ == "__main__":
    scrapper = MangaScrapper('Wingdom')
    print(scrapper.chapters)

    # scrapper.download_many(10,14)
