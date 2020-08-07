import json
import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

URLS_TEPI = [
    'https://sajiansedap.grid.id/goreng',
    'https://sajiansedap.grid.id/tumis',
    'https://sajiansedap.grid.id/panggang',
    'https://sajiansedap.grid.id/rebus',
    'https://sajiansedap.grid.id/kukus',
]

URLS_DALAM = [] # a dictionary with nama_resep dan link_resep

END_RESULTS = []

class ResepSpider(scrapy.Spider):
    name = 'resepspider'
    
    def start_requests(self):
        for url in URLS_TEPI:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        list_resep = []
        for resep in response.css('.main__content--title'):
            nama = resep.css('::text').get()
            link = resep.attrib['href']
            URLS_DALAM.append({
                'nama_resep': nama,
                'link_resep': link
            })
        
class DetailResepSpider(scrapy.Spider):
    name = 'detailresepspider'
    
    def start_requests(self):
        for url in URLS_DALAM:
            yield scrapy.Request(url=url['link_resep'], callback=self.parse)


    def parse(self, response):
        nama = response.css('.read__title>h1::text').get()
        for resep in response.css('.read>div>p'):
            p = resep.css('::text').getall()
            if 'Bahan:' in p:
                # print(nama)
                # print(p)
                END_RESULTS.append({
                    'nama': nama,
                    'bahan': p
                })

configure_logging()
runner = CrawlerRunner()

@defer.inlineCallbacks
def crawl():
    yield runner.crawl(ResepSpider)
    yield runner.crawl(DetailResepSpider)
    reactor.stop()

crawl()
reactor.run()

print(f'resep didapat: {len(END_RESULTS)}')

with open('resep.txt', 'w') as outfile:
    json.dump(END_RESULTS, outfile)