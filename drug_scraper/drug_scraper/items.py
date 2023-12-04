# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MedicationItem(scrapy.Item):
    name = scrapy.Field()
    generic_name = scrapy.Field()
    ratings = scrapy.Field()
    drug_classes = scrapy.Field()
    uses = scrapy.Field()
    status = scrapy.Field()
    schedule = scrapy.Field()
    interactions = scrapy.Field()
    side_effects = scrapy.Field()

