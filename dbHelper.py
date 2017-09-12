#!/usr/bin/python
# -*- coding: UTF-8 -*-

import MySQLdb
import log
import sys

class DbHelper():
	def __init__(self):
		self.insertImgSQL = "INSERT INTO `pixiv`.`imageinfo` (`id`, `path`, `author`, `authorid`) VALUES ('%s','%s','%s','%s')"
		log.out('连接数据库...')
		self.db = MySQLdb.connect("localhost","root","1234","pixiv",3308)
		self.cur = self.db.cursor(cursorclass=MySQLdb.cursors.DictCursor)

	#检测图片是否已经存在
	def check_image_exist(self,imageid):
		result = self.cur.execute("SELECT id FROM imageinfo where id = '%s';" % (imageid))
		if result == 0:
			return False
		else:
			return True
	
	#写入一条数据
	def insert_img(self,imageid,path,author,authorid,taglist):
		self.cur.execute(self.insertImgSQL,(imageid,path,author,authorid))
		self.db.commit()
		for tag in taglist:
			isexist = check_tag_exist(tag)
			if isexist == 0:
				self.insert_tag(tag)


	#获取tag对应id，0为不存在
	def check_tag_exist(self,tag):
		result = self.cur.execute("SELECT tagid FROM taginfo where des = '%s';" % (tag))
		if result == 0:
			return 0
		else:
			info = self.cur.fetchone()
			return info['tagid']

	#写入新的tag
	def insert_tag(self,tag):
		self.cur.execute("INSERT INTO `pixiv`.`taginfo` (`des`) VALUES ('%s');" % (tag))
		self.db.commit()

	#查询tag关联是否存在
	def check_linktag_exist(self,imageid,tag):
		result = self.cur.execute("SELECT imageid,tag FROM linktag where imageid = '%s' and tag = '%s';" % (imageid,tag))
		if result == 0:
			return False
		else:
			return True

	#写入tag关联表
	def insert_taglink(self,imageid,tag):
		if not self.check_linktag_exist(imageid,tag):
			self.cur.execute("INSERT INTO `pixiv`.`linktag` (`imageid`,`tag`) VALUES ('%s','%s');" % (imageid,tag))
			self.db.commit()
		

dbHelper = DbHelper()
#dbHelper.insert_img(1,'aaaa','fff',1234)
#print(dbHelper.check_image_exist(1))
# dbHelper.insert_tag('fff')
# print(dbHelper.check_tag_exist('fff'))
# dbHelper.insert_taglink(11,'asd')