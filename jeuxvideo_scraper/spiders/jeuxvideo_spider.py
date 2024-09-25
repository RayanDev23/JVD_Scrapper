import scrapy

class JeuxVideoSpider(scrapy.Spider):
    name = 'jeuxvideo'
    index = 1
    max_pages = 951

    custom_settings = {
        'CONCURRENT_REQUESTS': 32,
        'DOWNLOAD_DELAY': 0.25,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 16,
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'COOKIES_ENABLED': False,
        'RETRY_TIMES': 2,
        'ROBOTSTXT_OBEY': True
    }

    def __init__(self):
        self.visited_urls = set()

    def start_requests(self):
        start_url = f'https://www.jeuxvideo.com/tests/?p={self.index}'
        yield scrapy.Request(url=start_url, callback=self.parse)

    def parse(self, response):
        jeux_links = response.css('a::attr(href)').extract()

        jeux_links = [link for link in jeux_links if '/jeux/' in link]

        jeux_links = [response.urljoin(link) for link in jeux_links]

        self.logger.info(f"Page {self.index}: {len(jeux_links)} liens de jeux trouvés.")

        for link in jeux_links:
            if link not in self.visited_urls:
                self.visited_urls.add(link)
                yield scrapy.Request(url=link, callback=self.parse_jeu)
                self.logger.info(f"Scraping jeu: {link}")

        if self.index < self.max_pages:
            self.index += 1
            next_url = f'https://www.jeuxvideo.com/tests/?p={self.index}'
            self.logger.info(f"Passage à la page {self.index}")
            yield scrapy.Request(url=next_url, callback=self.parse)
        else:
            self.logger.info("Scraping terminé, dernière page atteinte.")

    def parse_jeu(self, response):
        title = response.css('h1::text').get()

        rating = response.css('.gameCharacteristicsMain__gaugeText::text').get()

        developer = response.css('.gameCharacteristicsDetailed__characValue::text').get()

        self.logger.info(f"Jeu extrait: {title} | Note: {rating} | Développeur: {developer.strip() if developer else 'N/A'}")

        yield {
            'title': title,
            'rating': rating,
            'developer': developer.strip() if developer else None
        }
