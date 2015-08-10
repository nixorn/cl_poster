import scrapy
import operator
from scrapy.crawler import CrawlerProcess
from models import Ad, Image
from database import db_session


class CraigSpider(scrapy.Spider):
    name = "craiglist"
    allowed_domains = ['craigslist.org']
    download_delay = 2
    
    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)

        ids = kwargs['ad_ids'][:]
        self.start_urls = ["http://" + kwargs['area']
                           + '.craiglist.org/'
                           + kwargs['category']
                           + '/' + ad_id + '.html' for ad_id in ids]
    
    def parse(self, response):
        description = response.css('#postingbody').extract()
        description = [item+'\n' for item in description]
        description = reduce(operator.concat, description[1:], description[0])
        

        print response.css('.postingtitletext').extract()[0],\
            response.url.split('/')[2].split('.')[0],\
            response.css('#postingbody').extract(),\
            description

         
    def parseImage(self, response):
        pass

    
#process = CrawlerProcess({
#    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
#})



