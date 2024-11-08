# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv


class SansacrawlingPipeline:
    def process_item(self, item, spider):
        return item
    
class CsvExportPipeline:
    def open_spider(self, spider):
        # Open the CSV file and set up the writer
        self.file = open("output.csv", "w", newline='', encoding="utf-8")
        self.writer = csv.writer(self.file)
        # Write header row (keys of the first item yielded)
        self.writer.writerow([
            "title", "location", "category", "price", 
            "deadline", "description", "jobtype", "requirements", 
            "currency", "slug", "name", "user_type", "email", 
            "images", "password"
        ])

    def close_spider(self, spider):
        # Close the file when spider finishes
        self.file.close()

    def process_item(self, item, spider):
        # Write each scraped item to a row in the CSV file
        self.writer.writerow([
            item.get("title"), item.get("location"),
            item.get("category"), item.get("price"), item.get("deadline"),
            item.get("description"), item.get("jobtype"), item.get("requirements"),
            item.get("currency"), item.get("slug"), item.get("name"),
            item.get("user_type"), item.get("email"), item.get("images"),
            item.get("password")
        ])
        return item