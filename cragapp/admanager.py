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

#output grabed html page to see what happens
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
            

class CraigSpider(scrapy.Spider):
    name = "craiglist"
    allowed_domains = ['craigslist.org']
    download_delay = 2
    start_urls = ['https://accounts.craigslist.org/login']
    handle_httpstatus_list = [404]
    
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
        elif args.action == "delete" : callback = self.delete1
        elif args.action == "repost" : callback = self.repost1
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


    def delete1(self, response):
        debug_html_content(response,"delete",1)
        delete_form = filter(lambda x: self.ad.idcrag in x ,
                             response.xpath("//form[./input[@value='delete']]").extract())[0]
        #first CL magic. in urls like https://post.craigslist.org/manage/5163849759/kytja
        #kytja - row code. on even ad action (delete,renew,repost) this code the same.
        self.row_code    = delete_form.split(self.ad.idcrag+'/')[1].split('"')[0]
        
        
        return scrapy.Request(
            url='https://post.craigslist.org/manage/'
            +self.ad.idcrag+'/'+self.row_code+'?action=delete&go=delete',
            method='GET',
            callback=self.delete2)

    def delete2(self, response):
        debug_html_content(response,"delete",2)
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

    def repost1(self, response):
        debug_html_content(response,"repost",1)
    
        repost_form = filter(lambda x: self.ad.idcrag in x ,
                             response.xpath("//form[./input[@value='repost']]").extract())[0]
        
        self.row_code    = repost_form.split(self.ad.idcrag+'/')[1].split('"')[0]
        
            
        return scrapy.Request(
            url='https://post.craigslist.org/manage/'
            +self.ad.idcrag+'/'+self.row_code+'?action=repost&go=repost',
            method='GET',
            callback=self.repost2)

    def repost2(self, response):
        debug_html_content(response,"repost",2)

        repost_url = response.xpath("//form[@id='postingForm']/@action").extract()[0]
        cryptedStepCheck = response.\
                                xpath("//form[./input[@name='cryptedStepCheck']]/input[@name='cryptedStepCheck']/@value").extract()[0]

        categoryid = response.xpath("//select[@name='CategoryID']/option[@selected]/@value").extract()[0]

        
        req = scrapy.FormRequest.from_response(
            response=response,
            url=response.request.url,
            formdata ={
                'id2':"1348x860X1348x370X1366x768",
                #id2 =  $(document).width() + "x" 
                #+ $(document).height() + "X" 
                #+ $(window).width() + "x" 
                #+ $(window).height() + "X" 
                #+ screen.width + "x" 
                #+ screen.height
                'browserinfo':"%7B%0A%09%22plugins%22%3A%20%22Plugin%200%3A%20Shockwave%20Flash%3B%20Shockwave%20Flash%2011.2%20r202%3B%20libflashplayer.so%3B%20%28Shockwave%20Flash%3B%20application/x-shockwave-flash%3B%20swf%29%20%28FutureSplash%20Player%3B%20application/futuresplash%3B%20spl%29.%20%22%2C%0A%09%22timezone%22%3A%20-180%2C%0A%09%22video%22%3A%20%221366x768x24%22%2C%0A%09%22supercookies%22%3A%20%22DOM%20localStorage%3A%20Yes%2C%20DOM%20sessionStorage%3A%20Yes%2C%20IE%20userData%3A%20No%22%0A%7D",
                #browserinfo = escape(JSON.stringify(fetch_client_info(), null, ""))
                'FromEMail':self.user.username,
                'Privacy':"C",
                'contact_phone':self.ad.contact_phone,
                'contact_name':self.ad.contact_name,
                'CategoryID':categoryid,
                'PostingTitle': self.ad.title,
                'GeographicArea':self.ad.specific_location,
                'postal': self.ad.postal,
                'PostingBody':self.ad.description,
                'go':"Continue",
                'cryptedStepCheck':cryptedStepCheck},
            method='POST',
            callback=self.repost3)
    
        return req

    
    def repost3(self, response):
        debug_html_content(response,"repost",3)
        cryptedStepCheck = response.\
                                xpath("//form[./input[@name='cryptedStepCheck']]/input[@name='cryptedStepCheck']/@value").extract()[0]
        return scrapy.FormRequest.from_response(
            response=response,
            url=response.request.url,
            formdata ={
                'cryptedStepCheck':cryptedStepCheck,
                'continue':"y",
                'go':"Continue"},
            method='POST',
            callback=self.finalize)

    
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
    "USER-AGENT":"Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0"
})

process.crawl(CraigSpider)
process.start()
