from celery.task import task
from .models import Ad, AdAttribute, CurrentValues
from .parse_local import BitParser
from .localbitcoin_api import LocalBitcoin
from os import getenv
from decimal import Decimal

api = LocalBitcoin(getenv('hmac_auth_key'), getenv('hmac_auth_secret'))


def queryset_to_list(queryset):
    return [result[0] for result in list(queryset)]


def lower_list(list):
    return [word.lower() for word in list]


@task
def update_current_values():
    parser = BitParser()
    row, state = CurrentValues.objects.get_or_create(id=1)
    row.best_sell_price = parser.parse_best_ad('sell', bank_name=[], stop_list=[], good_words=[])['price']
    row.best_buy_price = parser.parse_best_ad('buy', bank_name=[], stop_list=[], good_words=[])['price']
    btc_prices = parser.get_btc_e_price()
    row.btc_e_sell_price = btc_prices['sell']
    row.btc_e_buy_price = btc_prices['buy']
    row.save()
    parser.driver.quit()




def calculate_new_price(ad, btc_e_prices, best_price=None):
    if ad.type == 'buy':
        if ad.price != best_price and best_price is not None and ad.type_step == 'money':
            new_price = best_price - ad.step
        elif ad.price != best_price and (best_price is None or ad.type_step == 'percent'):
            new_price = btc_e_prices['buy'] * ad.step/100
        else:
            return None
        new_price = max(new_price, btc_e_prices['buy'])
    if ad.type == 'sell':
        if ad.price != best_price and best_price is not None and ad.type_step == 'money':
            new_price = best_price + ad.step
        elif ad.price != best_price and (best_price is None or ad.type_step == 'percent'):
            new_price = btc_e_prices['sell'] * ad.step/100
        else:
            return None
        new_price = min(new_price, btc_e_prices['sell'])
    return new_price


@task
def update_ads_price():
    all_ads = Ad.objects.all()
    parser = BitParser()
    btc_price = parser.get_btc_e_price()
    for ad in all_ads:
        if ad.type_step == 'money':
            bank_list = queryset_to_list(AdAttribute.objects.filter(ad=ad)
                                         .filter(attribute_name='bank').values_list('attribute_value'))
            stop_list = queryset_to_list(AdAttribute.objects.filter(ad=ad)
                                         .filter(attribute_name='stop_list').values_list('attribute_value'))
            not_stop_list = queryset_to_list(AdAttribute.objects.filter(ad=ad)
                                             .filter(attribute_name='not_stop_list').values_list('attribute_value'))

            best_price = parser.parse_best_ad(purpose=ad.type,
                                              bank_name=lower_list(bank_list),
                                              stop_list=lower_list(stop_list),
                                              good_words=lower_list(not_stop_list))['price']
            print('BEST  PRICE IS ', best_price)
            new_price = calculate_new_price(ad, btc_price, best_price)
        else:
            new_price = calculate_new_price(ad, btc_price)
        if new_price is not None:
            print(new_price)
            ad.price = Decimal(new_price)
            make_a_requests(ad)
            ad.save()

    parser.driver.quit()


def make_a_requests(ad):
    params = {  "currency": "RUB",
                 "require_identification": False,
                 "city": "Moscow",
                 "price_equation": str(ad.price),
                 "lon": 37,
                 "lat": 55,
                 "bank_name": ad.bank_name,
                 "msg": ad.msg,
                 "sms_verification_required": False,
                 "require_trusted_by_advertiser": False,
                 "countrycode": "RU",
                 "ad_id": ad.ad_id,
                 "track_max_amount": False,
                 "location_string": "Moscow",
                 "account_info": ad.account_info
                }

    api.sendRequest(endpoint='/api/ad/{}/'.format(ad.ad_id),
                    params=params,
                    method='post')