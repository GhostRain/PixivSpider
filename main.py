# -*- coding:utf-8 -*-
import urllib
import urllib2
import cookielib
import requests
import time
import os
import sys
import random
import win32api
import log
from bs4 import BeautifulSoup
from ip_request import requestPool
from dbHelper import dbHelper

class PixivSpider:
	def __init__(self):
		self.se = requests.session()
		#主站首页
		self.main_url = 'https://www.pixiv.net/'
		#收藏夹
		self.bookmarkUrl = 'https://www.pixiv.net/bookmark.php'
		#登录请求url
		self.loginUrl = 'https://accounts.pixiv.net/api/login?lang=zh'
		#浏览器参数
		user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'
		#登录页面地址，拿去post_key用
		self.referer_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
		#收藏推荐页
		self.bookmark_addUrl = 'https://www.pixiv.net/bookmark_add.php?id='
		#伪造头部
		self.headers = {'User-Agent' : user_agent,
			'Referer' : 'https://accounts.pixiv.net/login',
			'Connection':'keep-alive',
			'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
			'Accept-Encoding':'gzip, deflate',
			'Accept-Language':'zh-CN,zh;q=0.8'}
		#从登录页面拿取post_key
		post_key_html = self.se.get(self.referer_url, headers=self.headers).text
		post_key_soup = BeautifulSoup(post_key_html, 'lxml')
		post_key = post_key_soup.find('input')['value']
		log.out("post_key="+post_key)
		
		self.postdata = urllib.urlencode({'pixiv_id' : '634784732@qq.com',
			'password' : 'cs741111',
			'post_key' : post_key,
			'return_to' : 'https://www.pixiv.net/'
			})
		
		self.timeout = 3
		self.download_path = 'download'
		self.imgIDList = ['62578571']

	def login(self):
		log.out('正在登录...')
		#登录
		self.response = self.se.post(self.loginUrl, data=self.postdata, headers=self.headers)
		log.out('登录成功')
		#log.out('Cookie:', self.se.cookies)

	#下载收藏资源
	def download_bookmark(self):
		#2页收藏
		for page_num in range(1, 3):
			self.bookmarkUrl = self.bookmarkUrl + '?rest=show&p=' + str(page_num)
			self.response = self.get_html(self.bookmarkUrl)
			self.get_img(self.response.text)
			time.sleep(2)
		self.download_bookmarkadd()

	def download_bookmarkadd(self):
		if len(self.imgIDList) <= 0:
			return
		imgID = random.choice(self.imgIDList)
		self.imgIDList.remove(imgID)
		addUrl = self.bookmark_addUrl+imgID
		self.response = self.get_html(addUrl)
		self.get_img(self.response.text)
		time.sleep(2)
		self.download_bookmarkadd()

	def get_img(self, html):
		li_soup = BeautifulSoup(html, 'lxml')
		li_list = li_soup.find_all('li', attrs={'class', 'image-item'})
		for li in li_list:
			href = li.find('a')['href']
			jump_to_url = self.main_url + href
			log.out('jump_to_url...'+jump_to_url)
			jump_to_html = self.get_html(jump_to_url).text

			time.sleep(1)
			img_soup = BeautifulSoup(jump_to_html, 'lxml')
			img_info = img_soup.find('div', attrs={'class', 'works_display'}).find('div', attrs={'class', '_layout-thumbnail ui-modal-trigger'})
			if img_info is None:
				continue
			#log.out(img_info)
			self.download_img(img_info, jump_to_url)

	def download_img(self, img_info, href):
		title = img_info.find('img')['alt']
		src = img_info.find('img')['src']
		file_name = src.split('/')[-1]
		file_name = file_name.split('_')[0]
		src_headers = self.headers
		src_headers['Referer'] = href
		log.out(src)
		try:
			html = requests.get(src, headers=src_headers)
			img = html.content
		except:
			log.out('获取该图片失败:'+src)
			return False
		if os.path.exists(os.path.join(file_name+'.jpg')):
			log.out('跳过重复图片')
		else:
			log.out('正在保存...'+file_name)
			f = open(file_name+'.jpg', 'ab')
			f.write(img)
			#存到当前已抓取ID列表
			self.imgIDList.append(file_name)
			#写入数据库
			#if not dbHelper.check_image_exist():
			#	dbHelper.insert_img(int(file_name),'aaaa','fff',1234)

	#获取对应url里的html文本
	def get_html(self, url, proxy=None, num_retries = 6):
		if proxy == None:
			try:
				return self.se.get(url, headers=self.headers, timeout=self.timeout)
			except:
				if num_retries > 0:
					log.out('打开网页出错，5秒后重试...')
					time.sleep(5)
					return self.get_html(url,num_retries = num_retries - 1)
				else:
					log.out('开始使用代理...')
					ip = requestPool.get_randomIP()
					now_proxy = {'http': ip}
					return self.get_html(url, proxy=now_proxy, timeout=self.timeout)
		else:
			try:
				return self.se.get(url, headers=self.headers, proxies=proxy, timeout=self.timeout)
			except:
				if num_retries > 0:
					log.out('5秒后更换代理重试...')
					time.sleep(5)
					ip = requestPool.get_randomIP()
					log.out('当前代理ip：'+ip)
					now_proxy = {'http': ip}
					return self.get_html(url, proxy=now_proxy, timeout=self.timeout, num_retries = num_retries - 1)
				else:
					log.out('代理也拯救不了...')
					log.out('10秒后取消代理重新连接...')
					return self.get_html(url)
		

	#初始化存储路径,按照日期
	def mkdir(self):
		log.out('初始化存储路径...')
		nowDataStr = time.strftime("%Y-%m-%d", time.localtime())
		#self.work_path = nowDataStr.strip()
		self.work_path = self.download_path
		is_exist = os.path.exists(os.path.join(self.work_path))
		if not is_exist:
			os.makedirs(os.path.join(self.work_path))
			os.chdir(os.path.join(self.work_path))
			return True
		else:
			os.chdir(os.path.join(self.work_path))
			return False

	def closeHandler(self):
		os.chdir(sys.path[0])
		f = open('cache.dat', 'wb')
		f.write(','.join(map(str,self.imgIDList)))
		f.close()

	def link_start(self):
		self.mkdir()
		self.login()
		#self.download_bookmarkadd()
		self.download_bookmark()

pSpider = PixivSpider()
pSpider.link_start()

#关闭窗口回调
def on_close(sig):
	pSpider.closeHandler()

win32api.SetConsoleCtrlHandler(on_close, True)