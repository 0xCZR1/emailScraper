import scrapy
import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class EmailSpider(CrawlSpider):
    name = "email_spider"
    allowed_domains = ['uvt.ro']
    start_urls = ['https://www.uvt.ro/']

    rules = (
        Rule(LinkExtractor(allow_domains=allowed_domains), callback='parse_email', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(EmailSpider, self).__init__(*args, **kwargs)
        self.emails_seen = set()

    def parse_email(self, response):
        self.logger.info('Crawling: %s', response.url)

        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        
        potential_emails = re.findall(email_regex, response.text)
        
        for email in potential_emails:
            if self.is_valid_email(email) and email not in self.emails_seen:
                self.emails_seen.add(email)
                yield {'email': email}

    def is_valid_email(self, email):
        if email.count('@') != 1:
            return False
        
        local_part, domain = email.split('@')
        
        if not local_part or not domain:
            return False
        
        if len(local_part) > 64 or len(domain) > 255:
            return False
        
        if domain.count('.') == 0:
            return False
        
        if any(part.startswith('.') or part.endswith('.') for part in [local_part, domain]):
            return False
        
        return True