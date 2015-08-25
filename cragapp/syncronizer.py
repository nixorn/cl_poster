#in fact it is scrapy spider + minimal running logic.
import scrapy
import operator
import argparse
import logging
from scrapy.crawler import CrawlerProcess
from models import Ad, Image, User, VPS, Category, Area
from database import db_session

logging.basicConfig(filename='cragloop.log',level=logging.ERROR)

parser = argparse.ArgumentParser(description='Crawl from craiglist ad and store it into database.')
subparsers = parser.add_subparsers(help='Scrap all user ads or concret ad?')

userscrap_parser = subparsers.add_parser('userscrap', help='Scrap all user ads')
userscrap_parser.add_argument('--idusers',
                    help='User to grab data from')

adscrap_parser = subparsers.add_parser('adscrap', help='Scrap concret ad')
adscrap_parser.add_argument('--idads',
                    help='internal ad id to sync for CL')

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


#proxy setup
if 'idads' in dir(args):
    ad = Ad.query.filter(Ad.idads == args.idads).first()
    user = User.query.filter(User.idusers == ad.idusers).first()
    vps = VPS.query.filter(VPS.idvpss == user.idvpss).first()
    
    
elif 'idusers' in dir(args):
    user = User.query.filter(User.idusers == args.idusers).first()
    vps = VPS.query.filter(VPS.idvpss == user.idvpss).first()

else:
    logging.error("Can't work with proxy!")
    raise Exception("No proxy setted up!")

proxy = 'https://' + ':'.join([str(vps.ip), str(vps.port)])
    




