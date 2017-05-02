from django.db import models


TYPES_OF_AD = (
    ('buy', 'Обьявление о продаже клиенту'),
    ('sell', 'Обьявление о покупке у клиента')
)

TYPES_OF_WORDS = (
    ('bank', 'Банки'),
    ('stop_list', 'Стоп-лист'),
    ('not_stop_list', 'Не стоп-лист')
)

TYPES_OF_STEP = (
    ('percent', 'Проценты от BTC-E'),
    ('money', 'В рублях от лучшего обьявления')
)

class CurrentValues(models.Model):
    best_sell_price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    best_buy_price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    btc_e_sell_price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    btc_e_buy_price = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)


class Ad(models.Model):

    ad_id = models.CharField(max_length=40, db_index=True, verbose_name='ID объявления на localbitcoins')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', default=0.10)
    type = models.CharField(max_length=80, choices=TYPES_OF_AD, verbose_name='Тип обьявления')
    bank_name = models.CharField(max_length=80)
    account_info = models.TextField()
    msg = models.TextField()
    type_step = models.CharField(max_length=80, choices=TYPES_OF_STEP, default='money', verbose_name='Тип шага')
    step = models.IntegerField(verbose_name='Шаг')
    #update_time = models.IntegerField(verbose_name='Обновлять каждые(сек)')

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Мои объявления'

    def __str__(self):
        return '{}/{}/{}'.format(self.ad_id, self.type, self.price)


class AdAttribute(models.Model):
    ad = models.ForeignKey(Ad, related_name='Ключевые_слова', db_index=True, verbose_name='Обьявление')
    attribute_name = models.CharField(max_length=80, choices=TYPES_OF_WORDS, verbose_name='Тип')
    attribute_value = models.CharField(max_length=200, verbose_name='Значение')

    class Meta:
        verbose_name = 'Ключевое слово'
        verbose_name_plural = 'Ключевые слова'

    def __str__(self):
        return '{}-{}-{}'.format(self.ad.ad_id, self.attribute_name, self.attribute_value)
