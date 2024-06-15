# -*- coding: UTF8 -*-

from contextlib import closing
import requests
import json
import os
import re
from aligo import Aligo,set_config_folder
def login_ali():
    set_config_folder('plugins/neteasy')
    ali = Aligo(name="zhao_config")  # 第一次使用，会弹出二维码，供扫描登录

    return ali

def upload_aliyun(srcfile,destfile):
    ali=login_ali()
    remote_folder = ali.get_folder_by_path(destfile)
    if remote_folder is None:
        raise RuntimeError('指定的文件夹不存在')
    ali.upload_file(srcfile, parent_file_id=remote_folder.file_id)

    # user = ali.get_user()
    # ll = ali.get_file_list()
    # # 遍历列表
    # for file in ll:
    #     # 搜索你的网盘文件夹目录
    #     if (file.name == destfile):
    #         checkupId = file.file_id
    #         print('目录TestId:', checkupId)
    #         # 打包文件
    #         #up_file = ali.upload_file(srcfile, checkupId)
    #         up_file = ali.upload_file(srcfile, "网易视频")
    #         return True
    #         print(up_file)
    return  True


def downloadneteasy(url):

    s=requests.session()
    try:
        ret=s.get(url)
        ret_json = ret.json()

    except Exception as e:
        print('not json data')

        print(ret.content)
        return None




    return ret_json

