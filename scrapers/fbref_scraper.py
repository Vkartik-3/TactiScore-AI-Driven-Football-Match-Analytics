# scrapers/fbref_scraper.py
import scrapy
from scrapy.crawler import CrawlerProcess
import logging

class FBrefScraper(scrapy.Spider):
    name = 'fbref_spider'
    
    def __init__(self, league='EPL', season='2023-2024', *args, **kwargs):
        super(FBrefScraper, self).__init__(*args, **kwargs)
        self.start_urls = [f'https://fbref.com/en/comps/{league}/{season}/']
        
    def parse(self, response):
        for match_url in response.css('table.matches a::attr(href)').getall():
            yield response.follow(match_url, self.parse_match)
            
    def parse_match(self, response):
        # Extract detailed match statistics
        home_team = response.css('div.scorebox div:nth-child(1) h1 a::text').get()
        away_team = response.css('div.scorebox div:nth-child(2) h1 a::text').get()
        
        # Extract xG, shots, possession, etc.
        home_xg = float(response.css('div.scorebox div:nth-child(1) div.score_xg::text').get() or 0)
        away_xg = float(response.css('div.scorebox div:nth-child(2) div.score_xg::text').get() or 0)
        
        # Advanced stats from tables
        stats = {}
        for stat_row in response.css('table#stats_squads_standard_for tr'):
            stat_name = stat_row.css('th::text').get()
            home_value = stat_row.css('td:nth-child(2)::text').get()
            away_value = stat_row.css('td:nth-child(3)::text').get()
            if stat_name and home_value and away_value:
                stats[f'home_{stat_name}'] = home_value
                stats[f'away_{stat_name}'] = away_value
        
        yield {
            'match_date': response.css('div.scorebox div.scorebox_meta div::text').get(),
            'home_team': home_team,
            'away_team': away_team,
            'home_xg': home_xg,
            'away_xg': away_xg,
            'stats': stats
        }

def run_scraper():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data/raw/fbref_matches.json'
    })
    process.crawl(FBrefScraper)
    process.start()
    
if __name__ == "__main__":
    run_scraper()