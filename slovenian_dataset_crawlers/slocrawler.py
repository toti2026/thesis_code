import requests
from bs4 import BeautifulSoup
from ratelimit import limits, sleep_and_retry
import time 
ONE_MINUTE = 60

class SloCrawler:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_url(keyword, frm, to, page):
        return f"https://www.rtvslo.si/iskalnik?c_mod=search&q={keyword}&from={frm}&to={to}&a=6&page={page}"
    
    def parseHtml(self, keyword, frm, to, page = 0):
        url = self.get_url(keyword, frm, to, page)
        headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
        soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
        articles = []
        
        for article in soup.select('.article-archive-item .md-news > a[href]'):
            articles.append(article['href'])

        with open(f'converted_data_{keyword}.csv', 'a') as f:
            for article in articles:
                f.write(f"{article} \n\n")

        time.sleep(5)
        current_page = soup.select('.pagination .page-item.active')[1] # returns two elements referring to the active item
        try:
            next_page = current_page.find_next_sibling().select_one('a.page-link').text
            self.parseHtml(keyword, frm, to, int(next_page) - 1)
        except:
            pass    
    
    def parse_ranges(self, frm, to):
        self.parseHtml(frm, to)
    
    def main(self):
        old_date_ranges = [('2022-02-01', '2022-04-30'), ('2022-05-01', '2022-07-31'), ('2022-08-01', '2022-10-31'), ('2022-11-01', '2022-12-31'), ('2023-01-01', '2023-03-31'), ('2023-04-01', '2023-06-30'), ('2023-07-01', '2023-09-30'), ('2023-10-01', '2023-12-31'), ('2024-01-01', '2024-03-31'), ('2024-04-01', '2024-06-30'), ('2024-07-01', '2024-09-30'), ('2024-10-01', '2024-12-31'), ('2025-01-01', '2025-03-31'), ('2025-04-01', '2025-06-30')]
        date_ranges =[('2024-04-01', '2024-06-30'), ('2024-07-01', '2024-09-30'), ('2024-10-01', '2024-12-31'), ('2025-01-01', '2025-03-31'), ('2025-04-01', '2025-06-30')]
        for range in old_date_ranges:
            print(f"Querying for dates: {range}")
            self.parseHtml('slovenija', *range)
            time.sleep(5)


if __name__ == "__main__":
    SloCrawler().main()