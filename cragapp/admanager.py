import scrapy
import itertools
import operator
import argparse
import time
import random
import requests
import logging
from scrapy.crawler import CrawlerProcess
from models import Ad, User, VPS, Area, Image, Category
from database import db_session

logging.basicConfig(filename='logs/admanager.log',level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Crawl from craiglist ad and store it into database.')
parser.add_argument('--idads',
                    help='id from internal database')

parser.add_argument('--action',
                    help='renew|delete|repost|add|undelete|edit|confirm|None')

parser.add_argument('--confirm_link',
                    help='Link for mail confirmation. Optional argument,'+\
                    'needed for confirmation only.')

parser.add_argument('--username',
                    help='user for login. needed if operation is confirm')

args = parser.parse_args()

#output grabed html page to see what happens
def debug_html_content(response,action_name,step_num):
    with open("logs/"+str(action_name)+"_step_"+str(step_num)+".html", 'w') as f:
            f.write("REQUEST\n")
            f.write("\nURL: "+str(response.request.url)+'\n')
            f.write("\nHEADERS:\n")
            for header in response.request.headers.items():
                f.write(str(header)+'\n')
            f.write("\nCOOKIES: "+str(response.request.cookies)+'\n')
            f.write('\nBODY:\n')
            f.write(str(response.request.body)+'\n')
            try:
                f.write("\nFORM_DATA: "+str(response.request.formdata)+'\n')
            except: pass
            f.write("\n###########################################\n")
            f.write("\n\n\nRESPONSE\n")
            f.write("\nHEADERS:\n")
            for header in response.headers.items():
                f.write(str(header)+'\n')
            f.write('\nBODY:\n')
            f.write(response.body)
            f.write("\n###########################################\n")
            f.flush()


class AdManager(scrapy.Spider):
    name = "admanager"
    allowed_domains = ['craigslist.org']
    download_delay = 2
    start_urls = ['https://accounts.craigslist.org/login']
    handle_httpstatus_list = [404]
    custom_settings = {'USER_AGENT':"Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0",}

    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)
        
        if args.idads:
            self.ad   = Ad.query.filter(Ad.idads == args.idads).first()
            self.user = User.query.filter(User.idusers == self.ad.idusers).first()
            vps  = VPS.query.filter(VPS.idvpss == self.user.idvpss).first()
            self.proxy = 'https://' + ':'.join([str(vps.ip), str(vps.port)])
            self.area = Area.query.filter(Area.idarea == self.ad.idarea).first()
            self.category = Category.query.\
                filter(Category.idcategory == self.ad.idcategory).first()

        elif args.username:
            self.user = User.query.filter(User.username == args.username).first()

    def parse(self, response):
        if   args.action == "renew"    : callback = self.renew1
        elif args.action == "delete"   : callback = self.delete1
        elif args.action == "repost"   : callback = self.repost1
        elif args.action == "undelete" : callback = self.undelete1
        elif args.action == "add"      : callback = self.add_go
        elif args.action == "edit"     : callback = self.edit1
        elif args.action == "confirm"  : callback = self.confirm1
        elif args.action == "None"     : callback = self.none
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
            dont_filter=True,
            callback=self.finalize)

    def repost1(self, response):
        if self.ad.status == "Not posted":
            raise Exception("Looks ad dont posted."+
                            " Try to sync and reschedule action ")
        if not ad.idcrag:
            raise Exception("Ad have no CL id. It is not OK.")
        
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
                'browserinfo':"%7B%0A%09%22plugins%22%3A%20%22Plugin%200%3A%20Shockwave%20Flash%3B%20Shockwave%20Flash%2011.2%20r202%3B%20libflashplayer.so%3B%20%28Shockwave%20Flash%3B%20application/x-shockwave-flash%3B%20swf%29%20%28FutureSplash%20Player%3B%20application/futuresplash%3B%20spl%29.%20%22%2C%0A%09%22timezone%22%3A%20-180%2C%0A%09%22video%22%3A%20%221366x768x24%22%2C%0A%09%22supercookies%22%3A%20%22DOM%20localStorage%3A%20Yes%2C%20DOM%20sessionStorage%3A%20Yes%2C%20IE%20userData%3A%20No%22%0A%7D",
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
            dont_filter=True,
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
            dont_filter=True,
            callback=self.finalize)

    def add_go(self, response):#go button
        debug_html_content(response,"add_go",1)

        return scrapy.FormRequest.from_response(
            response=response,
            url="https://accounts.craigslist.org/login/pstrdr",
            formdata ={"areaabb":self.area.clcode},
            method='POST',
            headers={"Host":"accounts.craigslist.org",
                     'Referer':'https://accounts.craigslist.org/login/home',
                     'Connection':'keep-alive'},
            callback=self.add_serv)

    def add_serv(self, response):# select services offer
        debug_html_content(response,"add_serv",2)

        cryptedStepCheck = response.\
            xpath("//form[./input[@name='cryptedStepCheck']]/input[@name='cryptedStepCheck']/@value").extract()[0]

        return scrapy.FormRequest.from_response(
            response=response,
            url=response.request.url.split("?s=")[0],
            formdata = {"id":"so",
                        "cryptedStepCheck":cryptedStepCheck},
            method='POST',
            callback=self.add_sks,
            headers={"Host":"post.craigslist.org",
                     'Connection':'keep-alive'},

            dont_filter=True)

    def add_sks(self, response):#select which servise you want to offers. skilled trade for example
        debug_html_content(response,"add_sks",3)

        cryptedStepCheck = response.\
            xpath("//form[./input[@name='cryptedStepCheck']]"+\
                  "/input[@name='cryptedStepCheck']/@value").extract()[0]

        url = response.xpath("//form[./input[@name='cryptedStepCheck']]"+\
                             "/@action").extract()[0]
        return scrapy.FormRequest.from_response(
            response=response,
            url=response.request.url.split("?s=")[0],

            formdata = {"id":str(self.category.numcode),
                        "cryptedStepCheck":cryptedStepCheck},
            headers={"Host":"post.craigslist.org",
                     'Connection':'keep-alive'},
            method='POST',
            dont_filter=True,
            #callback=self.add_body)
            callback=self.add_location)

    #location. long island needed?
    # if "choose the location that fits best" in 
    def add_location(self,response):
        debug_html_content(response, "add_location", 4)
        if "choose the location that fits best" in response.body:
            long_i_code = response\
                .xpath("//label[text()='long island']/input/@value")\
                .extract_first()
        
            cryptedStepCheck = response.\
                xpath("//form[./input[@name='cryptedStepCheck']]"+\
                "/input[@name='cryptedStepCheck']/@value").extract()[0]
        
            return scrapy.FormRequest.from_response(
                response=response,
                url=response.request.url,
                formdata = {"n":long_i_code,
                    "cryptedStepCheck":cryptedStepCheck},
                method='POST',
                headers={"Host":"post.craigslist.org",
                         'Connection':'keep-alive'},
                dont_filter=True,
                callback=self.add_body)
        #if response not contain location info
        #just skip this step and send body
        else: return self.add_body(response)
    
    def add_body(self, response): #title body etc
        debug_html_content(response,"add_body",5)

        #body will add 2 minutes
        time.sleep(30)
        cryptedStepCheck = \
            response.xpath("//form[./input[@name='cryptedStepCheck']]"+\
                "/input[@name='cryptedStepCheck']/@value").extract()[0]

        url = response.\
              xpath("//form[./input[@name='cryptedStepCheck']]/@action")\
              .extract()[0]


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
                'wantamap':"on",#
                'xstreet0':"",
                'xstreet1':"",
                'city':"",
                'region':"",
                'postal':self.ad.postal,,
                'go':"Continue",
                'cryptedStepCheck':cryptedStepCheck},
            method='POST',
            headers={"Host":"post.craigslist.org",
                     'Connection':'keep-alive'},

            dont_filter=True,
            callback=self.add_images)




    def add_images(self, response):#images
        debug_html_content(response,"add_images",5)

        images = Image.query.filter(Image.idads == self.ad.idads).all()

        #need to send with request. in headers and somewhere in body

        cryptedStepCheck = \
            response.xpath("//form[./input[@name='cryptedStepCheck']]/input[@name='cryptedStepCheck']/@value").extract()[0]
        resp = None
        for image in images:
            boundary = "----moxieboundary" + time.time().__str__().replace('.','') + \
                       random.choice(range(10)).__str__()
            url = response.request.url.split("?s=")[0],

            files = [("name", image.filename),
                     ("cryptedStepCheck", cryptedStepCheck),
                     ("ajax", '1'),
                     ("a", "add"),
                     (image.filename, image.image)]

            oldheaders = response.request.headers
            cookie =  response.request.headers['Cookie']
            headers = {'Host':"post.craigslist.org",
                       'User-Agent':oldheaders['User-Agent'],
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                       'Accept-Language':"en-US,en;q=0.5",
                       'Accept-Encoding': 'gzip,deflate',
                       'Referer': oldheaders['Referer'].replace('s=edit', 's=editimage'),
                       'Cookie': oldheaders['Cookie'],
                       'Connection':"keep-alive",
                       'Pragma':"no-cache",
                       'Cache-Control':"no-cache"}

            url = url[0] # WTF? Why string becomes (string,)
            req = requests.Request('POST',url,files=files,headers=headers)
            prepared = req.prepare()
            prepared.body = prepared.body.replace('; filename="name"','')
            prepared.body = prepared.body.replace('; filename="ajax"','')
            prepared.body = prepared.body.replace('; filename="cryptedStepCheck"','')
            prepared.body = prepared.body.replace('; filename="a"','')
            current_boundary = prepared.headers["Content-Type"].split('boundary=')[1]
            prepared.headers["Content-Type"] = prepared.headers["Content-Type"].replace(current_boundary, boundary)
            prepared.body = prepared.body.replace(current_boundary, boundary)
            print image.filename + image.mime

            #it refuses replase with str. Thats why str->bytearray->do replace->str
            prepared.body = bytearray(prepared.body)
            prepared.body = prepared.body.replace(
                bytearray('name="'+image.filename+'"; filename="'+image.filename+'"', 'ascii'),
                bytearray('name="file"; filename="'+image.filename+'"\nContent-Type: '+image.mime, 'ascii'))#
            prepared.body = str(prepared.body)
            prepared.headers["Content-Length"] = len(prepared.body).__str__()

            '''print '{}\n{}\n{}\n\n{}'.format(
                '-----------START-----------',
                prepared.method + ' ' + prepared.url,
                '\n'.join('{}: {}'.format(k, v)
                          for k, v in prepared.headers.items()),
                "image"
                #prepared.body,
            )'''

            s = requests.Session()
            resp = s.send(prepared)

            image.craglink = resp.json()['added']['URL']

            db_session.add(image)
            try:
                db_session.commit()
            except:
                db_session.rollback()
                raise Exception("DB commit is not OK")

        return scrapy.FormRequest.from_response(
            response=response,
            url = response.request.url.split("?s=")[0],
            formdata = {
                'cryptedStepCheck':cryptedStepCheck,
                'a':'fin',
                'go':'Done with Images'},
            method='POST',
            dont_filter=True,
            callback=self.add_publish)

    def add_publish(self, response):#publish
        debug_html_content(response,"add_publish",6)
        cryptedStepCheck = \
            response.xpath("//form[./input[@name='cryptedStepCheck']]"+\
                "/input[@name='cryptedStepCheck']/@value").extract()[0]
        return scrapy.FormRequest.from_response(
            response=response,
            url = response.request.url.split("?s=")[0],
            formdata = {
                'cryptedStepCheck':cryptedStepCheck,
                'continue':"y",
                'go':"Continue"},
            method='POST',
            headers={"Host":"post.craigslist.org",
                     'Connection':'keep-alive'},
            dont_filter=True,
            callback=self.add_get_id)

    def add_get_id(self,response):#get idcrag
        debug_html_content(response,"add_get_id",7)
        idcrag = response\
                 .xpath('//a[@target="_blank"]/@href')\
                 .extract_first().split('/')[-1].split('.')[0]
        self.ad.idgrag = idcrag
        db_session.add(self.ad)
        try:
            db_session.commit()
        except:
            db_session.rollback()
            raise Exception("DB commit is not OK")

    def undelete1(self, response):
        debug_html_content(response,"undelete",1)
        undelete_form = filter(lambda x: self.ad.idcrag in x,
            response.xpath("//form[./input[@value='undelete']]").extract())[0]
        
        self.crypt = response.\
            xpath("//form[./input[@name='crypt']]/input[@name='crypt']/@value").\
            extract()[0]
        
        self.row_code = undelete_form.split(self.ad.idcrag+'/')[1].split('"')[0]

        return scrapy.FormRequest.from_response(
            response=response,
            url='https://post.craigslist.org/manage/'+
            self.ad.idcrag+'/'+self.row_code,
            formdata ={
                "action":"undelete",
                "crypt":self.crypt,
                "go":"undelete"},
            method='POST',
            callback=self.finalize)
        
    def renew1(self, response):
        debug_html_content(response,"renew",1)
        renew_form = filter(lambda x: self.ad.idcrag in x,
                            response.xpath("//form[./input[@value='renew']]")\
                            .extract())[0]

        #split renew_form for "<>", get entry of tag wich contains "crypt"
        #and split for " "
        atrs = filter(lambda x: "crypt" in x,
                       renew_form.split("><"))[0].split(" ")

        #get value from "value" attr
        self.crypt = filter(lambda x: "value" in x, atrs)[0].split('"')[1]

        
        self.row_code = renew_form.split(self.ad.idcrag+'/')[1].split('"')[0]

        return scrapy.FormRequest.from_response(
            response=response,
            url='https://post.craigslist.org/manage/'+
            self.ad.idcrag+'/'+self.row_code,
            formdata ={
                "action":"renew",
                "crypt":self.crypt,
                "go":"renew"},
            method='POST',
            callback=self.finalize)
        
    def confirm1(self, response):#go into confirmation
        debug_html_content(response,"confirm",1)
        url = args.confirm_link
        return scrapy.Request(url=url
            ,method='GET'
            ,callback=self.confirm2)
    
    def confirm2(self, response):#accept terms if need
        debug_html_content(response,"confirm",2)
        if "Terms of Use" in response.body:
            cryptedStepCheck = \
                response.xpath("//form[./input[@name='cryptedStepCheck']]"+\
                "/input[@name='cryptedStepCheck']/@value").extract_first()

            confirm_link = response.xpath("//form/@action").extract_first()
            return scrapy.FormRequest.from_response(
                response=response,
                url=confirm_link,
                formdata ={
                    "cryptedStepCheck":cryptedStepCheck,
                    "continue":"y"})
        #nothing to confirm
        else: return None
        

        
    def edit1(self, response): #not implemented
        debug_html_content(response,"edit",1)

    #testing function which should output in file final response
    def finalize(self,response):
        debug_html_content(response,"finalize",1)

    def none(self, response):#dummy
        pass


    
process = CrawlerProcess({
    "USER-AGENT":"Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0",
})

process.crawl(AdManager)
process.start()
