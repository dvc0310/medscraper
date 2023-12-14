import scrapy
import json

class Sideeffectspider2Spider(scrapy.Spider):
    name = "sideeffectspider2"
    allowed_domains = ["drugs.com"]
    start_urls = ["https://drugs.com"]
    
    def __init__(self, *args, **kwargs):
        super(Sideeffectspider2Spider, self).__init__(*args, **kwargs)
        with open('processed_data5.json', 'r') as json_file:
            self.drugs_data = json.load(json_file)

    def start_requests(self):
        for drug in self.drugs_data:
            generic_name = drug.get('generic_name')  # Assuming 'generic_name' is the key in your drugs_data
            url = f"https://www.drugs.com/sfx/{generic_name}-side-effects.html"
            if url:
                # Pass the generic_name in the meta
                yield scrapy.Request(url, callback=self.parse, meta={'generic_name': generic_name})
        

    def parse(self, response):
        
        # Extract serious side effects
        serious_side_effects = response.xpath("//h2[@id='serious-side-effects']/following-sibling::ul[1]/li")
        serious_effects_list = serious_side_effects.xpath(".//text()").getall()

        # Extract other side effects
        other_side_effects = response.xpath("//h2[contains(text(), 'Other side effects')]/following-sibling::ul[1]/li")
        other_effects_list = other_side_effects.xpath(".//text()").getall()

        # Combine the lists of side effects
        combined_effects_list = serious_effects_list + other_effects_list
        
        # If no specific side effects are found, look for common or rare side effects
        if not combined_effects_list:
            # Find headers that contain 'common' or 'rare' and capture the following list items
            keyword_side_effects = response.xpath("//h2[contains(., 'common') or contains(., 'rare')]/following-sibling::ul[1]/li | //h2[contains(., 'common') or contains(., 'rare')]/following-sibling::ol[1]/li")
            combined_effects_list = keyword_side_effects.xpath(".//text()").getall()

        # Create the item to return
        item = {
            'generic_name': response.meta.get('generic_name', 'Unknown'), 
            'side_effects': combined_effects_list,
            'serious_effects_list': serious_effects_list
        }
        
        return item

        
