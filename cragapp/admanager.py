import scrapy
import operator
import argparse
import time
import requests
from scrapy.crawler import CrawlerProcess
from models import Ad, User, VPS, Area, Image, Category
from database import db_session


parser = argparse.ArgumentParser(description='Crawl from craiglist ad and store it into database.')
parser.add_argument('--idads', 
                    help='id from internal database')

parser.add_argument('--action',
                    help='renew|delete|repost|add|undelete')

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
        self.area = Area.query.filter(Area.idarea == self.ad.idarea).first()
        self.category = Category.query.filter(Category.idcategory == self.ad.idcategory).first()


    def parse(self, response):
        if   args.action == "renew"    : callback = self.renew1
        elif args.action == "delete"   : callback = self.delete1
        elif args.action == "repost"   : callback = self.repost1
        elif args.action == "undelete" : callback = self.undelete1
        elif args.action == "add"      : callback = self.add1
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
        
        return scrapy.FormRequest.from_response(
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

    def add1(self, response):#go button
        debug_html_content(response,"add",1)

        return scrapy.FormRequest.from_response(
            response=response,
            url="https://accounts.craigslist.org/login/pstrdr",
            formdata ={"areaabb":self.area.clcode},
            method='POST',
            callback=self.add2,
            dont_filter=True)

    def add2(self, response):# select services offer
        debug_html_content(response,"add",2)

        
        cryptedStepCheck = response.\
            xpath("//form[./input[@name='cryptedStepCheck']]/input[@name='cryptedStepCheck']/@value").extract()[0]

        return scrapy.FormRequest.from_response(
            response=response,
            url=response.request.url.split("?s=")[0],
            formdata = {"id":"so", 
                        "cryptedStepCheck":cryptedStepCheck},
            method='POST',
            callback=self.add3,
            dont_filter=True)

    def add3(self, response):#select which servise you want to offers. skilled trade for example
        debug_html_content(response,"add",3)


        cryptedStepCheck = response.\
            xpath("//form[./input[@name='cryptedStepCheck']]/input[@name='cryptedStepCheck']/@value").extract()[0]

        url = response.xpath("//form[./input[@name='cryptedStepCheck']]/@action").extract()[0]
        return scrapy.FormRequest.from_response(
            response=response,
            url=response.request.url.split("?s=")[0],

            formdata = {"id":str(self.category.numcode),
                        "cryptedStepCheck":cryptedStepCheck},
            method='POST',
            callback=self.add4)
    
    def add4(self, response): #title body etc
        debug_html_content(response,"add",4)

        cryptedStepCheck = \
            response.xpath("//form[./input[@name='cryptedStepCheck']]/input[@name='cryptedStepCheck']/@value").extract()[0]

        url = response.xpath("//form[./input[@name='cryptedStepCheck']]/@action").extract()[0]

        
        return scrapy.FormRequest.from_response(
            response=response,
            url = response.request.url.split("?s=")[0],
            formdata ={
                'id2':"1348x860X1348x370X1366x768",
                'browserinfo':"%7B%0A%09%22plugins%22%3A%20%22Plugin%200%3A%20Shockwave%20Flash%3B%20Shockwave%20Flash%2011.2%20r202%3B%20libflashplayer.so%3B%20%28Shockwave%20Flash%3B%20application/x-shockwave-flash%3B%20swf%29%20%28FutureSplash%20Player%3B%20application/futuresplash%3B%20spl%29.%20%22%2C%0A%09%22timezone%22%3A%20-180%2C%0A%09%22video%22%3A%20%221366x768x24%22%2C%0A%09%22supercookies%22%3A%20%22DOM%20localStorage%3A%20Yes%2C%20DOM%20sessionStorage%3A%20Yes%2C%20IE%20userData%3A%20No%22%0A%7D",
                'FromEMail':self.user.username,
                'Privacy':"C",
                'contact_phone':self.ad.contact_phone,
                'contact_name':self.ad.contact_name,
                'PostingTitle': self.ad.title,
                'GeographicArea':self.ad.specific_location,
                'postal': self.ad.postal,
                'PostingBody':self.ad.description,
                'has_license':str(self.ad.haslicense),#1 if has
                'license_info':self.ad.license_info,
                'go':"Continue",
                'cryptedStepCheck':cryptedStepCheck},
            method='POST',
            callback=self.add5)
    
    def add5(self, response):#images
        debug_html_content(response,"add",5)

        images = Image.query.filter(Image.idads == self.ad.idads).all()

        #need to send with request. in headers and somewhere in body
        boundary = "----moxieboundary" + time.time().__str__().replace('.','')
        cryptedStepCheck = \
            response.xpath("//form[./input[@name='cryptedStepCheck']]/input[@name='cryptedStepCheck']/@value").extract()[0]
        hidden_name = response.xpath("//input[@type='hidden' and @value='fin']/@name").extract()[0]
        for image in images:
            url=response.request.url.split("?s=")[0],
            #url = '/'.join(url[0].split('/')[0:-1])
            headers = {"Content-Type":"multipart/form-data; boundary="+boundary},
            
            '''body = bytearray(boundary + '\n'
                             + 'Content-Disposition: form-data; name="name"'+'\n\n'
                             + image.filename + '\n'
                             + boundary + '\n'
                             + 'Content-Disposition: form-data; name="cryptedStepCheck"' + '\n\n'
                             + cryptedStepCheck + '\n'
                             + boundary + '\n'
                             + 'Content-Disposition: form-data; name="ajax"'+'\n\n'+'1'
                             + boundary + '\n'
                             + 'Content-Disposition: form-data; name="'+'"'+hidden_name+'"' + '\n\n'
                             + 'add' +'\n'
                             + boundary + '\n'
                             + 'Content-Disposition: form-data; name="file"; filename="'+image.filename+'"' + '\n'
                             + 'Content-Type: '+ image.mime + '\n\n', 'ascii')+ image.image + b'\n' +  bytearray(boundary + '\n', 'ascii')'''

            files = [("name", image.filename),
                     ("cryptedStepCheck", cryptedStepCheck),
                     ("ajax", '1'),
                     ("a", "add"),
                     (image.filename, image.image)]



            cookie =  response.request.headers['Cookie']


            url = url[0] # WTF? Why string becomes (string,)
            req = requests.Request('POST',url,files=files,headers={'Cookie':cookie, })
            prepared = req.prepare()
            print '{}\n{}\n{}\n\n{}'.format(
                        '-----------START-----------',
                        prepared.method + ' ' + prepared.url,
                        '\n'.join('{}: {}'.format(k, v) for k, v in prepared.headers.items()),
                        prepared.body,
                    )
            #resp = requests.post(url,files=files,headers={'Cookie':cookie, })
            #print resp.text
            #print resp.request.url




        
    def add6(self, response):#publish
        debug_html_content(response,"add",6)

        
    def renew1(self, response):
        print response.body

    def undelete1(self, response):
        print response.body
    

    
    #testing function which should output in file final response
    def finalize(self,response):
        with open("finalize.html", 'w') as f:
            f.write(response.body)
            f.flush()

    
process = CrawlerProcess({
    "USER-AGENT":"Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0",
    "DUPEFILTER_DEBUG": True
})


process.crawl(CraigSpider)
process.start()
