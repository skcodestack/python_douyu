# -*- coding: utf-8 -*-
import scrapy

'''添加内容'''
from douyu.items import DouyuItem
import json

class DouyuSpiderSpider(scrapy.Spider):
	name = "douyuSpider"
	allowed_domains = ["douyucdn.cn"]
	start_urls = ['http://douyucdn.cn/']
	'''添加内容'''
	offset = 0
	start_urls = (
		'http://capi.douyucdn.cn/api/v1/getVerticalRoom?limit=20&offset='+str(offset),
	)


	def parse(self, response):
		# print response 
		'''添加内容'''
		data=json.loads(response.body)['data']
		if not data:
			return

		for it in data:
			item = DouyuItem()
			item['image_url']=it['vertical_src']
			item['image_path']=' '
			item['data']=it
			# print it['vertical_src']
			yield item

		self.offset+=20
		yield scrapy.Request('http://capi.douyucdn.cn/api/v1/getVerticalRoom?limit=20&offset=%s'%str(self.offset),callback=self.parse)
