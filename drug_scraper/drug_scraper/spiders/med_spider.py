from drug_scraper.items import MedicationItem
import string
import scrapy
import re

class MedicationSpider(scrapy.Spider):
    name = 'medication_spider'
    allowed_domains = ['drugs.com']
    base_url = 'https://www.drugs.com/alpha/'
    CLOSESPIDER_ITEMCOUNT = 1  # Stops after scraping 1 items


    def start_requests(self):
        letters = string.ascii_lowercase

        # Generate URLs for two-letter combinations and '{letter}0-9'
        for first_letter in letters:
            single = f"{first_letter}.html"
            yield scrapy.Request(f"{self.base_url}{single}", self.parse)
            # Generate URLs for combinations like 'aa', 'ab', ..., 'az'
            for second_letter in letters:
                if first_letter != second_letter:  # Avoid combinations like 'aa', 'bb', etc.
                    combination = f"{first_letter}{second_letter}.html"
                    yield scrapy.Request(f"{self.base_url}{combination}", self.parse)

            # Generate URL for '{letter}0-9'
            yield scrapy.Request(f"{self.base_url}{first_letter}0-9.html", self.parse)

        # Generate and include the URL for the number range '0-9'
        yield scrapy.Request(self.base_url + '0-9.html', self.parse)
    
    def parse(self, response):
        # Selector for the list of drugs within the 'ul' with the class 'ddc-list-column-2'
        drug_links_selector = 'ul.ddc-list-column-2 li a:not([href*="/pi/"]):not([href*="/pro/"]):not([href*="/monograph/"]):not([href*="/cons/"])::attr(href)'

        # Extract the links
        drug_links = response.css(drug_links_selector).getall()
        for link in drug_links:
            # Join the relative link with the base URL
            full_link = response.urljoin(link)
            # Follow the link to the drug's detail page
            yield scrapy.Request(full_link, callback=self.parse_drug_details)

    def parse_drug_details(self, response):
        # Your parsing code here for the medication page
        # Instantiate an item
        item = MedicationItem()
        # Extract data using CSS or XPath selectors
        item['name'] = response.css('h1::text').get()
        item['drug_classes'] = self.get_drug_class_list(response)
        item['uses'] = self.get_uses(response)
        item["status"] = response.css('.ddc-status-info-item b:contains("Availability") + span::text').get().strip()


        # Yield or return the item
        yield item
        
    def get_drug_class_list(self, response):
        # Find all paragraphs with class 'drug-subtitle'
        target_subtitles = response.css('p.drug-subtitle')

        # If no such elements, return an empty list
        if not target_subtitles:
            return []

        # Extract the drug class list
        drug_class_list = target_subtitles[0].css('a[href*="drug-class"]::text').getall()
        
        return drug_class_list
    
    def get_uses(self, response):
        # Select the header with the id 'uses'
        uses_header = response.xpath('//*[@id="uses"]')

        # Select all following siblings that are paragraphs until the next header
        paragraphs = uses_header.xpath('following-sibling::p[count(preceding-sibling::h2[@id="uses"]) = count(preceding-sibling::h2)]').getall()

        uses = []
        # Extract the text from each paragraph
        for paragraph_html in paragraphs:
            paragraph_selector = scrapy.Selector(text=paragraph_html)
            text = paragraph_selector.xpath('string(.)').get().strip()
            if text:
                uses.append(text)

        return uses

    







