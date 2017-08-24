from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from decimal import Decimal
import re


class BitParser():
    BIT_SITE_URL = 'https://localbitcoins.com/'
    BUY_ADS_URL = 'ru/buy-bitcoins-online/RU/russian-federation/perevody-cherez-konkretnyi-bank/'
    SELL_ADS_URL = 'ru/sell-bitcoins-online/RU/russian-federation/perevody-cherez-konkretnyi-bank/'

    SLEEP_TIME = 3

    def __init__(self, profile_path):
        self.profile = webdriver.FirefoxProfile(profile_path)
        self.driver = webdriver.Firefox(firefox_profile=self.profile)

    def parse_best_ad(self, purpose, bank_name, stop_list, good_words):
        if purpose == 'buy':
            url = self.BIT_SITE_URL + self.BUY_ADS_URL
            is_desc = False
        elif purpose == 'sell':
            url = self.BIT_SITE_URL + self.SELL_ADS_URL
            is_desc = True
        else:
            return None
        self.go_to_url(url)
        sleep(self.SLEEP_TIME)
        page_count = self.parse_page_count()
        ads = []
        for page in range(1, page_count + 1):
            if page != 1:
                self.go_to_url('{}?page={}'.format(url, page))
                sleep(self.SLEEP_TIME)
            ads.extend(list(self.collect_ads_from_page()))
        ads = sorted(ads, key=lambda ad: ad['price'], reverse=is_desc)

        for ad in ads:
            self.driver.get(ad['url'])
            if self.check_entry_conditions(bank_name, stop_list, good_words):
                return ad

    def check_entry_conditions(self, required_list, stop_list, not_stop_words):
        adlisting = self.driver.find_elements_by_class_name('adlisting')[0]
        raw_html = adlisting.get_attribute('innerHTML').lower()
        if not required_list and not stop_list and not_stop_words:
            return True
        for word in required_list:
            if re.findall(word, raw_html):
                break
            if word == required_list[-1]:
                return False
        for word in stop_list:
            if stop_list and re.findall(word, raw_html):
                for good_word in not_stop_words:
                    if re.findall(good_word, raw_html):
                        return True
                return False
        return True

    def parse_page_count(self):
        adlisting = self.driver.find_elements_by_class_name('pagination')[0]
        raw_html = adlisting.get_attribute('innerHTML')
        soup = BeautifulSoup(raw_html, 'html.parser')
        li_count = len(soup.find_all('li'))
        return li_count - 2

    def collect_info_about_ad(self, url):
        self.go_to_url(url)
        adlisting = self.driver.find_elements_by_class_name('adlisting')[0]
        raw_html = adlisting.get_attribute('innerHTML')
        soup = BeautifulSoup(raw_html, 'html.parser')
        price = re.findall(r'([\d\.]+) RUB / BTC', soup.find('h4', {'id': 'ad_price'}).text)[0]
        username = re.findall(r'/accounts/profile/([^/]+)/',
                              soup.find('a', {'class': 'profile-link'},
                                        href=True)['href'])
        return {
            'url': url,
            'header': soup.find_all('h1')[1].text,
            'price': price,
            'username': username
        }

    def collect_ads_from_page(self):
        sleep(self.SLEEP_TIME)
        table = self.driver.find_elements_by_class_name('table-bitcoins')[0]
        soup = BeautifulSoup(table.get_attribute('innerHTML'), 'html.parser')
        for ad in soup.find_all('tr')[1:]:
            try:
                price = re.findall(r'([\d\.]+) RUB', ad.find('td', {'class': 'column-price'}).text)[0]
            except IndexError:
                return None
            url_slug = ad.find('a', {'class': 'btn-default'}, href=True)['href']
            absolute_url = '{}{}'.format(self.BIT_SITE_URL, url_slug)
            yield {'url': absolute_url,
                   'price': Decimal(price)}

    def multiselect_set_selections(self, element_id, labels):
        el = self.driver.find_element_by_id(element_id)
        for option in el.find_elements_by_tag_name('option'):
            if option.text in labels:
                option.click()

    def check_captcha(self):
        try:
            self.driver.switch_to.frame(self.driver.find_elements_by_tag_name("iframe")[0])
            self.driver.find_element_by_id('recaptcha-anchor')
        except:
            self.driver.switch_to.default_content()
            return False
        self.driver.switch_to.default_content()
        return True

    def get_btc_e_price(self):
        self.go_to_url('https://btc-e.com/exchange/btc_rur')
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        return {'buy': Decimal(soup.find('span', {'id': 'min_price'}).text),
                'sell': Decimal(soup.find('span', {'id': 'max_price'}).text)}

    def go_to_url(self, url):
        try:
            self.driver.get(url)
        except:
            sleep(self.SLEEP_TIME)
            self.driver.get(url)


if __name__ == '__main__':
    parser = BitParser('/Users/MacBook/Library/Application Support/Firefox/Profiles/ynjsgjro.default')
    while True:
        print(parser.parse_best_ad('Сбербанк', ['Киви', 'Qiwi'], ['Kiwi'], ['Sber']))
        sleep(60)
