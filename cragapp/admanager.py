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
        if   args.action == "renew"  : callback = self.renew
        elif args.action == "delete" : callback = self.delete
        elif args.action == "repost" : callback = self.repost
        elif args.action == "add"    : callback = self.add
        else: raise Exception("incorrect action option. must be renew|delete|repost|add")
        
        return scrapy.FormRequest.from_response(
            response,
            formdata={
                'step':"confirmation",
                'rt':"L",
                'rp':"/login/home",
                'p':"0",
                'inputEmailHandle': self.user.username,
                'inputPassword': self.user.password},
            callback=callback)


    def delete(self, response):
        delete_form = filter(lambda x: self.ad.idcrag in x ,
                             response.xpath("//form[./input[@value='delete']]").extract())[0]
        #first CL magic. in urls like https://post.craigslist.org/manage/5163849759/kytja
        #kytja - row code. on even ad action (delete,renew,repost) this code the same.
        self.row_code    = delete_form.split(self.ad.idcrag+'/')[1].split('"')[0]
        
        
        return scrapy.Request(
            url='https://post.craigslist.org/manage/'
            +self.ad.idcrag+'/'+self.row_code+'?action=delete&go=delete',
            method='GET',
            callback=self.delete1)

    def delete1(self, response):
        #second CL magic. every action contains crypt sequence. need to push this
        #sequence to server in form data.

        self.crypt = response.\
                     xpath("//form[./input[@name='crypt']]/input[@name='crypt']/@value").\
                     extract()[0]
        

        return scrapy.FormRequest.from_response(
            response=response,
            url='https://post.craigslist.org/manage/'
            + self.ad.idcrag + '/' + self.row_code,
            formdata ={
                "action":"delete",
                "crypt":self.crypt,
                "go":"delete"},
            method='POST',
            callback=self.finalize)

    def repost(self, response):
        with open("logs/repost_step_1.html", 'w') as f:
            f.write(response.body)
            f.flush()

        repost_form = filter(lambda x: self.ad.idcrag in x ,
                             response.xpath("//form[./input[@value='repost']]").extract())[0]
        
        self.row_code    = repost_form.split(self.ad.idcrag+'/')[1].split('"')[0]
        
            
        return scrapy.Request(
            url='https://post.craigslist.org/manage/'
            +self.ad.idcrag+'/'+self.row_code+'?action=repost&go=repost',
            method='GET',
            callback=self.repost1)

    def repost1(self, response):
        with open("logs/repost_step_2.html", 'w') as f:
            f.write(response.body)
            f.flush()
        self.crypt = response.\
                xpath("//form[./input[@name='cryptedStepCheck']]/input[@name='cryptedStepCheck']/@value").extract()[0]
        
        '''return scrapy.FormRequest.from_response(
            response=response,
            url='https://post.craigslist.org/manage/'
            + self.ad.idcrag + '/' + self.row_code,
            formdata ={
                "action":"delete",
                "crypt":self.crypt,
                "go":"delete"},
            method='POST',
            callback=self.finalize)'''


    
    def renew(self, response):
        print response.body
    

    def add(self, response):
        pass
    
    #testing function which should output in file final response
    def finalize(self,response):
        with open("finalize.html", 'w') as f:
            f.write(response.body)
            f.flush()

    
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(CraigSpider)
process.start()
