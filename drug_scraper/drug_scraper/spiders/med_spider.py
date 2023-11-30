from drug_scraper.items import MedicationItem
import string
import scrapy

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
        drug_links_selector = 'ul.ddc-list-column-2 li a:not([href*="/pro/"]):not([href*="/monograph/"])::attr(href)'

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
        item['side_effects'] = self.extract_side_effects(response)




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
        all_uses = []

        # Extracting "uses" based on the breadcrumb
        breadcrumb_selector = 'ol.ddc-breadcrumb-3 li.ddc-breadcrumb-item'
        breadcrumb_items = response.css(breadcrumb_selector)
        treatments_text = breadcrumb_items.css('::text').getall()

        if 'Treatments' in treatments_text:
            treatments_index = treatments_text.index('Treatments')
            if len(breadcrumb_items) > treatments_index + 1:
                breadcrumb_use = breadcrumb_items[treatments_index + 1].css('::text').get().strip().lower()
                if breadcrumb_use:
                    all_uses.append(breadcrumb_use)

        # Always use the backup method as well
        backup_uses = self.backup_uses(response)
        all_uses.extend(backup_uses)

        # Remove duplicates
        return list(set(all_uses))


    def backup_uses(self, response):
        uses_list = []
        # Select all sibling elements following the <h2> tag with the id of "uses"
        target_uses = response.css('h2#uses ~ *')

        for sibling in target_uses:
            # Check if the element is an <a> tag and process it
            links = sibling.css('a[href*="condition"]::text').getall()
            for link_text in links:
                use = link_text.strip().lower()
                if use and use not in uses_list:
                    uses_list.append(use)

        return uses_list

    
    def extract_side_effects(self, response):
    # Locate the header with the id 'side-effects'
        side_effects_header = response.xpath('//h2[@id="side-effects"]')

        # Find all ul elements following this header until 'ddc-related-links'
        # Use the 'following-sibling' axis and stop at the specified class
        side_effects_lists = side_effects_header.xpath(
            'following-sibling::ul[preceding-sibling::div[contains(@class, "ddc-related-links")]]'
        )

        # Extract the side effects from each ul
        side_effects_data = []
        for ul in side_effects_lists:
            effects = ul.xpath('li//text()').getall()
            # Clean up the effects text and add to the list
            cleaned_effects = [effect.strip() for effect in effects if effect.strip()]
            side_effects_data.extend(cleaned_effects)

        return side_effects_data