class SaveVideo():
    LessonList = []

    def __init__(self):
        pass


    def getVideo(self, url):
        '''
        获取视频
        '''
        d = self.pq(url)
        DomTree = d("iframe")
        jsonData = DomTree.attr('data')
        video=''
        try:
            objectid = json.loads(jsonData)['objectid']  # 获取下载资源视频的对象
            downloadUrl = self.pq('http://ptr.chaoxing.com/ananas/status/' + objectid)  # 获取下载资源的URL
            video = json.loads(downloadUrl.html())['httphd']  # 在这里，我们要下载的是高清视频
        except:
            pass
        return video

    def pq(self, url, headers=None):
        '''
        将PyQuery 请求写成方法
        '''
        d = self.pq(url=url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'})
        return d

    def downloadVideo(self, url, file_name=''):
        '''
        下载视频
        :param url: 下载url路径
        :return: 文件
        '''
        with closing(requests.get(url, stream=True)) as response:
            chunk_size = 1024*1024
            content_size = int(response.headers['content-length'])
            path=os.getcwd()
            print(path)
            if not os.path.exists(os.path.join(path,"video")):
                os.makedirs(os.path.join(path,"video"),exist_ok=True)
            file_D=os.path.join(path,"video",file_name+".mp4")
            print(file_D)
            #file_D='video/' + file_name + '.mp4'
            if(os.path.exists(file_D)  and os.path.getsize(file_D)==content_size):
                print('跳过'+file_name)
                return False,'已经存在！',file_D
            else:
                progress = ProgressBar(file_name, total=content_size, unit="MB", chunk_size=chunk_size, run_status="正在下载",fin_status="下载完成")
                with open(file_D, "wb") as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        file.write(data)
                        progress.refresh(count=len(data))
                return True,file_name,file_D
'''
下载进度
'''
class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0, unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (
            self.title, self.status, self.count / self.chunk_size, self.unit, self.seq, self.total / self.chunk_size,
            self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)

def parse_videourl_qq(message):
    pattern = re.compile(r'https?://c\.m\.163\.com/[^\s<>"]+')

    matches = pattern.findall(message)
    newvideourl=""
    # print(matches)
    if len(matches) >= 1:
        print(matches[0][:-1])
        videourl=matches[0][:-1]
        keys1 = '.html?spss=newsapp'
        keys2 = "/"

        # pos1 = videourl.find(keys2)
        pos2 = videourl.find(keys1)
        pos1 = videourl.rfind(keys2)
        videoindicate = videourl[pos1 + 1:pos2]
        print(videoindicate)
        newvideourl = "https://gw.m.163.com/nc-gateway/api/v1/video/detail/" + videoindicate
        print(newvideourl)
        #return newvideourl
    return newvideourl

    key1='CQ:json,data='
    pos1 = message.find(key1)
    message=message[pos1+len(key1):-1]
    #print(message)
    json_ret=None
    try:
        json_ret=json.loads(message.replace("&#44","").replace(";",','))
    except Exception as e:
        print(e)
    if json_ret!=None:
        print(json_ret['meta']['news']['jumpUrl'])
        keys1 = '.html?spss=newsapp'
        keys2 = "/"
        videourl=json_ret['meta']['news']['jumpUrl']
        # pos1 = videourl.find(keys2)
        pos2 = videourl.find(keys1)
        pos1 = videourl.rfind(keys2)
        videoindicate = videourl[pos1 + 1:pos2]
        print(videoindicate)
        newvideourl = "https://gw.m.163.com/nc-gateway/api/v1/video/detail/" + videoindicate
        print(newvideourl)
        return newvideourl
    else:
        return None


def parse_videourl(message):


    pos1 = message.find("<url>")
    pos2 = message.find("</url>")
    videourl = message[pos1 + 5:pos2]
    print(videourl)
    keys1 = '.html?spss=newsapp'
    keys2 = "/"
    #pos1 = videourl.find(keys2)
    pos2 = videourl.find(keys1)
    pos1=videourl.rfind(keys2)
    videoindicate = videourl[pos1 + 1:pos2]
    print(videoindicate)
    newvideourl = "https://gw.m.163.com/nc-gateway/api/v1/video/detail/"+videoindicate
    print(newvideourl)
    return  newvideourl
def download_163news(message):
    videourl = parse_videourl_qq(message)
    if videourl!='':
        ret_json = downloadneteasy(videourl)
        if ret_json != None:
            title = ret_json['data']['title']
            mp4_url = ret_json['data']['mp4_url']
            m3u8_url = ret_json['data']['m3u8_url']
            topicImg = ret_json['data']['topicImg']
            vid = ret_json['data']['vid']
            print(title)
            print(mp4_url)
            print(m3u8_url)
            print(topicImg)
            C = SaveVideo()
            title = re.sub(r'[~`!@#$%^&*()_“”：\-+=|\\{\}\[\]:;\"\'<>,.?/·！￥…（）—【】、？《》，。]+', '_', title)
            retcode,filename,filepath = C.downloadVideo(mp4_url, file_name=title)


            return  retcode,filename,filepath


if __name__ == '__main__':

    filepath = r'D:\pysrc\wechatbot\chatgpt-on-wechat-ipad\plugins\neteasy\video\美国一警察执勤时拍不雅短剧_被捕后被控两项重罪.mp4'
    upload_aliyun(filepath, '网易视频')
    exit(0)
    message = '''
        <?xml version=\"1.0\"?>\n<msg>\n\t<appmsg appid=\"wx7be3c1bb46c68c63\" sdkver=\"0\">\n\t\t<title>\344\270\215\346\204\247\346\230\257\351\241\266\347\272\247\346\250\241\347\211\271\357\274\214\350\272\253\346\235\220\350\204\270\350\233\213\351\203\275\346\230\257\345\245\263\347\245\236\347\272\247\345\210\253\347\232\204\357\274\214\347\234\237\347\232\204\345\244\252\347\276\216\344\272\206\357\274\201</title>\n\t\t<des>\345\210\206\344\272\253\347\275\221\346\230\223\350\247\206\351\242\221\343\200\212\344\270\215\346\204\247\346\230\257\351\241\266\347\272\247\346\250\241\347\211\271\357\274\214\350\272\253\346\235\220\350\204\270\350\233\213\351\203\275\346\230\257\345\245\263\347\245\236\347\272\247\345\210\253\347\232\204\357\274\214\347\234\237\347\232\204\345\244\252\347\276\216\344\272\206\357\274\201\343\200\213</des>\n\t\t<username />\n\t\t<action>view</action>\n\t\t<type>4</type>\n\t\t<showtype>0</showtype>\n\t\t<content />\n\t\t<url>https://c.m.163.com/news/v/VVBTJ0HT3.html?spss=newsapp</url>\n\t\t<lowurl />\n\t\t<dataurl />\n\t\t<lowdataurl />\n\t\t<contentattr>0</contentattr>\n\t\t<streamvideo>\n\t\t\t<streamvideourl />\n\t\t\t<streamvideototaltime>0</streamvideototaltime>\n\t\t\t<streamvideotitle />\n\t\t\t<streamvideowording />\n\t\t\t<streamvideoweburl />\n\t\t\t<streamvideothumburl />\n\t\t\t<streamvideoaduxinfo />\n\t\t\t<streamvideopublishid />\n\t\t</streamvideo>\n\t\t<canvasPageItem>\n\t\t\t<canvasPageXml><![CDATA[]]></canvasPageXml>\n\t\t</canvasPageItem>\n\t\t<appattach>\n\t\t\t<attachid />\n\t\t\t<cdnthumburl>308186020100047a307802010002040745f51302032f50e70204ef192e70020460ce158904536175706170706d73675f653436343064343331643237316537655f313632343131383636353731385f36383433385f63646361366165352d623665362d346537642d623030372d6362656334633339313530330204010400030201000405004c52af00</cdnthumburl>\n\t\t\t<cdnthumbmd5>da287030f772d28abc8e31f1dae21eae</cdnthumbmd5>\n\t\t\t<cdnthumblength>8835</cdnthumblength>\n\t\t\t<cdnthumbheight>68</cdnthumbheight>\n\t\t\t<cdnthumbwidth>120</cdnthumbwidth>\n\t\t\t<cdnthumbaeskey>51d60be513399b485ac91f1aa43033dd</cdnthumbaeskey>\n\t\t\t<aeskey>51d60be513399b485ac91f1aa43033dd</aeskey>\n\t\t\t<encryver>1</encryver>\n\t\t\t<fileext />\n\t\t\t<islargefilemsg>0</islargefilemsg>\n\t\t</appattach>\n\t\t<extinfo />\n\t\t<androidsource>3</androidsource>\n\t\t<thumburl />\n\t\t<mediatagname />\n\t\t<messageaction><![CDATA[]]></messageaction>\n\t\t<messageext><![CDATA[]]></messageext>\n\t\t<emoticongift>\n\t\t\t<packageflag>0</packageflag>\n\t\t\t<packageid />\n\t\t</emoticongift>\n\t\t<emoticonshared>\n\t\t\t<packageflag>0</packageflag>\n\t\t\t<packageid />\n\t\t</emoticonshared>\n\t\t<designershared>\n\t\t\t<designeruin>0</designeruin>\n\t\t\t<designername>null</designername>\n\t\t\t<designerrediretcturl>null</designerrediretcturl>\n\t\t</designershared>\n\t\t<emotionpageshared>\n\t\t\t<tid>0</tid>\n\t\t\t<title>null</title>\n\t\t\t<desc>null</desc>\n\t\t\t<iconUrl>null</iconUrl>\n\t\t\t<secondUrl>null</secondUrl>\n\t\t\t<pageType>0</pageType>\n\t\t</emotionpageshared>\n\t\t<webviewshared>\n\t\t\t<shareUrlOriginal />\n\t\t\t<shareUrlOpen />\n\t\t\t<jsAppId />\n\t\t\t<publisherId />\n\t\t</webviewshared>\n\t\t<template_id />\n\t\t<md5>da287030f772d28abc8e31f1dae21eae</md5>\n\t\t<weappinfo>\n\t\t\t<username />\n\t\t\t<appid />\n\t\t\t<appservicetype>0</appservicetype>\n\t\t\t<secflagforsinglepagemode>0</secflagforsinglepagemode>\n\t\t\t<videopageinfo>\n\t\t\t\t<thumbwidth>120</thumbwidth>\n\t\t\t\t<thumbheight>68</thumbheight>\n\t\t\t\t<fromopensdk>0</fromopensdk>\n\t\t\t</videopageinfo>\n\t\t</weappinfo>\n\t\t<statextstr>GhQKEnd4N2JlM2MxYmI0NmM2OGM2Mw==</statextstr>\n\t\t<musicShareItem>\n\t\t\t<musicDuration>0</musicDuration>\n\t\t</musicShareItem>\n\t\t<findernamecard>\n\t\t\t<username />\n\t\t\t<avatar><![CDATA[]]></avatar>\n\t\t\t<nickname />\n\t\t\t<auth_job />\n\t\t\t<auth_icon>0</auth_icon>\n\t\t\t<auth_icon_url />\n\t\t</findernamecard>\n\t\t<finderGuarantee>\n\t\t\t<scene><![CDATA[0]]></scene>\n\t\t</finderGuarantee>\n\t\t<directshare>0</directshare>\n\t\t<gamecenter>\n\t\t\t<namecard>\n\t\t\t\t<iconUrl />\n\t\t\t\t<name />\n\t\t\t\t<desc />\n\t\t\t\t<tail />\n\t\t\t\t<jumpUrl />\n\t\t\t</namecard>\n\t\t</gamecenter>\n\t\t<patMsg>\n\t\t\t<chatUser />\n\t\t\t<records>\n\t\t\t\t<recordNum>0</recordNum>\n\t\t\t</records>\n\t\t</patMsg>\n\t\t<websearch>\n\t\t\t<rec_category>0</rec_category>\n\t\t\t<channelId>0</channelId>\n\t\t</websearch>\n\t</appmsg>\n\t<fromusername>zhaokaihui123</fromusername>\n\t<scene>0</scene>\n\t<appinfo>\n\t\t<version>73</version>\n\t\t<appname>\347\275\221\346\230\223\346\226\260\351\227\273</appname>\n\t</appinfo>\n\t<commenturl></commenturl>\n</msg>\n
        '''
    message1='''
"<?xml version='1.0'?>\n<msg>\n\t<appmsg appid='wx7be3c1bb46c68c63' sdkver='0'>\n\t\t<title>美国一警察执勤时拍不雅短剧，被捕后被控两项重罪</title>\n\t\t<des>分享网易视频《美国一警察执勤时拍不雅短剧，被捕后被控两项重罪》</des>\n\t\t<username />\n\t\t<action>view</action>\n\t\t<type>4</type>\n\t\t<showtype>0</showtype>\n\t\t<content />\n\t\t<url>https://c.m.163.com/news/sv/VE3NTMK5P.html?spss=newsapp&amp;spsnuid=yxEDNniygRH%2BLOTZ9DRcI1b6LleXCC%2BCkap%2FSMUSf1E%3D&amp;spsdevid=CQk0MTIxYWVmYWNhZTBiZmQ3CU44SzVUMTcxMjYwMjkzNjk%253D&amp;spsvid=&amp;spsshare=wx&amp;spsts=1718384902775&amp;spstoken=kwUhCAI71WD1HK7pC6Ubrpb17sN4HrgsARl2QPTvuOAearFlxPLBtWOTVsdhnmZ%2F</url>\n\t\t<lowurl />\n\t\t<forwardflag>0</forwardflag>\n\t\t<dataurl />\n\t\t<lowdataurl />\n\t\t<contentattr>0</contentattr>\n\t\t<streamvideo>\n\t\t\t<streamvideourl />\n\t\t\t<streamvideototaltime>0</streamvideototaltime>\n\t\t\t<streamvideotitle />\n\t\t\t<streamvideowording />\n\t\t\t<streamvideoweburl />\n\t\t\t<streamvideothumburl />\n\t\t\t<streamvideoaduxinfo />\n\t\t\t<streamvideopublishid />\n\t\t</streamvideo>\n\t\t<canvasPageItem>\n\t\t\t<canvasPageXml><![CDATA[]]></canvasPageXml>\n\t\t</canvasPageItem>\n\t\t<appattach>\n\t\t\t<attachid />\n\t\t\t<cdnthumburl>3057020100044b3049020100020461cefcb302032f7b170204b61daa240204666c7911042437656537666230642d616665392d343061652d393763332d3365626131363062353238650204051408030201000405004c511f00</cdnthumburl>\n\t\t\t<cdnthumbmd5>550d10800132fdeca696d197c504da78</cdnthumbmd5>\n\t\t\t<cdnthumblength>18747</cdnthumblength>\n\t\t\t<cdnthumbheight>1920</cdnthumbheight>\n\t\t\t<cdnthumbwidth>1080</cdnthumbwidth>\n\t\t\t<cdnthumbaeskey>0cab6c4517eddf67596efbc88f5f42f6</cdnthumbaeskey>\n\t\t\t<aeskey>0cab6c4517eddf67596efbc88f5f42f6</aeskey>\n\t\t\t<encryver>1</encryver>\n\t\t\t<fileext />\n\t\t\t<islargefilemsg>0</islargefilemsg>\n\t\t</appattach>\n\t\t<extinfo />\n\t\t<androidsource>2</androidsource>\n\t\t<thumburl />\n\t\t<mediatagname />\n\t\t<messageaction><![CDATA[]]></messageaction>\n\t\t<messageext><![CDATA[]]></messageext>\n\t\t<emoticongift>\n\t\t\t<packageflag>0</packageflag>\n\t\t\t<packageid />\n\t\t</emoticongift>\n\t\t<emoticonshared>\n\t\t\t<packageflag>0</packageflag>\n\t\t\t<packageid />\n\t\t</emoticonshared>\n\t\t<designershared>\n\t\t\t<designeruin>0</designeruin>\n\t\t\t<designername>null</designername>\n\t\t\t<designerrediretcturl><![CDATA[null]]></designerrediretcturl>\n\t\t</designershared>\n\t\t<emotionpageshared>\n\t\t\t<tid>0</tid>\n\t\t\t<title>null</title>\n\t\t\t<desc>null</desc>\n\t\t\t<iconUrl><![CDATA[null]]></iconUrl>\n\t\t\t<secondUrl>null</secondUrl>\n\t\t\t<pageType>0</pageType>\n\t\t\t<setKey>null</setKey>\n\t\t</emotionpageshared>\n\t\t<webviewshared>\n\t\t\t<shareUrlOriginal />\n\t\t\t<shareUrlOpen />\n\t\t\t<jsAppId />\n\t\t\t<publisherId />\n\t\t\t<publisherReqId />\n\t\t</webviewshared>\n\t\t<template_id />\n\t\t<md5>550d10800132fdeca696d197c504da78</md5>\n\t\t<websearch>\n\t\t\t<rec_category>0</rec_category>\n\t\t\t<channelId>0</channelId>\n\t\t</websearch>\n\t\t<weappinfo>\n\t\t\t<username />\n\t\t\t<appid />\n\t\t\t<appservicetype>0</appservicetype>\n\t\t\t<secflagforsinglepagemode>0</secflagforsinglepagemode>\n\t\t\t<videopageinfo>\n\t\t\t\t<thumbwidth>1080</thumbwidth>\n\t\t\t\t<thumbheight>1920</thumbheight>\n\t\t\t\t<fromopensdk>0</fromopensdk>\n\t\t\t</videopageinfo>\n\t\t</weappinfo>\n\t\t<statextstr>GhQKEnd4N2JlM2MxYmI0NmM2OGM2Mw==</statextstr>\n\t\t<musicShareItem>\n\t\t\t<musicDuration>0</musicDuration>\n\t\t</musicShareItem>\n\t\t<finderLiveProductShare>\n\t\t\t<finderLiveID><![CDATA[]]></finderLiveID>\n\t\t\t<finderUsername><![CDATA[]]></finderUsername>\n\t\t\t<finderObjectID><![CDATA[]]></finderObjectID>\n\t\t\t<finderNonceID><![CDATA[]]></finderNonceID>\n\t\t\t<liveStatus><![CDATA[]]></liveStatus>\n\t\t\t<appId><![CDATA[]]></appId>\n\t\t\t<pagePath><![CDATA[]]></pagePath>\n\t\t\t<productId><![CDATA[]]></productId>\n\t\t\t<coverUrl><![CDATA[]]></coverUrl>\n\t\t\t<productTitle><![CDATA[]]></productTitle>\n\t\t\t<marketPrice><![CDATA[0]]></marketPrice>\n\t\t\t<sellingPrice><![CDATA[0]]></sellingPrice>\n\t\t\t<platformHeadImg><![CDATA[]]></platformHeadImg>\n\t\t\t<platformName><![CDATA[]]></platformName>\n\t\t\t<shopWindowId><![CDATA[]]></shopWindowId>\n\t\t\t<flashSalePrice><![CDATA[0]]></flashSalePrice>\n\t\t\t<flashSaleEndTime><![CDATA[0]]></flashSaleEndTime>\n\t\t\t<ecSource><![CDATA[]]></ecSource>\n\t\t\t<sellingPriceWording><![CDATA[]]></sellingPriceWording>\n\t\t\t<platformIconURL><![CDATA[]]></platformIconURL>\n\t\t\t<firstProductTagURL><![CDATA[]]></firstProductTagURL>\n\t\t\t<firstProductTagAspectRatioString><![CDATA[0.0]]></firstProductTagAspectRatioString>\n\t\t\t<secondProductTagURL><![CDATA[]]></secondProductTagURL>\n\t\t\t<secondProductTagAspectRatioString><![CDATA[0.0]]></secondProductTagAspectRatioString>\n\t\t\t<firstGuaranteeWording><![CDATA[]]></firstGuaranteeWording>\n\t\t\t<secondGuaranteeWording><![CDATA[]]></secondGuaranteeWording>\n\t\t\t<thirdGuaranteeWording><![CDATA[]]></thirdGuaranteeWording>\n\t\t\t<isPriceBeginShow>false</isPriceBeginShow>\n\t\t\t<lastGMsgID><![CDATA[]]></lastGMsgID>\n\t\t\t<promoterKey><![CDATA[]]></promoterKey>\n\t\t\t<discountWording><![CDATA[]]></discountWording>\n\t\t\t<priceSuffixDescription><![CDATA[]]></priceSuffixDescription>\n\t\t\t<showBoxItemStringList />\n\t\t</finderLiveProductShare>\n\t\t<finderOrder>\n\t\t\t<appID><![CDATA[]]></appID>\n\t\t\t<orderID><![CDATA[]]></orderID>\n\t\t\t<path><![CDATA[]]></path>\n\t\t\t<priceWording><![CDATA[]]></priceWording>\n\t\t\t<stateWording><![CDATA[]]></stateWording>\n\t\t\t<productImageURL><![CDATA[]]></productImageURL>\n\t\t\t<products><![CDATA[]]></products>\n\t\t\t<productsCount><![CDATA[0]]></productsCount>\n\t\t</finderOrder>\n\t\t<finderShopWindowShare>\n\t\t\t<finderUsername><![CDATA[]]></finderUsername>\n\t\t\t<avatar><![CDATA[]]></avatar>\n\t\t\t<nickname><![CDATA[]]></nickname>\n\t\t\t<commodityInStockCount><![CDATA[]]></commodityInStockCount>\n\t\t\t<appId><![CDATA[]]></appId>\n\t\t\t<path><![CDATA[]]></path>\n\t\t\t<appUsername><![CDATA[]]></appUsername>\n\t\t\t<query><![CDATA[]]></query>\n\t\t\t<liteAppId><![CDATA[]]></liteAppId>\n\t\t\t<liteAppPath><![CDATA[]]></liteAppPath>\n\t\t\t<liteAppQuery><![CDATA[]]></liteAppQuery>\n\t\t\t<platformTagURL><![CDATA[]]></platformTagURL>\n\t\t\t<saleWording><![CDATA[]]></saleWording>\n\t\t\t<lastGMsgID><![CDATA[]]></lastGMsgID>\n\t\t\t<profileTypeWording><![CDATA[]]></profileTypeWording>\n\t\t\t<reputationInfo>\n\t\t\t\t<hasReputationInfo>0</hasReputationInfo>\n\t\t\t\t<reputationScore>0</reputationScore>\n\t\t\t\t<reputationWording />\n\t\t\t\t<reputationTextColor />\n\t\t\t\t<reputationLevelWording />\n\t\t\t\t<reputationBackgroundColor />\n\t\t\t</reputationInfo>\n\t\t\t<productImageURLList />\n\t\t</finderShopWindowShare>\n\t\t<findernamecard>\n\t\t\t<username />\n\t\t\t<avatar><![CDATA[]]></avatar>\n\t\t\t<nickname />\n\t\t\t<auth_job />\n\t\t\t<auth_icon>0</auth_icon>\n\t\t\t<auth_icon_url />\n\t\t\t<ecSource><![CDATA[]]></ecSource>\n\t\t\t<lastGMsgID><![CDATA[]]></lastGMsgID>\n\t\t</findernamecard>\n\t\t<finderGuarantee>\n\t\t\t<scene><![CDATA[0]]></scene>\n\t\t</finderGuarantee>\n\t\t<directshare>0</directshare>\n\t\t<gamecenter>\n\t\t\t<namecard>\n\t\t\t\t<iconUrl />\n\t\t\t\t<name />\n\t\t\t\t<desc />\n\t\t\t\t<tail />\n\t\t\t\t<jumpUrl />\n\t\t\t</namecard>\n\t\t</gamecenter>\n\t\t<patMsg>\n\t\t\t<chatUser />\n\t\t\t<records>\n\t\t\t\t<recordNum>0</recordNum>\n\t\t\t</records>\n\t\t</patMsg>\n\t\t<secretmsg>\n\t\t\t<issecretmsg>0</issecretmsg>\n\t\t</secretmsg>\n\t\t<referfromscene>0</referfromscene>\n\t\t<gameshare>\n\t\t\t<liteappext>\n\t\t\t\t<liteappbizdata />\n\t\t\t\t<liteapppriority>0</liteapppriority>\n\t\t\t</liteappext>\n\t\t\t<gameshareid />\n\t\t\t<sharedata />\n\t\t\t<isvideo>0</isvideo>\n\t\t\t<duration>-1</duration>\n\t\t\t<isexposed>0</isexposed>\n\t\t\t<readtext />\n\t\t</gameshare>\n\t\t<mpsharetrace>\n\t\t\t<hasfinderelement>0</hasfinderelement>\n\t\t\t<lastgmsgid />\n\t\t</mpsharetrace>\n\t\t<wxgamecard>\n\t\t\t<framesetname />\n\t\t\t<mbcarddata />\n\t\t\t<minpkgversion />\n\t\t\t<mbcardheight>0</mbcardheight>\n\t\t\t<isoldversion>0</isoldversion>\n\t\t</wxgamecard>\n\t</appmsg>\n\t<fromusername>wxid_gqhxp9ipfxv222</fromusername>\n\t<scene>0</scene>\n\t<appinfo>\n\t\t<version>73</version>\n\t\t<appname>网易新闻</appname>\n\t</appinfo>\n\t<commenturl></commenturl>\n</msg>",
    '''
    message2='''
    &amp;#91;&amp;#91;分享&amp;#93;这腿白么，要是能摸摸就好了&amp;#93;请使用最新版本手机QQ查看[CQ:json,data={&quot;app&quot;:&quot;com.tencent.structmsg&quot;&amp;#44;&quot;desc&quot;:&quot;新闻&quot;&amp;#44;&quot;bizsrc&quot;:&quot;&quot;&amp;#44;&quot;view&quot;:&quot;news&quot;&amp;#44;&quot;ver&quot;:&quot;0.0.0.1&quot;&amp;#44;&quot;prompt&quot;:&quot;&amp;#91;分享&amp;#93;这腿白么，要是能摸摸就好了&quot;&amp;#44;&quot;meta&quot;:{&quot;news&quot;:{&quot;action&quot;:&quot;&quot;&amp;#44;&quot;android_pkg_name&quot;:&quot;&quot;&amp;#44;&quot;app_type&quot;:1&amp;#44;&quot;appid&quot;:100346651&amp;#44;&quot;ctime&quot;:1686236218&amp;#44;&quot;desc&quot;:&quot;&quot;&amp;#44;&quot;jumpUrl&quot;:&quot;https:\/\/c.m.163.com\/news\/sv\/VY5NI8DHP.html?spss=newsapp&amp;amp;spsnuid=yxEDNniygRH%2BLOTZ9DRcI1b6LleXCC%2BCkap%2FSMUSf1E%3D&amp;amp;spsdevid=CQk0MTIxYWVmYWNhZTBiZmQ3CU44SzVUMTcxMjYwMjkzNjk%253D&amp;amp;spsvid=&amp;amp;spsshare=qq&amp;amp;spsts=1686236215127&amp;amp;spstoken=NyzOMLIHXCnpVATAg4sXlhoKHibx7iHxcgwSF1IcBPm%2F8syrkw5te1NHpbH8CvJ5&quot;&amp;#44;&quot;preview&quot;:&quot;https:\/\/pic.ugcimg.cn\/7d4872b59b2f18e662d611d439ed58e7\/jpg1&quot;&amp;#44;&quot;source_icon&quot;:&quot;http:\/\/p.qpic.cn\/qqconnect_app_logo\/YCOL3hU8ffVhXSIfd1ibFM5IWItywjblfGhCojgCzH8I\/0&quot;&amp;#44;&quot;source_url&quot;:&quot;&quot;&amp;#44;&quot;tag&quot;:&quot;网易新闻&quot;&amp;#44;&quot;title&quot;:&quot;这腿白么，要是能摸摸就好了&quot;&amp;#44;&quot;uin&quot;:21202893}}&amp;#44;&quot;config&quot;:{&quot;ctime&quot;:1686236218&amp;#44;&quot;forward&quot;:true&amp;#44;&quot;token&quot;:&quot;c932a3be410db33337035a30f642e2ea&quot;&amp;#44;&quot;type&quot;:&quot;normal&quot;}}]
    '''
    title='徐志胜何广智cp感爆棚，一句“我身边一定得是你”，李诞：在一起'
    pattern = r'[~`!@#$%^&*()_“”：\-+=|\\{\}\[\]:;\"\'<>,.?/·！￥…（）—【】、？《》，。]+'
    title = re.sub(pattern, '_', title)
    print(title)


    videourl=parse_videourl_qq(message1)
    videurl=parse_videourl(message1)
    ret_json=downloadneteasy(videurl)
    title=ret_json['data']['title']
    title = re.sub(pattern, '_', title)
    mp4_url=ret_json['data']['mp4_url']
    m3u8_url =ret_json['data']['m3u8_url']
    topicImg=ret_json['data']['topicImg']
    vid=ret_json['data']['vid']
    print(title)
    print(mp4_url)
    print(m3u8_url)
    print(topicImg)

    C = SaveVideo()
    #C.getLesson()
    #url='http://flv0.bn.netease.com/df2634e8adc26a43b9ef42b7372e222eaff55bce3036d8fd5926bc255d953e76627d3134fd28f8937f989c4dc8410ca20b2b37a9feb71d4003273b5c4a8dbb9f839f1339d6aaeff3c60178c71f7d4bf1d08a4202af4742b029077cf458c74304298e556d122ad8baeee6daeb3007279521c0287401d5bce2.mp4'


    C.downloadVideo(mp4_url,file_name=title)

    #downloadneteasy()
