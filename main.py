import requests
import re
from typing import List, Dict, Literal
from bs4 import BeautifulSoup
from mongo_manager import mongo


def correct_tag_text(tag_text: str, return_type: Literal['string', 'float'] = 'string'):
    to_replace = ['  ', '\n']
    for item in to_replace:
        tag_text = tag_text.replace(item, '')
    if return_type == 'float':
        tag_text = re.match(r'R\$ (\d+\,\d+)', tag_text).group(1)
        tag_text = float(tag_text.replace(',', '.'))
    return tag_text


def try_get_info(content: BeautifulSoup, name: str, attrs: Dict):
    try:
        return content.find(name=name, attrs=attrs).get_text()
    except AttributeError:
        return 'Not found'


def new_get_useful_info(page_content: BeautifulSoup):
    gathered_info = []
    for vinyl_info in page_content.find_all(name='div', attrs={'class': 'media search-teaser'}):
        media_left = vinyl_info.find('div', attrs={'class': 'media-left'})
        media_body = vinyl_info.find('div', attrs={'class': 'media-body'})
        img_url = media_left.find('img', attrs={'class': 'item-cover media-object'})['src']
        vinyl_name = try_get_info(media_body, name='h4', attrs={'class': 'media-heading'})
        band_name = try_get_info(media_body, name='h5', attrs={'class': 'media-heading'})
        vinyl_price = try_get_info(media_body, name='button', attrs={'class': 'price'})
        special_info = try_get_info(media_body, name='div', attrs={'class': 'breakable-label'})
        gathered_info.append({
            'vinyl_name': correct_tag_text(vinyl_name),
            'band_name': correct_tag_text(band_name),
            'special_info': correct_tag_text(special_info),
            'img_url': img_url,
            'price': correct_tag_text(vinyl_price, 'float')
        })
    mongo.insert_vinyl_info(gathered_info)


class IMusicWebScraping:
    def __init__(self, search_params: List[str]):
        self._base_url = 'https://imusic.br.com/vinyl/search?query={}'
        self._search_params = search_params

    def main(self):
        for term in self._search_params:
            page_info = self._get_page_content(term)
            new_get_useful_info(page_info)

    def _get_page_content(self, search_term: str):
        r = requests.get(self._base_url.format(search_term))
        return BeautifulSoup(r.content, features="html.parser")


if __name__ == '__main__':
    scraping = IMusicWebScraping(['mastodon'])
    scraping.main()
