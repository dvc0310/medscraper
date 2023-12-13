import scrapy
import json
from drug_scraper.items import SideItem  # Ensure this path is correct

class SideeffectspiderSpider(scrapy.Spider):
    name = "SideEffectSpider"
    allowed_domains = ["rxlist.com"]

    def __init__(self, *args, **kwargs):
        super(SideeffectspiderSpider, self).__init__(*args, **kwargs)
        with open('sidelinks.json', 'r') as json_file:
            self.drugs_data = json.load(json_file)

    def start_requests(self):
        for drug in self.drugs_data:
            link = drug.get('link')
            generic_name = drug.get('generic_name')  # Assuming 'generic_name' is the key in your drugs_data
            if link:
                # Pass the generic_name in the meta
                yield scrapy.Request(link, callback=self.parse_side_effects, meta={'generic_name': generic_name})
        

    def parse_side_effects(self, response):
        # Find all p tags that contain 'side effects' in the text
        p_selectors = response.xpath("//p[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'side effect')]")

        for p in p_selectors:
            # Get the following ul that is before the next div or h3
            ul = p.xpath('following-sibling::ul[not(following-sibling::div | following-sibling::h3)][1]')

            # Check that we have found a <ul>
            if ul:
                # Extract all <li> texts within the <ul>
                list_items = ul.xpath('.//li/text()').getall()
                side_effects = [text.strip() for text in list_items if text.strip()]  # Filter out empty strings

                item = SideItem()
                item["generic_name"] = response.meta.get('generic_name', 'Unknown')  # Default to 'Unknown' if not found
                item["side_effect"] = side_effects
                
                yield item