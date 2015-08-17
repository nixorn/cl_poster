#in fact it is scrapy spider + minimal running logic.
import scrapy
import operator
import argparse
from scrapy.crawler import CrawlerProcess
from models import Ad, Image, User, VPS
from database import db_session


parser = argparse.ArgumentParser(description='Crawl from craiglist ad and store it into database.')
parser.add_argument('--idusers', 
                    help='User to grab data from')


args = parser.parse_args()


def debug_html_content(response,action_name,step_num):
    with open("logs/"+str(action_name)+"_step_"+str(step_num)+".html", 'w') as f:
            f.write("REQUEST\n")
            f.write(str(response.request.url)+'\n')
            f.write(str(response.request.headers)+'\n')
            f.write(str(response.request.cookies)+'\n')
            f.write(str(response.request.body)+'\n')
            f.write("\nRESPONSE\n")
            f.write(str(response.headers)+'\n')
            f.write(response.body)
            f.flush()




class Synchronizer(scrapy.Spider):
    name = "synchronizer"
    allowed_domains = ['craigslist.org']
    start_urls = ['https://accounts.craigslist.org/login']
    download_delay = 2
    
    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)
        self.user = User.query.filter(User.idusers == args.idusers).first()
        
        
    
    def parse(self, response):
        
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'step':"confirmation",
                'rt':"L",
                'rp':"/login/home",
                'p':"0",
                'inputEmailHandle': self.user.username,
                'inputPassword': self.user.password},
            callback=self.parse_home)

    
    def parse_home(self, response):
        debug_html_content(response,"parse_home",1)
        rows = response.xpath('//tr')
        for row in rows:
            status = row.xpath('/td[@class="status Z"]/small/text()').extract_first()
            allowed_actions = row.xpath('/td[@class="buttons Z"]'+
                                        '/form/input[@class="managebtn"]'+
                                        '/@value').extract()
            url = row.xpath('/td[@class="title Z"]/a/@href').extract_first()
            idcrag = row.xpath('/td[@class="postingID Z"]/text()').extract_first().strip()
            print status, allowed_actions, url, idcrag
    
    def parse_ad(self, response):

        description = response.xpath(".//*[@id='postingbody']/text()").extract()
        description = [item+'\n' for item in description]
        description = reduce(operator.concat, description[1:], description[0])
        
        self.ad.title       = response.xpath(".//*[@class='postingtitletext']/text()").extract()[0]
        self.ad.area        = response.url.split('/')[2].split('.')[0]
        self.ad.description = description
        self.ad.status      = response.xpath('.//*[@id="pagecontainer"]'+
                                             '/section/section[2]/div[2]/p[2]/text()').extract()
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

process.crawl(Synchronizer)
process.start()
