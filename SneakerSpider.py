#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from bs4 import BeautifulSoup
import requests
import urllib2
import cookielib
import random
from urlparse import urlparse

from useragent import UserAgent
ua = UserAgent()

class SneakerSpider:

    def __init__(self, root_save_dir, referer = None):
        self.root_dir = root_save_dir
        self.max_tries = 10;
        cookie_support = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
                    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
                    'Opera/9.25 (Windows NT 5.1; U; en)',
                    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
                    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
                    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
                    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
                    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
                    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 "]
        agent = random.choice(user_agents)
        opener.addheaders = [("User-agent", agent), ("Accept", "*/*"), ('Referer', 'http://www.baidu.com')]
        self.opener = opener
        self.referer = referer

    def getPage(self, url):
        num_tries = 0
        headers = {'User-Agent': ua.get()}
        if self.referer:
           headers['Referer'] = self.referer
        else :
           headers['Referer'] = urlparse(url).netloc

        response = None
        while num_tries < self.max_tries :
            try :
                response = requests.get(url, headers=headers, stream=True)
                break
            except Exception, e:
                print e
                num_tries += 1
        return response

    def getPage_urllib2(self, url):
        num_tries = 0
        headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
                  , 'Referer': url}
        if self.referer:
            headers['Referer'] = self.referer

        req = urllib2.Request(url, None, headers)
        res = None
        while num_tries < self.max_tries :
            try :
                res = urllib2.urlopen(req)
                break
            except Exception, e:
                print e
                num_tries += 1
        return res

    def getPage_withCookie(self,url):
        res = self.opener.open(url)
        return res

    def makeDir(self, path):
        isExistent = os.path.exists(path)
        if not isExistent :
            print "Making", path
            os.makedirs(path)
        else :
            print path+"exist"

    def saveImg(self, url, file_name):
            res = self.getPage_urllib2(url)
            data = res.read()
            f = open(file_name, 'wb')
            f.write(data)
            f.close()


    def getSneakers(self, root_url):
        pass

class NikeSpider(SneakerSpider):

    def __init__(self, root_save_dir, referer = None):
        SneakerSpider.__init__(self, root_save_dir, referer)

    def getSneakers(self, root_url):
        #get root page
        response_1 = self.getPage(root_url)
        soup_1 = BeautifulSoup(response_1.content.decode('utf-8','ignore'))
        #print soup_1.contents
        cnt = 0
        for tag_1 in soup_1.find_all(class_='grid-item fullSize'):
            cnt += 1
        #get the inside page:
            res_2 = self.getPage((tag_1.find(class_='grid-item-image-wrapper sprite-sheet sprite-index-0')).a['href'])
            soup_2 = BeautifulSoup(res_2.content.decode('utf-8','ignore'))
            tag_2 =  soup_2.find(class_='color-chip-container')
            shoes = soup_2.find(class_='exp-product-header')
            if shoes is None :
                continue
            shoes_name = shoes.h1.string
            shoes_name = ''.join(shoes_name.split())
            dir_path = self.root_dir + '/' + shoes_name + '/'
            isExistent = os.path.exists(dir_path)
            if not isExistent:
                print 'Making '+dir_path
                self.makeDir(dir_path)
                for li in tag_2.find_all('li'):
                     res_3 = self.getPage(li.a['href'])
                     soup_3 = BeautifulSoup(res_3.content.decode('utf-8','ignore'))
                     for tag_3 in soup_3.find_all(class_='exp-pdp-alt-image'):
                        img_url =  tag_3['data-medium-image']
                        file_path =  dir_path + (img_url.split('/'))[-1]
                        print 'Saving '+file_path
                        self.saveImg(img_url, file_path)
            else :
                print "Already has this shoe"
        print cnt

