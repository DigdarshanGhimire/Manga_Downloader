import requests
from PIL import Image
import os
from multiprocessing import Pool
from bs4 import BeautifulSoup
import time
from functools import partial
import io
import asyncio

class MangaScrapper:
    def __init__(self,manganame):
        #Status message
        self.message = "Success"

        #Assignments
        self.manganame = manganame.title().replace(' ','-')

        self.chap1url = f'https://manga4life.com/read-online/{self.manganame}-chapter-1-index-1.html'
        self.chapurl = f'https://manga4life.com/read-online/{self.manganame}-' + 'chapter-{chapternumber}-index-{index}.html'
        
        self.mainurlportion = 'https://{curpathname}/manga/'+self.manganame+'{directory}'
        self.chappageportion = '/{chapternumber}-{pagenumber}.png'

        #Getting manga poster
        self.mangaposterurl = f'https://temp.compsci88.com/cover/{self.manganame}.jpg'

        #Checking if the directories required exists
        self.required_dirs = ['manga_pages','manga_chapters_pdf','onedownloads']
        for dir in self.required_dirs:
            self.checkdir(dir)

        self.clear('manga_pages')

        t1 = time.time()
        r = self.get_pagescript(self.chap1url)
        print("Finished in: ", time.time()-t1,"seconds")

        if r!=True:
            self.__chapters = None
            return

        #Finding all the chapters in the manga
        self.__chapters = self.extract_pagedata(self.page_source,'vm.CHAPTERS = [{"Chapter"','vm.CHAPTERS = ')
        self.__chapters = self.convert_2_list(self.__chapters)
        self.__chapters.sort(key=lambda k: int(k['Chapter']))
        self.chapter_numbers()
    

    def clear(self,dir):
        pages = os.listdir('manga_pages')
        for page in pages:
            os.remove(f"{dir}/{page}")
    
    @property
    def poster(self):
        return self.request(self.mangaposterurl)

        
    def chapter_numbers(self):
        self.chapternumbers = []
        for chapter in self.chapters:
            chapnum = chapter['Chapter'][1:]
            chapnum = float(chapnum[:-1] + '.' + chapnum[-1])
            if (chapnum.is_integer()):
                chapnum = int(chapnum)
            chapnum = f"{chapter['Type']} {chapnum}"
            self.chapternumbers.append(chapnum)




    def convert_2_list(self,chaptersstring):
        chaptersstring = chaptersstring[1:-1]
        chapterlst = []
        dictionaryopened  = False
        quotations = [False,""]
        dictionary = {}
        key = value = ''
        keytime = True
        for character in chaptersstring:

            if quotations[1] == character:
                quotations = [False,""]
                if keytime==False:
                    dictionary[key] = value
                    keytime = True
                    key = value = ''
    
            
            elif quotations[0] == False:
                if character == '{':
                    dictionaryopened = True

                elif character == '}':
                    dictionary[key] = value
                    key = value = ''
                    keytime = True
                    chapterlst.append(dictionary)
                    dictionaryopened = False
                    dictionary = {}
                
                elif character in ['"',"'"]:
                    quotations = [True,character]
                
                elif character == ':':
                    keytime = False

            elif keytime:
                key = key + character

            else:
                value = value + character

        return chapterlst


    def find_chapter(self,chapter):
        return self.chapters[self.chapternumbers.index(chapter)]

    def find_curpath(self,chapter):
        print(chapter)
        index_lst = self.chapternumbers.index(chapter)
        index = self.find_chapter(chapter)['Chapter'][0]

        chapternumber = self.chapternumbers[index_lst].split(' ')[1]
        chapternumber = self.arrange_no(chapternumber,chapter=True)

        #Extracting the curpathname
        chapurl = self.chapurl.format(chapternumber=chapternumber,index=index)
        url_start_index = self.page_source.find('vm.CurPathName = "')
        url_end_index = url_start_index + self.page_source[url_start_index:].find(';')+1
        curpathname = self.page_source[url_start_index:url_end_index]
        curpathname = curpathname.split(' = ')[1][:-1]
        curpathname = curpathname.split('"')[1]
        self.curpathname = curpathname
        self.directory = self.find_chapter(chapter)['Directory']
        return chapternumber, int(self.find_chapter(chapter)['Page'])


    def fill_mainurl(self,curpathname,directory):
        if directory!='':
            directory = '/' + directory

        mainurlportion = self.mainurlportion.format(curpathname=curpathname,directory=directory)
        return mainurlportion
    

    def fill_chapurl(self,chapter,page):
        return self.chappageportion.format(chapternumber=self.arrange_no(chapter,chapter=True),pagenumber=self.arrange_no(page,page=True))

    @property
    def chapters(self):
        return self.__chapters

    def get_pagescript(self,url):
        try:
            response = requests.get(url)
            page_source = response.content.decode()

            soup = BeautifulSoup(page_source,'html.parser')
            if soup.title.string == '404 Page Not Found':
                self.message = "Either the manga doesn't exists or it is just not included in the manga4life site. Please try again with a valid name"
                print ("Either the manga doesn't exists or it is just not included in the manga4life site. Please try again with a valid name")

            self.page_source = page_source
            return True

        except requests.exceptions.ConnectionError:
            return "Internet Error"


    def merge_into_pdf(self,chaptername,dir='onedownloads',savedir='manga_chapters_pdf'):
        images = []
        for page in self.pageslist:
            img = Image.open(io.BytesIO(page))
            img_rgb = img.convert('RGB')
            images.append(img_rgb)
            print(images)

        first_image = images[0]
        try:
            first_image.save(f'{savedir}//{chaptername}.pdf',save_all=True,append_images=images[1:])
            return f"Download Successful of: {chaptername}.pdf"
        
        except IndexError:
            print("Something wrong happened")
        

    def download_one(self, chapter,fromdir='manga_pages',save_dir='onedownloads'):
        self.pageslist = []
        chapternumber, totalpages = self.find_curpath(chapter=chapter)
        pages = list(range(1,totalpages+1))
        p = Pool()
        self.pageslist = p.map(partial(self.download_one_page,chapternumber=chapternumber,savedir=fromdir,directdownload=False),pages)
        p.close()
        p.join()

        self.merge_into_pdf(self.arrange_no(chapternumber,chapter=True),dir='manga_pages',savedir='manga_chapters_pdf')
        del self.pageslist

    def download_one_page(self,pagenumber,chapternumber,savedir='onedownloads',directdownload=True):
        if (directdownload):
            chapternumber, totalpages = self.find_curpath(chapter=chapternumber)

        url = self.url(chapternumber,pagenumber)
        response = self.request(url)
        if response[0] == False:
            return response[1]

        if directdownload:
            with open(f'{savedir}/{self.arrange_no(chapternumber)}-{self.arrange_no(pagenumber)}.png','wb') as f:
                f.write(response[1].content)
                return f'Download of Chapter {chapternumber},Page {pagenumber} successful'

        return response[1].content


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
        istart = self.chapternumbers.index(str(chapterstart))
        iend = self.chapternumbers.index(str(chapterend))

        for i in range(istart,iend+1):
            self.download_one(self.chapternumbers[i])
    

    @staticmethod
    def arrange_no(no,chapter=False,page=False):
        no = str(no)
        d = ''
        if '.' in no:
            no,d = no.split('.')
            d = '.'+d

        if chapter:
            n = 4
        else:
            n = 3

        while len(no)<n:
            no = '0'+no
            
        return no + d


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
        return self.fill_mainurl(self.curpathname,self.directory) + self.fill_chapurl(chapter,page)                               