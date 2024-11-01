from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CrawlingSpider(CrawlSpider):
    name = "mycrawler"
    allowed_domains = ["thejobadverts.com"]
    start_urls = [
        "https://thejobadverts.com/jobs/",
        "https://thejobadverts.com/jobs/it-projects-assistant/"
    ]


    rules = (
        Rule(LinkExtractor(allow=r"/jobs/"), callback="parse_item"),
    )

    def parse_item(self, response):
        yield{
            "title": response.css("h1::text").get(),
            "location_category_price": response.css("header ul li::text").getall(),
            "deadline": response.css(".entry-content .entry-meta li::text")[1].get(),
            "description": " ".join(
                response.css(".entry-content *::text").getall()
            ).strip()        
        }