class AdidasSpider(SneakerSpider):

    def __init__(self, root_save_dir, referer = None):
        SneakerSpider.__init__(self, root_save_dir, referer)

    def getSneakers(self, root_url):
        #get root page
        merge_index_path = "/home/caffemaker/SneakerHead/New_SneakerImg/Adidas/merge_index"
        merge_index = open(merge_index_path, 'w+')
        res_1 = self.getPage_urllib2(root_url)
        soup_1 = BeautifulSoup(res_1.read())
        cnt = 0
        for tag_1 in soup_1.find_all(class_='productTileWrapper'):
            cnt += 1
        #get the inside page:
            res_2 = self.getPage_urllib2(tag_1.a['href'])
            soup_2 = BeautifulSoup(res_2.read())
            shoes = soup_2.find(class_='pdpTit')
            if shoes is None:
                continue
            sneaker_name = shoes.text
            sneaker_name = ''.join(sneaker_name.split())
            dir_path = self.root_dir + '/' + sneaker_name + '/'
            #print dir_path
            isExistent = os.path.exists(dir_path)
            if not isExistent:
                 print 'Making '+dir_path
                 self.makeDir(dir_path)
                 same_sneaker_tag = soup_2.find(class_ = 'pdpColorImg cf')
                 same_sneaker = same_sneaker_tag.find_all('a')
                 same_sneaker_num = len(same_sneaker)
                 if same_sneaker_num > 1 :
                     same_sneaker_index = ''
                     for sneaker in same_sneaker :
                        name = sneaker.img['title']
                        name = ''.join(name.split())
                        same_sneaker_index += name
                        same_sneaker_index += ' '
                     merge_index.write(same_sneaker_index.encode('gb2312')+'\n')
                 tag_2 = soup_2.find(class_ = 'pdpSmallImgSlids')
                 for a in tag_2.find_all('a'):
                    img_url = a.img['data-hero']
                    img_path = dir_path + (img_url.split('/'))[-1]
                    print 'Saving '+img_path
                    self.saveImg(img_url, img_path)
            else :
                 print "Already has this Sneaker"
        return cnt



class PumaSpider(SneakerSpider):

    def __init__(self, root_save_dir, referer = None):
        SneakerSpider.__init__(self, root_save_dir, referer)
        self.index = "http://cn.puma.com"
        self.product_id = 0

    def getSneakers(self, root_url):
        i = 0
        while i < 10 :
            cnt = 0
            try :
                res_1 = self.getPage_urllib2(root_url)
                soup_1 = BeautifulSoup(res_1.read())
                #print soup_1.contents
#get pr    oduct :
                for tag_1 in soup_1.find_all(class_='product-image-inner'):
                    cnt += 1
                    if cnt < self.product_id :
                        print "Already has this sneaker id"
                        continue
                #get the inside page:
                    product_url = self.index + tag_1.a['href']
                    res_2 = self.getPage_urllib2(product_url)
                    soup_2 = BeautifulSoup(res_2.read())
                    sneaker = soup_2.find(class_='about_tit')
                    if sneaker is None :
                        print "sneaker is none"
                        continue
                    sneaker_name = sneaker.text
                    print sneaker_name
                    sneaker_name = ''.join(sneaker_name.split())
                    dir_path = self.root_dir + '/' + sneaker_name + '/'
                    isExistent = os.path.exists(dir_path)
                    if not isExistent:
                        print 'Making '+dir_path
                        self.makeDir(dir_path)
                    #get different color:
                        tag_2 = soup_2.find('ul', class_='usa')
                        for li in tag_2.find_all('li'):
                            sneaker_url = self.index +'/'+li['skucode']+'/item'
                            res_3 = self.getPage_urllib2(sneaker_url)
                            soup_3 = BeautifulSoup(res_3.read())
                            tag_3 =  soup_3.find('ul', class_='swiper-wrapper')
                            for img_li in tag_3.find_all('li') :
                                img_url = 'http:'+ (img_li.img['src']).replace('80X80','540X540')
                                img_name = ((img_url.split('?'))[0].split('/'))[-1]
                                img_path = dir_path  + img_name
                                print 'Saving '+img_path
                                self.saveImg(img_url, img_path)
                    else :
                        print "Already has this sneaker dir"
                print cnt
                return cnt
                break
            except Exception, e:
                print e
                i += 1
                self.product_id = cnt

def PumaFromPumaStore():
    spider = PumaSpider('/home/caffemaker/SneakerHead/SneakerImg/PUMA', 'http://cn.puma.com/')
    url_list = ["http://cn.puma.com/productList.htm?loxiaflag=1464689225456&categories=%2Cmen%2Csneakers&isContent=false&row=60&gender=men&type=sneakers&size=&color=&lowPrice=&highPrice=&sort=&pageNumber=2&keyword="
               ,"http://cn.puma.com/productList.htm?loxiaflag=1464689225456&categories=%2Cmen%2Csneakers&isContent=false&row=60&gender=men&type=sneakers&size=&color=&lowPrice=&highPrice=&sort=&pageNumber=3&keyword="]
    s_num = 0
    for url in url_list :
        cnt = spider.getSneakers(url)
        s_num += cnt
    print s_num

