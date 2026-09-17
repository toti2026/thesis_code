import requests
from bs4 import BeautifulSoup
import time 
import json 
from tqdm import tqdm

SLO_MONTH = { 
    'januar': '01',
    'februar': '02',
    'marec': '03',
    'april': '04',
    'maj': '05',
    'junij': '06',
    'julij': '07',
    'avgust': '08',
    'september': '09',
    'oktober': '10',
    'november': '11',
    'decembra': '12'
}

def get_batches(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

def parse_rtvoslo_date(date):
    try: 
        split_date = date.split("\n")[1]
        day, rest = split_date.split(". ")
        day = day.strip()
        month, year, *rest = rest.split(" ")
        
        parsed_month = SLO_MONTH.get(month, 13)

        return f"{day}-{parsed_month}-{year}"
    except:
        print('date conversion failed')


"""
Used to crawl the article of rtvslo.si
"""

class SloArticleCrawler: 
    def __init__(self):
        pass

    def read(self, url):
        try: 
            headers = { 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'}
            soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
            title = soup.select_one('.article-header h1').get_text()
            subtitle = soup.select_one('.article-header .subtitle').get_text()
            slug = soup.select_one('.article-header .lead').get_text()
            article_meta = soup.select_one('.article-meta .publish-meta')
            article_meta = article_meta.get_text() if article_meta else None
            formatted_date = parse_rtvoslo_date(article_meta) if article_meta else ""
            article_body = soup.select_one('article.article')
            paragraphs = article_body.findChildren('p')
            content = ""
            article_tags = soup.select_one('.article-tags')
            article_tags = article_tags.findChildren('a') if article_tags else []
            tags = []

            for tag in article_tags:
                tags.append(tag.get_text())

            for p in paragraphs:
                content += p.get_text()

            return { 'title': title, 'subtitle': subtitle, 'slug': slug, 'date': formatted_date, 'tags': tags, 'content': content }
        except:
            print(url + " failed")
        
        

    def process_files(self, filename, out_dir):
        f = open(filename, 'r')
        lines = f.readlines()
        lines = list(filter(lambda x: x != "\n", lines))
        batch_size = 50

        print(f'Started reading {len(lines)} lines in {int(len(lines)/batch_size)} batches.')
        for idx, batch in enumerate(get_batches(lines, batch_size)):
            to_write = {}
            print(f"Reading batch {idx+1} with {len(batch)} items")
            
            for url in tqdm(batch):
                url = url.strip()
                article_id = url.split('/')[-1]
                data = self.read(url)
                to_write[article_id] = data
                time.sleep(3.5)
            
            with open(f"{out_dir}/{idx+1}.json", 'w') as f:
                json.dump(to_write, f,  ensure_ascii=False, indent=4)
            
            time.sleep(5)

    def main(self):
        #self.read('https://www.rtvslo.si/dostopno/clanki/v-sempetru-se-zacenja-zlata-liga-narodov-v-odbojki-sede/625657')
        self.process_files('converted_data_slovenija.csv', 'data/slovenija_2025')

if __name__ == "__main__":
    SloArticleCrawler().main()