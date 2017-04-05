# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DouyuItem(scrapy.Item):
	# define the fields for your item here like:
	#room_name    anchor_city    nickname  image_url image_path  linkmd5id  update
	data = scrapy.Field()
	image_url = scrapy.Field()
	image_path= scrapy.Field()
	pass
