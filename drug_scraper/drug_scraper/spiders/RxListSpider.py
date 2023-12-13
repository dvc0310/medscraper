import scrapy
from fuzzywuzzy import fuzz
import json
from drug_scraper.items import DrugItem  # Ensure this path is correct

class RxListSpider(scrapy.Spider):
    name = 'rxlist_spider'
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    start_urls = ["https://www.rxlist.com/script/main/alphaidx.asp?p={}_rx-mcon".format(letter) for letter in alphabet]

    # Initialize once and reuse
    def __init__(self, *args, **kwargs):
        super(RxListSpider, self).__init__(*args, **kwargs)
        with open('./notebooks/jsons/generic_drug_features.json', 'r') as json_file:
            self.drugs_data = json.load(json_file)
            
    def parse(self, response):
        for li in response.xpath('//ul/li'):
            link = li.xpath('.//a[contains(@href, "generic-drug.htm")]')
            if link:
                drug_name = link.xpath('text()').get()
                drug_link = response.urljoin(link.xpath('@href').get())

                for name in self.drugs_data.keys():
                    if self.is_close_match(self.normalize_name(drug_name), self.normalize_name(name)):
                        item = DrugItem()
                        item['drug_name'] = name
                        item['link'] = drug_link
                        yield item

    def normalize_name(self, name):
        return name.lower().replace(' ', '-').replace('_', '-').replace('/', '-')

    def is_close_match(self, name1, name2, threshold=90):
        return fuzz.partial_ratio(name1, name2) > threshold
