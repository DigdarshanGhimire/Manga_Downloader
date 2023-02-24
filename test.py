


















exit()
import requests
import multiprocessing as mp
import time

pages = []

def arrange_page_no(page_no):
    page_no = str(page_no)
    while len(page_no)<3:
        page_no = '0'+page_no
    return page_no

def process_one(page,inc):
    global pages
    url = f'https://scans-hot.leanbox.us/manga/Kingdom/0645-{arrange_page_no(page+inc)}.png'
    response = requests.get(url)
    if response.status_code != 404:
        global pages
        pages.append((page + inc,response))
        print(page+inc,response)
        return ((page + inc,response))
    print("It's False now")

    global run
    print(run)
    run = False
    print(run)

def get_pages():
    global pages
    pages.sort(key=lambda x: x[0])
    print(pages)

run = True
if __name__ == "__main__":
    page = 1
    start = time.time()
    while run:
        # p1 = mp.Process(target=process_one,args=(page,0))
        # p2 = mp.Process(target=process_one,args=(page,1))
        # p3 = mp.Process(target=process_one,args=(page,2))
        # p4 = mp.Process(target=process_one,args=(page,3))

        # p1.start()
        # p2.start()
        # p3.start()
        # p4.start()

        # p1.join()
        # p2.join()
        # p3.join()
        # p4.join()
        process_one(page,0)
        process_one(page,1)
        process_one(page,2)
        process_one(page,3)
        page += 4

    end = time.time()
    get_pages()
    print("Time Taken:",end-start,'seconds')
