import scrapy
import json
import scrapy
from drug_scraper.items import InteractionItem
import os
class InteractionSpiderSpider(scrapy.Spider):
    name = "interaction_spider"
    allowed_domains = ["drugs.com"]
    

    def start_requests(self):
        # Load URLs from a JSON file
        print("Current Directory:", os.getcwd())
        with open('links.json', 'r') as file:
            urls = json.load(file)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # Initialize an item
        interaction_item = InteractionItem()

        # Extract drug name from the URL
        # Assuming the URL format is as you described
        url = response.url
        drug_name = url.split('/')[-1].replace('-index.html', '')

        # Set the extracted drug name
        interaction_item['name'] = drug_name
        interaction_item['major_interactions'] = []
        interaction_item['minor_interactions'] = []
        interaction_item['moderate_interactions'] = []

        # Select all <ul> of the specified class except the last one
        uls = response.css('ul.interactions.ddc-list-column-2')[:-1]
        if not uls:
            uls = response.css('ul.interactions.ddc-list-unstyled:not(.interactions-label)')


        for ul in uls:
            # Iterate over each <li> in the <ul>
            for li in ul.css('li'):
                li_class = li.attrib.get('class', '')
                li_text = li.css('a::text').get().strip()

                # Replace spaces with hyphens and remove parentheses
                formatted_li_text = li_text.replace(' ', '-').replace(',','-').translate(str.maketrans('', '', '()'))

                # Add the formatted text to the appropriate field
                if 'int_3' in li_class:
                    interaction_item['major_interactions'].append(formatted_li_text)
                elif 'int_2' in li_class:
                    interaction_item['minor_interactions'].append(formatted_li_text)
                elif 'int_1' in li_class:
                    interaction_item['moderate_interactions'].append(formatted_li_text)


        yield interaction_item