class Synchronizer(scrapy.Spider):
    name = "synchronizer"
    allowed_domains = ['craigslist.org']
    start_urls = ['https://accounts.craigslist.org/login']
    download_delay = 2

    
    def parse(self, response):
        
        if 'idads' in dir(args):
            ad = Ad.query.filter(Ad.idads == args.idads).first()

            category = Category.query.\
                       filter(Category.idcategory == ad.idcategory)\
                           .first()
            area = Area.query.filter(Area.idarea == ad.idarea).first()
            url = "http://"+area.urlname\
                  + '.craigslist.org/'\
                  + category.clcode + '/'\
                  + ad.idcrag + '.html'
            return scrapy.Request(url,
                                  meta={'idads':ad.idads, 'proxy':proxy},
                                  callback=self.parse_ad)
        
        elif 'idusers' in dir(args):
            self.user = User.query.filter(User.idusers == args.idusers).first()
            return scrapy.FormRequest.from_response (
                response,
                formdata={
                    'step':"confirmation",
                    'rt':"L",
                    'rp':"/login/home",
                    'p':"0",
                    'inputEmailHandle': self.user.username,
                    'inputPassword': self.user.password},
                meta={'idads':ad.idads, 'proxy':proxy},
                callback=self.parse_home)


    def parse_home(self, response):
        debug_html_content(response,"parse_home",1)
        sel = scrapy.Selector(text=response.body, type='html')
        for row in sel.xpath('//tr')[2:]: # crrop table head
            status = row.xpath('./td[contains(@class,"status")]/small/text()')\
                        .extract_first()
            allowed_categories = [cat.fullname for cat in Category.query.all()]

            rawcatname = row.xpath('./td[contains(@class,"areacat")]/text()')\
                            .extract()
            
            cat_name = filter(lambda x: x.strip()!='', rawcatname)[0].strip()

            if cat_name in allowed_categories:
                #+ default None action
                allowed_actions = row.xpath('./td[contains(@class,"buttons")]'+
                                            '/form/input[@class="managebtn"]'+
                                            '/@value').extract() + ["None"]
                url = row.xpath('./td[contains(@class,"title")]/a/@href')\
                         .extract_first()
                idcrag = row.xpath('./td[contains(@class,"postingID")]/text()')\
                            .extract_first().strip()
                title = row.xpath('./td[contains(@class,"title")]/text()')\
                           .extract_first().strip()
                area_code = row.xpath('./td[contains(@class,"areacat")]/b/text()')\
                               .extract_first().strip()
                area = Area.query.filter(Area.clcode == area_code).first()

                category = Category.query.filter(Category.fullname == cat_name)\
                                         .first()
                ad = Ad.query.filter(Ad.idcrag == idcrag).first()

                if not ad:
                    ad = Ad(
                        idcrag = idcrag,
                        description='',
                        title=title,
                        posting_time='',
                        scheduled_action="",
                        repost_timeout="",
                        prev_action   ="",
                        prev_act_time ="",
                        prev_act_stat ="",
                        status=status,
                        idusers=self.user.idusers,
                        idcategory=category.idcategory,
                        idarea=area.idarea,
                        replymail='',
                        allowed_actions = ','.join(allowed_actions),
                        contact_phone='',
                        contact_name='',
                        postal='',
                        specific_location='',
                        haslicense='',
                        license_info='')
                    db_session.add(ad)
                    try:
                        db_session.commit()
                    except:
                        db_session.rollback()
                        raise Exception("DB commit is not OK")
                    
                elif ad:
                    ad.status = status
                    ad.allowed_actions = ','.join(allowed_actions)
                    db_session.add(ad)
                    try:
                        db_session.commit()
                    except Exception as e:
                        db_session.rollback()
                        raise Exception("DB commit is not OK\n"+e.message)
                    
                if url:
                    print "RUNNING OUT AD", ad.idads
                    yield scrapy.Request(
                        url=url,
                        meta={'idads':ad.idads, 'proxy':proxy},
                        callback=self.parse_ad)


    def parse_ad(self, response):
        debug_html_content(response,"parse_ad",1)
        print "COMMING AD", response.meta['idads']

        ad = Ad.query.filter(Ad.idads == response.meta['idads']).first()
        description = response.xpath(".//*[@id='postingbody']/text()").extract()
        description = [item+'\n' for item in description]
        if description:
            description = reduce(operator.concat, description[1:], description[0])

        area_urlname       = response.url.split('/')[2].split('.')[0]

        area = Area.query.filter(Area.urlname == area_urlname).first()
        if area: ad.idarea = area.idarea
        if description:
            ad.description = description
            ad.title       = response\
              .xpath('//span[@class="postingtitletext"]/text()')\
              .extract_first().strip()

        db_session.add(ad)
        try:
            db_session.commit()
        except:
            db_session.rollback()
            raise Exception("DB commit is not OK")

        img_urls = response.xpath('//*[@href]')\
            .re('http://images.craigslist.org/'\
                +'[0-9a-zA-Z_]+[0-9]{2,3}x[0-9]{2,3}'\
                +'.(jpg|png|gif|jpeg)')\
            
            + response.xpath('//*[@src]')
                .re('http://images.craigslist.org/'\
                    +'[0-9a-zA-Z_]+[0-9]{2,3}x[0-9]{2,3}'\
                    '.(jpg|png|gif|jpeg)') 
        
        img_urls = list(set(img_urls))
        
        for pic_url in img_urls:
            yield scrapy.Request(pic_url,
                meta={'idads':ad.idads, 'proxy':proxy},
                callback=self.parseImage)

    def parseImage(self, response):

        idads = response.meta['idads']

        craglink = response.url
        img      = Image.query.filter(Image.craglink == craglink).first()
        if img:
            db_session.delete(img)
            db_session.commit()
        
        extension = craglink.split('.')[-1]
        filename  = craglink.split('/')[-1]
        
        if extension == "jpg": mime = "image/jpeg"
        else:                  mime = "image/" + extension

        image = response.body

        img = Image(extension  = extension,
                    mime       = mime,          
                    filename   = filename,      
                    craglink   = craglink,        
                    idads      = idads,         
                    image      = image)
                            

        db_session.add(img)
        try:
            db_session.commit()
        except:
            db_session.rollback()
            raise Exception("DB commit is not OK")

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(Synchronizer)
process.start()
