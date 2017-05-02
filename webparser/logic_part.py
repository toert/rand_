from parse_local import BitParser
from localbitcoin_api import LocalBitcoin
import json
import re
from time import sleep


def read_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as data:
        return json.load(data)


def load_json(filepath, data):
    with open(filepath, 'w') as outfile:
        json.dump(data, outfile)


def get_id_from_url(url):
    return re.findall('ad/(\d+)/', url)[0]


def generate_keywords(*args):
    return [word.lower() for word in args]


def update_buy_price(parser, own_ad_params, bank, stop_list, not_stop_list):
    ad = parser.parse_best_ad('buy', bank, stop_list, not_stop_list)

    if get_id_from_url(ad['url']) != own_ad_params['ad_id']:
        new_price = ad['price'] - own_ad_params['step']
        btc_buy_price = parser.get_btc_e_price()['buy_price']
        new_price = max(new_price, btc_buy_price)
        own_ad_params['price_equation'] = str(new_price)
        print(api.sendRequest(endpoint='/api/ad/{}/'.format(own_ad_params['ad_id']),
                       params=own_ad_params,
                       method='post'))
        print('Цена покупки для клиента изменена: ', new_price)
    else:
        print('Цена покупки осталась прежней!')


def update_sell_price(parser, own_ad_params, bank, stop_list, not_stop_list):
    ad = parser.parse_best_ad('sell', bank, stop_list, not_stop_list)

    if get_id_from_url(ad['url']) != own_ad_params['ad_id']:
        new_price = ad['price'] + own_ad_params['step']
        btc_sell_price = parser.get_btc_e_price()['sell_price']
        new_price = min(new_price, btc_sell_price)
        own_ad_params['price_equation'] = str(new_price)
        print(api.sendRequest(endpoint='/api/ad/{}/'.format(own_ad_params['ad_id']),
                        params=own_ad_params,
                        method='post'))
        print('Цена продажи для клиента изменена:', new_price)
    else:
        print('Цена продажи осталась прежней!')


if __name__ == '__main__':
    common_config = read_json('common_config.json')
    bank = common_config['bank']
    stop_list = common_config['stop_list']
    not_stop_list = common_config['not_stop_list']
    sell_config = read_json('sell_config.json')
    buy_config = read_json('buy_config.json')
    api = LocalBitcoin(common_config['hmac_auth_key'], common_config['hmac_auth_secret'])

    parser = BitParser()
    while True:
        print('______')
        update_sell_price(parser, sell_config, generate_keywords(*bank),
                          generate_keywords(*stop_list), generate_keywords(*not_stop_list))
        update_buy_price(parser, buy_config, generate_keywords(*bank),
                         generate_keywords(*stop_list), generate_keywords(*not_stop_list))
        sleep(120)