class JD_spider(SneakerSpider):

    def __init__(self, root_save_dir, referer = None):
        SneakerSpider.__init__(self,root_save_dir, referer)

    def getSneakers(self,root_url):
        i = 0
        while i < 10:
            cnt = 0
            try :
                res_1 = self.getPage_urllib2(root_url)
                soup_1 = BeautifulSoup(res_1.read())
                for item in soup_1.find_all(class_="\\\"jItem\\\""):
                    cnt += 1
                    # item_url = "http:"+
                    sneaker = item.find(class_ = "\\\"jDesc\\\"")
                    if sneaker is None:
                        print "The sneaker is None"
                        continue
                    sneaker_name = sneaker.text
                    print sneaker_name
                    sneaker_name = ''.join(sneaker_name.split())
                    sneaker_name = ''.join(sneaker_name.split("\\n"))
                    sneaker_name = ''.join(sneaker_name.split("\\r"))
                    sneaker_name = ''.join(sneaker_name.split("/"))
                    dir_path = self.root_dir + '/' + sneaker_name + '/'
                    isExistent = os.path.exists(dir_path)
                    if not isExistent :
                        print "Making" + dir_path
                        self.makeDir(dir_path)
                    #different colors
                        scroll = item.find(class_ = "\\\"jScrollWrap\\\"")
                        for li in scroll.find_all("li"):
                            item_url = "http:"+(li['data-href'])[2:-2]
                            res_2 = self.getPage_urllib2(item_url)
                            soup_2 = BeautifulSoup(res_2)
                            tag_2 = soup_2.find(class_ = "spec-items")
                            for li_img in tag_2.find_all("li"):
                                prim_img_url = (li_img.img['src']).replace("n5", "n1")
                                prim_img_url =  prim_img_url.replace("54x54", "350x350")
                                img_url = "http:"+prim_img_url
                                print img_url
                                img_name = (img_url.split("/"))[-1]
                                img_path = dir_path + img_name
                                print "Saving: "+img_path
                                self.saveImg(img_url,img_path)
                    else :
                        print "Already has this Sneaker"
                print cnt
                return cnt
            except Exception, e :
                print e
                i += 1

class JD_NBspider(SneakerSpider):

    def __init__(self, root_save_dir, referer = None):
        SneakerSpider.__init__(self,root_save_dir, referer)

    def getSneakers(self,root_url):
        i = 0
        while i < 10:
            cnt = 0
            try :
                res_1 = self.getPage_urllib2(root_url)
                soup_1 = BeautifulSoup(res_1.read())
                for item in soup_1.find_all(class_="\\\"jPic\\\""):
                    cnt += 1
                    item_url = "http:" + (item.a['href'])[2:-2]
                    res_2 = self.getPage_urllib2(item_url)
                    soup_2 = BeautifulSoup(res_2.read())
                    sneaker = soup_2.find(class_ = "sku-name")
                    if sneaker is None:
                        print "The sneaker is None"
                        continue
                    sneaker_name = sneaker.text
                    print sneaker_name
                    sneaker_name = ''.join(sneaker_name.split())
                    sneaker_name = ''.join(sneaker_name.split("\\n"))
                    sneaker_name = ''.join(sneaker_name.split("\\r"))
                    sneaker_name = ''.join(sneaker_name.split("/"))
                    dir_path = self.root_dir + '/' + sneaker_name + '/'
                    isExistent = os.path.exists(dir_path)
                    if not isExistent :
                        print "Making" + dir_path
                        self.makeDir(dir_path)
                    #different colors
                        # scroll = item.find(class_ = "\\\"jScrollWrap\\\"")
                        # for li in scroll.find_all("li"):
                            # item_url = "http:"+(li['data-href'])[2:-2]
                            # res_2 = self.getPage_urllib2(item_url)
                            # soup_2 = BeautifulSoup(res_2)
                        tag_2 = soup_2.find(class_ = "spec-items")
                        for li_img in tag_2.find_all("li"):
                            prim_img_url = (li_img.img['src']).replace("n5", "n1")
                            prim_img_url =  prim_img_url.replace("54x54", "350x350")
                            img_url = "http:"+prim_img_url
                            print img_url
                            img_name = (img_url.split("/"))[-1]
                            img_path = dir_path + img_name
                            print "Saving: "+img_path
                            self.saveImg(img_url,img_path)
                    else :
                        print "Already has this Sneaker"
                print cnt
                return cnt
            except Exception, e :
                print e
                i += 1
