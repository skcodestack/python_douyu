# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import json
import codecs
import scrapy
from scrapy  import log
from hashlib import md5
import MySQLdb
from twisted.enterprise import adbapi
import datetime
import MySQLdb
import MySQLdb.cursors
import logging 

logger=logging.getLogger("shikai")
class MySQLStorePipeline(object):
	def __init__(self,dbpool):
		self.dbpool = dbpool

	@classmethod
	def from_settings(cls, settings):
		dbargs = dict(
			host=settings['MYSQL_HOST'],
			db=settings['MYSQL_DBNAME'],
			user=settings['MYSQL_USER'],
			passwd=settings['MYSQL_PASSWD'],
			charset='utf8',
			cursorclass = MySQLdb.cursors.DictCursor,
			use_unicode= True,
		)
		dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
		return cls(dbpool)
	#pipeline默认调用
	def process_item(self, item, spider):
		logger.info("===>process_item")
		d = self.dbpool.runInteraction(self._do_upinsert, item, spider)
		d.addErrback(self._handle_error, item, spider)
		# d.addBoth(lambda _: item)
		return d
	#将每行更新或写入数据库中
	def _do_upinsert(self, conn, item, spider):
		linkmd5id = self._get_linkmd5id(item)
		logger.info("===>_do_upinsert"+linkmd5id+";;;;;;")
		print "=====>"+linkmd5id
		# now = datetime.utcnow().replace(microsecond=0).isoformat(' ')
		now = datetime.datetime.now()
		conn.execute("""
		select 1 from douyumminfo where linkmd5id = %s
		""", (linkmd5id, ))
		ret = conn.fetchone()
		#room_name    anchor_city    nickname  image_url 
		# image_path  linkmd5id  update
		if ret:
			logger.info("===>_do_upinsert1111111111111111111111")
			conn.execute("""
			update douyumminfo set room_name = %s,anchor_city = %s,nickname = %s, image_url = %s, image_path = %s, updated = %s where linkmd5id = %s
			""", (item['data']['room_name'],item['data']['anchor_city'],item['data']['nickname'], item['image_url'], item['image_path'], now, linkmd5id))
		#print """
		#    update cnblogsinfo set title = %s, description = %s, link = %s, listUrl = %s, updated = %s where linkmd5id = %s
		#""", (item['title'], item['desc'], item['link'], item['listUrl'], now, linkmd5id)
		else:
			logger.info("===>_do_upinsert22222222222222222")
			conn.execute("""
			insert into douyumminfo(linkmd5id, room_name,anchor_city, nickname, image_url, image_path, updated) 
			values(%s, %s, %s, %s, %s, %s, %s)
			""", (linkmd5id, item['data']['room_name'],item['data']['anchor_city'], item['data']['nickname'], item['image_url'], item['image_path'], now))


	#print """
	#    insert into cnblogsinfo(linkmd5id, title, description, link, listUrl, updated)
	#    values(%s, %s, %s, %s, %s, %s)
	#""", (linkmd5id, item['title'], item['desc'], item['link'], item['listUrl'], now)
	#获取url的md5编码
	def _get_linkmd5id(self, item):
		#url进行md5处理，为避免重复采集设计
		return md5(item['image_url']).hexdigest()
	#异常处理
	def _handle_error(self, failue, item, spider):
		# log.error_message=''
		log.err(failue)




class ImagesPipeline(ImagesPipeline):
	"""
		docstring for ImagesPipeline
		download  image
	"""
	def get_media_requests(self, item, info):
		image_url = item['image_url']
		yield scrapy.Request(image_url)

	def item_completed(self, results, item, info):
		image_paths = [x['path'] for ok, x in results if ok]
		if not image_paths:
			raise DropItem("Item contains no images")
		item['image_path'] = image_paths[0]
		return item
		
class JsonWriterPipeline(object):
	'''
		save  info  to json
	'''
	def __init__(self):
		self.file = codecs.open('items.json', 'w', encoding='utf-8')

	def process_item(self, item, spider):
		line = json.dumps(dict(item), ensure_ascii=False) + "\n"
		self.file.write(line)
		return item

	def spider_closed(self, spider):
		self.file.close()
