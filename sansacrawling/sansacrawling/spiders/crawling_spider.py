from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import re
import time
import random
from slugify import slugify  # Optionally use python-slugify for more control
import bcrypt
from urllib.parse import urljoin
from datetime import datetime, timedelta

class CrawlingSpider(CrawlSpider):
    name = "mycrawler"
    allowed_domains = ["thejobadverts.com"]
    start_urls = [
        "https://thejobadverts.com/jobs/",
    ]

    rules = (
        Rule(LinkExtractor(allow=r"/jobs/"), callback="parse_item"),
    )

    def __init__(self, *args, **kwargs):
        super(CrawlingSpider, self).__init__(*args, **kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run headless
        service = Service("/usr/local/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def round_to_nearest_5000(self, num):
        """Rounds the given number to the nearest 5000."""
        return round(num / 5000) * 5000
    
    def parse_item(self, response):
        description_elements = response.css(".entry-content *:not(style):not(script):not(.entry-meta)::text").getall()
        description = " ".join(description_elements).strip()
        title = response.css("h1::text").get()
        # Create slug from title
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title)  # Remove special characters
        slug = slug.lower().strip()  # Lowercase and trim whitespace
        slug = re.sub(r'\s+', '-', slug)  # Replace spaces with hyphens
        password = '12345678g$'
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        hashed_password_str = hashed_password.decode('utf-8')

        timestamp_text = response.css(".entry-header .meta-date time::text").get()
        timestamp = datetime.strptime(timestamp_text, "%B %d, %Y")  # Adjust format if necessary

        # Calculate the date two weeks ago
        two_weeks_ago = datetime.now() - timedelta(weeks=2)

        # Skip yielding this item if the timestamp is older than two weeks
        if timestamp < two_weeks_ago:
            return  # Don't yield the item if it's more than two weeks old

        # Determine job type based on description content
        job_type = "remote" if "remote" in description.lower() else "onsite"

        # Extract 'requirements' based on 'Qualifications' keyword
        requirements = ""
        qualifications_match = re.search(r"\bQualifications\b(.*)", description, re.IGNORECASE | re.DOTALL)
        if qualifications_match:
            description = description[:qualifications_match.start()].strip()
            requirements = qualifications_match.group(1).strip()

        location_category_price = response.css(".entry-header li a::text").getall()
        location = location_category_price[0] if location_category_price else None
        category = location_category_price[1:-1] if len(location_category_price) > 2 else []
        name = location_category_price[-1] if location_category_price else None
        prespecified_fields = ['COMMUNICATIONS', 'CREATIVES', 'IT', 'MARKETING', 'ICT', 'MEDIA', 'SOCIAL MEDIA', 'EDITORS', 'DATA WORK']

        # Check if any of the category elements are in the prespecified fields
        if not any(cat in prespecified_fields for cat in category):
            return  # Skip yielding this item if none of the categories match
        
        if 'CREATIVES' in category:
            category = 'creative'  # Modify category to 'creative'
        elif 'COMMUNICATIONS' in category:
            category = 'communications'
        elif 'IT' in category:
            category = 'software development'
        elif 'MARKETING' in category:
            category = 'digital marketing'
        elif 'ICT' in category:
            category = 'software development'
        elif 'MEDIA' in category:
            category = 'communications'
        elif 'SOCIAL MEDIA' in category:
            category = 'social media management'
        elif 'EDITORS' in category:
            category = 'communications'
        elif 'DATA WORK' in category:
            category = 'data science'

        # First attempt to extract a price from the description
        price_match = re.search(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b', description)
        if price_match:
            extracted_price_str = price_match.group(0).replace(',', '')
            if len(extracted_price_str) >= 4:
                price = int(extracted_price_str)
            else:
                price = None  # Ignore values with fewer than 4 digits
        else:
            price = None  # No match found

        # Apply additional logic if price is still None
        if price is None:
            first_category = category[0] if category else None
            title = response.css("h1::text").get().lower()

            # Generate and round a random price based on the category or title
            if first_category == 'COMMUNICATIONS':
                price = self.round_to_nearest_5000(random.randint(30000, 60000))
            elif first_category == 'CREATIVES':
                price = self.round_to_nearest_5000(random.randint(25000, 50000))
            elif first_category == 'DATA WORK':
                price = self.round_to_nearest_5000(random.randint(25000, 50000))
            elif first_category == 'EDITORS':
                price = self.round_to_nearest_5000(random.randint(40000, 70000))
            elif first_category == 'IT':
                price = self.round_to_nearest_5000(random.randint(50000, 100000))
            elif first_category == 'ICT':
                price = self.round_to_nearest_5000(random.randint(50000, 100000))
            elif first_category == 'MARKETING':
                price = self.round_to_nearest_5000(random.randint(30000, 60000))
            elif first_category == 'MEDIA':
                price = self.round_to_nearest_5000(random.randint(40000, 70000))
            elif first_category == 'SOCIAL MEDIA':
                price = self.round_to_nearest_5000(random.randint(25000, 50000))
            elif "intern" in title:
                price = self.round_to_nearest_5000(random.randint(15000, 25000))
            elif "manager" in title:
                price = self.round_to_nearest_5000(random.randint(100000, 150000))
        # Get the image URL and convert to absolute URL
        email = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', description)
        item = {
            "title": title,
            "location": location,
            "category": category,
            "price": price,
            "deadline": response.css(".entry-content .entry-meta li::text")[1].get(),
            "description": description,
            "jobtype": job_type,
            "requirements": requirements,
            "currency": "KSH",
            "slug": slug,
            "name": name,
            "user_type": "brand",
            "image": response.css(".featured-image-section img::attr(src)").get(),
            "password": hashed_password_str
        }

        if email:
            item["email"] = email

        yield item

    def __del__(self):
        # Close the Selenium driver when done
        self.driver.quit()