def AdidasFromAdidasStore() :
    spider = AdidasSpider('/home/caffemaker/SneakerHead/New_SneakerImg/Adidas')
    url_list = ['http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=1'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=2'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=3'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=4'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=5'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=6'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=7'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=8'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=9'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=10'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=11'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=12'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=13'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=14'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=15'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=16'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=17'
                ,'http://www.adidas.com.cn/specific/ajaxproductlist/productlist/?sport_gender=39&product_style=215&dir=&limit=&order=&p=18' ]
    sneaker_num = 0
    for url in url_list:
        cnt = spider.getSneakers(url)
        sneaker_num += cnt
    print sneaker_num

def SauconyFromJD():
    spider = JD_spider("/home/caffemaker/SneakerHead/New_SneakerImg/Saucony")
    url_list = ["http://module-jshop.jd.com/module/getModuleHtml.html?appId=396546&orderBy=5&direction=1&keyword=%25E5%25A4%258D%25E5%258F%25A4&categoryId=2514823&pageSize=24&venderId=122538&domainKey=saucony&isGlobalSearch=1&maxPrice=0&pagePrototypeId=17&pageNo=1&shopId=119173&minPrice=0&pageInstanceId=18811382&moduleInstanceId=42083068&prototypeId=68&templateId=401682&layoutInstanceId=42083068&origin=0&callback=jshop_module_render_callback&_=1465129236818"
               , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=396546&orderBy=5&direction=1&keyword=%25E5%25A4%258D%25E5%258F%25A4&categoryId=2514823&pageSize=24&venderId=122538&domainKey=saucony&isGlobalSearch=1&maxPrice=0&pagePrototypeId=17&pageNo=2&shopId=119173&minPrice=0&pageInstanceId=18811382&moduleInstanceId=42083068&prototypeId=68&templateId=401682&layoutInstanceId=42083068&origin=0&callback=jshop_module_render_callback&_=1465129236818"
               , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=396546&orderBy=5&direction=1&keyword=%25E5%25A4%258D%25E5%258F%25A4&categoryId=2514823&pageSize=24&venderId=122538&domainKey=saucony&isGlobalSearch=1&maxPrice=0&pagePrototypeId=17&pageNo=3&shopId=119173&minPrice=0&pageInstanceId=18811382&moduleInstanceId=42083068&prototypeId=68&templateId=401682&layoutInstanceId=42083068&origin=0&callback=jshop_module_render_callback&_=1465129236818"
               , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=396546&orderBy=5&direction=1&keyword=%25E5%25A4%258D%25E5%258F%25A4&categoryId=2514823&pageSize=24&venderId=122538&domainKey=saucony&isGlobalSearch=1&maxPrice=0&pagePrototypeId=17&pageNo=4&shopId=119173&minPrice=0&pageInstanceId=18811382&moduleInstanceId=42083068&prototypeId=68&templateId=401682&layoutInstanceId=42083068&origin=0&callback=jshop_module_render_callback&_=1465129236818"]
    sneaker_num = 0
    for url in url_list :
        cnt = spider.getSneakers(url)
        sneaker_num += cnt
    print sneaker_num

def NBFromJD():
    spider = JD_NBspider("/home/caffemaker/SneakerHead/New_SneakerImg/NB")
    url_list = ["http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=1&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=2&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=3&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=4&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=5&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=6&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=7&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=8&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=9&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=10&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=11&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=12&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=13&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=14&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=15&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=16&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=17&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=18&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=19&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                , "http://module-jshop.jd.com/module/getModuleHtml.html?appId=211751&orderBy=1&direction=0&categoryId=1243970&pageSize=20&venderId=64877&isGlobalSearch=0&domainKey=newbalance&maxPrice=0&pagePrototypeId=17&pageNo=20&shopId=60920&minPrice=0&pageInstanceId=8376133&moduleInstanceId=42939718&prototypeId=52&templateId=402645&layoutInstanceId=42939718&origin=0&callback=jshop_module_render_callback&_=1465137174762"
                ]
    sneaker_num = 0
    for url in url_list :
        cnt = spider.getSneakers(url)
        sneaker_num += cnt
    print sneaker_num

def Onitsuka_TigerFromJD():
    spider = JD_spider("/home/caffemaker/SneakerHead/New_SneakerImg/Onitsuka_Tiger")
    url_list = ["http://module-jshop.jd.com/module/getModuleHtml.html?other=&appId=129442&orderBy=5&direction=0&categoryId=707598&pageSize=20&venderId=42602&domainKey=onitsukatiger&isGlobalSearch=0&maxPrice=0&pagePrototypeId=17&pageNo=1&shopId=40059&minPrice=0&pageInstanceId=4240209&moduleInstanceId=42081060&prototypeId=75&templateId=414060&layoutInstanceId=42081060&origin=0&callback=jshop_module_render_callback&_=1465132124483"
            , "http://module-jshop.jd.com/module/getModuleHtml.html?other=&appId=129442&orderBy=5&direction=0&categoryId=707598&pageSize=20&venderId=42602&domainKey=onitsukatiger&isGlobalSearch=0&maxPrice=0&pagePrototypeId=17&pageNo=2&shopId=40059&minPrice=0&pageInstanceId=4240209&moduleInstanceId=42081060&prototypeId=75&templateId=414060&layoutInstanceId=42081060&origin=0&callback=jshop_module_render_callback&_=1465132124483"
            , "http://module-jshop.jd.com/module/getModuleHtml.html?other=&appId=129442&orderBy=5&direction=0&categoryId=707598&pageSize=20&venderId=42602&domainKey=onitsukatiger&isGlobalSearch=0&maxPrice=0&pagePrototypeId=17&pageNo=3&shopId=40059&minPrice=0&pageInstanceId=4240209&moduleInstanceId=42081060&prototypeId=75&templateId=414060&layoutInstanceId=42081060&origin=0&callback=jshop_module_render_callback&_=1465132124483"
            , "http://module-jshop.jd.com/module/getModuleHtml.html?other=&appId=129442&orderBy=5&direction=0&categoryId=707598&pageSize=20&venderId=42602&domainKey=onitsukatiger&isGlobalSearch=0&maxPrice=0&pagePrototypeId=17&pageNo=4&shopId=40059&minPrice=0&pageInstanceId=4240209&moduleInstanceId=42081060&prototypeId=75&templateId=414060&layoutInstanceId=42081060&origin=0&callback=jshop_module_render_callback&_=1465132124483"
            , "http://module-jshop.jd.com/module/getModuleHtml.html?other=&appId=129442&orderBy=5&direction=0&categoryId=707598&pageSize=20&venderId=42602&domainKey=onitsukatiger&isGlobalSearch=0&maxPrice=0&pagePrototypeId=17&pageNo=5&shopId=40059&minPrice=0&pageInstanceId=4240209&moduleInstanceId=42081060&prototypeId=75&templateId=414060&layoutInstanceId=42081060&origin=0&callback=jshop_module_render_callback&_=1465132124483"
            , "http://module-jshop.jd.com/module/getModuleHtml.html?other=&appId=129442&orderBy=5&direction=0&categoryId=707598&pageSize=20&venderId=42602&domainKey=onitsukatiger&isGlobalSearch=0&maxPrice=0&pagePrototypeId=17&pageNo=6&shopId=40059&minPrice=0&pageInstanceId=4240209&moduleInstanceId=42081060&prototypeId=75&templateId=414060&layoutInstanceId=42081060&origin=0&callback=jshop_module_render_callback&_=1465132124483"]
    sneaker_num = 0
    for url in url_list :
        cnt = spider.getSneakers(url)
        sneaker_num += cnt
    print sneaker_num

# spider = NikeSpider('/home/caffemaker/SneakerHead/SneakerImg/Nike', 'http://store.nike.com/')
# spider.getSneakers("http://store.nike.com/cn/zh_cn/pw/%E7%94%B7%E5%AD%90-%E9%9E%8B%E7%B1%BB/7puZoi3?ipp=461")
# PumaFromPumaStore()
# AdidasFromAdidasStore()
NBFromJD()
# SauconyFromJD()
# Onitsuka_TigerFromJD()
