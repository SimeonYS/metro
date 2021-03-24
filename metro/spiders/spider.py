import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import MetroItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class MetroSpider(scrapy.Spider):
	name = 'metro'
	start_urls = ['https://www.firstmetro.com/press-releases']

	def parse(self, response):
		post_links = response.xpath('//td[@class="list-title"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@title="Next"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):
		date = response.xpath('//time/text()').get().strip()
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//span[@itemprop="articleBody"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=MetroItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
