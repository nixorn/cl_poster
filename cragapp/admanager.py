import scrapy
import operator
import argparse
from scrapy.crawler import CrawlerProcess
from models import Ad, User, VPS
from database import db_session


parser = argparse.ArgumentParser(description='Crawl from craiglist ad and store it into database.')
parser.add_argument('--idads', 
                    help='id from internal database')

parser.add_argument('--action',
                    help='renew|delete|repost|add')

args = parser.parse_args()




class CraigSpider(scrapy.Spider):
    name = "craiglist"
    allowed_domains = ['craigslist.org']
    download_delay = 2
    start_urls = ['https://accounts.craigslist.org/login']
    
    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)
        
        self.ad   = Ad.query.filter(Ad.idads == args.idads).first()
        self.user = User.query.filter(User.idusers == self.ad.idusers).first()
        self.vps  = VPS.query.filter(VPS.idvpss == self.user.idvpss).first()
        


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
            callback=self.after_login)
        

    def after_login(self, response):
        print args.action
        if   args.action == "renew"  : self.renew(response)
        elif args.action == "delete" : self.delete(response)
        elif args.action == "repost" : self.repost(response)
        elif args.action == "add"    : self.add(response)
        else: raise Exception("incorrect option")

    def renew(self, response):
        print response.body

    def delete(self, response):
        pass

    def repost(self, response):
        pass

    def add(self, response):
        pass

        

    
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(CraigSpider)
process.start()
