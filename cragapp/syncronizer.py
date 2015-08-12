#in fact it is scrapy spider + minimal running logic.
import scrapy
import operator
import argparse
from scrapy.crawler import CrawlerProcess
from models import Ad, Image
from database import db_session


parser = argparse.ArgumentParser(description='Crawl from craiglist ad and store it into database.')
parser.add_argument('--idads', nargs=1,
                    help='id from internal database')


args = parser.parse_args()




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
        
        self.ad = Ad.query.filter(Ad.idads == args.idads).first()

        
        self.start_urls = ['http://' + str(self.ad.area) + '.craigslist.org/'
                           + str(self.ad.category) + '/' + str(self.ad.idcrag) + '.html',]
        

        
    
    def parse(self, response):

        description = response.xpath(".//*[@id='postingbody']/text()").extract()
        description = [item+'\n' for item in description]
        description = reduce(operator.concat, description[1:], description[0])
        
        self.ad.title       = response.xpath(".//*[@class='postingtitletext']/text()").extract()[0]
        self.ad.area        = response.url.split('/')[2].split('.')[0]
        self.ad.description = description
        self.ad.status      = response.xpath(".//*[@id='pagecontainer']/section/section[2]/div[2]/p[2]/text()").extract()
        db_session.add(self.ad)
        db_session.commit()

        for pic_url in response.xpath(".//*[@id='thumbs']/a/@href").extract():
            yield scrapy.Request(pic_url, callback=self.parseImage)
            
         
    def parseImage(self, response):

        img = Image(extension=response.url.split('.')[-1],
                    craglink=response.url,
                    idads=self.ad.idads,         
                    image=response.body)         
        db_session.add(img)
        db_session.commit()







        

    
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(CraigSpider)
process.start()
