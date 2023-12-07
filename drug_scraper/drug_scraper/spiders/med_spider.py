from drug_scraper.items import MedicationItem
import string
import scrapy
import re
import pdb

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

    

    def get_alternative_names(self, response):
        alternative_names = []
        self.logger.info("Starting to extract alternative names")
        #pdb.set_trace()
        # Extract the primary name (usually the one in the <h1> tag)
        primary_name = response.css('h1::text').get()
        if primary_name:
            alternative_names.append(primary_name.strip().lower())

        # Extract the generic name from 'drug-subtitle'
        # First selector for text directly following the <b> tag
        generic_name_selector_1 = """
        //p[contains(@class, 'drug-subtitle')]/b[contains(text(), 'Generic name:')]/
        following-sibling::node()[not(self::br)][1]/descendant-or-self::text()
        """

        # Second selector for text within an anchor tag following the <b> tag
        generic_name_selector_2 = """
        //p[contains(@class, 'drug-subtitle')]/b[contains(text(), 'Generic name:')]/
        following-sibling::a[1]/text()
        """

        generic_name = response.xpath(generic_name_selector_2).get()
        if not generic_name:
            generic_name = response.xpath(generic_name_selector_1).get()

        alternative_names.append(generic_name.strip().lower())

        # Selector for links starting with '/drug-interactions'
        interaction_links_selector = 'a[href^="/drug-interactions/"]::attr(href)'

        # Extract the links
        interaction_links = response.css(interaction_links_selector).getall()
        for link in interaction_links:
            # Extract the generic name from the link
            generic_name = link.split('/')[2].split('.')[0].lower()
            if ',' in generic_name:
                generic_name = generic_name.split(',')[0]
            if generic_name:
                alternative_names.append(generic_name)

        # Existing logic for extracting generic and brand names...

        return list(alternative_names)


    def parse_drug_details(self, response):
        item = MedicationItem()
        item['name'] = response.css('h1::text').get().strip()

        # Use the new function to get a list of alternative names
        item['alternative_names'] = self.get_alternative_names(response)

        # Parse other details...
        item['drug_classes'] = self.get_drug_class_list(response)
        item['uses'] = self.get_uses(response)
        item["status"] = response.css('.ddc-status-info-item b:contains("Availability") + span::text').get().strip()
        item['generic_name'] = item['alternative_names'][-1]
        item['alternative_names'] = list(set(item['alternative_names']))
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

        # Select all following siblings that are paragraphs or list items until the next header
        content_nodes = uses_header.xpath('following-sibling::p[count(preceding-sibling::h2[@id="uses"]) = count(preceding-sibling::h2)] | ' \
                                        'following-sibling::ul[count(preceding-sibling::h2[@id="uses"]) = count(preceding-sibling::h2)]/li')

        uses = []
        # Extract the text from each paragraph and list item
        for node in content_nodes:
            text = node.xpath('string(.)').get().strip()
            if text:
                uses.append(text)

        return uses


    
"""     def start_requests(self):
        # Debugging: Specific URLs
        debug_urls = [
            'https://www.drugs.com/mtm/aquoral.html',
            'https://www.drugs.com/Adzynma.html',
            # Add any specific URLs you want to debug
        ]

        for url in debug_urls:
            yield scrapy.Request(url, self.parse_drug_details)  # Directly call parse_drug_details for debugging
 """
    






