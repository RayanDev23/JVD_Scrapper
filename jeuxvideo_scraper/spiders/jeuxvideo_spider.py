import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

class JeuxVideoSpider(scrapy.Spider):
    name = 'jeuxvideo'
    start_urls = ['https://www.jeuxvideo.com/tests.htm',
                'https://www.jeuxvideo.com/tests/?p=3',
                'https://www.jeuxvideo.com/tests/?p=2',
                'https://www.jeuxvideo.com/tests/?p=4',
                'https://www.jeuxvideo.com/tests/?p=5',
                'https://www.jeuxvideo.com/tests/?p=6',
                'https://www.jeuxvideo.com/tests/?p=7',
                'https://www.jeuxvideo.com/tests/?p=8',
]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,  # Limite le nombre de requêtes simultanées
        'DOWNLOAD_DELAY': 2,  # Délai entre les requêtes
    }

    def __init__(self):
        self.visited_urls = set()  # Pour stocker les URLs déjà visitées

    def start_requests(self):
        # Utiliser Selenium pour la première requête
        yield SeleniumRequest(url=self.start_urls[0], callback=self.parse, wait_time=5)

    def parse(self, response):
        # Récupérer le pilote Selenium de la réponse
        driver = response.meta.get('driver')

        # Récupérer les liens des jeux vidéo sur la page d'accueil
        jeux_links = response.css('a::attr(href)').extract()

        # Filtrer les liens qui correspondent à des jeux vidéo
        jeux_links = [link for link in jeux_links if '/jeux/' in link]

        # Ajouter le schéma manquant aux liens extraits
        jeux_links = [response.urljoin(link) for link in jeux_links]

        # Visiter chaque lien de jeu vidéo pour extraire les informations
        for link in jeux_links:
            if link not in self.visited_urls:
                self.visited_urls.add(link)
                yield SeleniumRequest(url=link, callback=self.parse_jeu, wait_time=5)

        # Trouver et cliquer sur le bouton de pagination suivante s'il existe
        try:
            next_button = driver.find_element(By.XPATH, '//a[@class="pagination__next"]/span')
            if next_button:
                next_button.click()

                # Attendre que la nouvelle page soit chargée
                WebDriverWait(driver, 10).until(EC.url_changes(response.url))

                # Récupérer la nouvelle URL après le chargement de la page
                new_url = driver.current_url

                # Mettre à jour la réponse avec la nouvelle URL
                yield SeleniumRequest(url=new_url, callback=self.parse, wait_time=5)
        except NoSuchElementException:
            self.logger.info("Bouton de pagination suivante non trouvé")

    def parse_jeu(self, response):
        # Extraire le titre du jeu
        title = response.css('h1::text').get()

        # Extraire la note du jeu
        rating = response.css('.gameCharacteristicsMain__gaugeText::text').get()

        # Extraire le développeur du jeu
        developer = response.css('.gameCharacteristicsDetailed__characValue::text').get()

        yield {
            'title': title,
            'rating': rating,
            'developer': developer.strip() if developer else None  # Supprimer les espaces inutiles
        }

# scrapy crawl jeuxvideo -o jeuxvideo_data.json