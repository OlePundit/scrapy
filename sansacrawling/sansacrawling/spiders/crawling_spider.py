from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class CrawlingSpider(CrawlSpider):
    name = "mycrawler"
    allowed_domains = ["twitter.com"]
    start_urls = ["https://thejobadverts.com/jobs/"]


    rules = (
        Rule(LinkExtractor(allow="hr_stellar"), callback="parse_item"),
    )

    def parse_item(self, response):