import unittest
import sys
from scrapy.http import TextResponse
from scrapy.http import HtmlResponse
import sys
import os

# Calculate the path to the root of your Scrapy project
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# Add the project root to the PYTHONPATH
sys.path.append(project_root)

# Now you can import your spider
from drug_scraper.spiders.med_spider import MedicationSpider


class TestMySpider(unittest.TestCase):
    def test_one(self):
        sample_html = '''
        <html>
            <body>
                <main id="container" class="ddc-width-container">
                    <div id="contentWrap">
                        <div id="content" class="content">
                            <div class="contentHead"></div>
                            <div class="contentBox">
                                <div class="ddc-pronounce-title">
                                    <h1>Abilify</h1>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
            </body>
        </html>
        '''

        # The URL we're going to pretend we're scraping
        test_url = 'http://example.com/test'

        # Create a Scrapy TextResponse object
        response = TextResponse(url=test_url,
                                body=sample_html,
                                encoding='utf-8')

        # Instantiate the spider
        spider = MedicationSpider()

        # Call the parse function with the fake response
        result = next(spider.parse(response))

        # Check if the extracted data is correct
        self.assertEqual(result['name'], 'Abilify')
        
    def test_get_drug_class_list(self):
        # Create a sample HTML with the expected structure
        sample_html = '''
        <html>
            <body>
                <p class="drug-subtitle">
                    <a href="some-drug-class">DrugClass1</a>
                    <a href="some-drug-class">DrugClass2</a>
                </p>
                <!-- More HTML content -->
            </body>
        </html>
        '''
        # Create a fake response object
        response = HtmlResponse(url='http://example.com', body=sample_html, encoding='utf-8')

        # Instantiate the spider
        spider = MedicationSpider()

        # Call the function to test
        drug_class_list = spider.get_drug_class_list(response)

        # Check if the function's output is as expected
        self.assertEqual(drug_class_list, ['DrugClass1', 'DrugClass2'])

    def test_get_uses(self):
        # Sample HTML snippet containing the breadcrumb for "Treatments"
        html = '''
        <ol class="ddc-breadcrumb-3">
            <li class="ddc-breadcrumb-item">Home</li>
            <li class="ddc-breadcrumb-item">Treatments</li>
            <li class="ddc-breadcrumb-item">Abilify</li>
        </ol>
        '''
        spider = MedicationSpider()
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        uses = spider.get_uses(response)
        self.assertEqual(uses, 'Abilify')

    def test_backup_uses(self):
        # Sample HTML snippet for the backup uses method
        html = '''
        <h2 id="uses">Uses</h2>
        <a href="condition1.html">Condition1</a>
        <a href="condition2.html">Condition2</a>
        <h2 id="other">Uses</h2>
        <a href="condition1.html">Condition1</a>
        <a href="condition2.html">Condition2</a>
        '''
        spider = MedicationSpider()
        response = HtmlResponse(url='http://example.com', body=html, encoding='utf-8')
        uses_list = spider.backup_uses(response)
        self.assertEqual(uses_list, ['condition1', 'condition2'])


        
if __name__ == "__main__":
    unittest.main()