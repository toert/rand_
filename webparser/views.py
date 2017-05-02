from django.shortcuts import render, get_object_or_404
from .models import Ad, CurrentValues


def render_dashboard(request):
    row = get_object_or_404(CurrentValues, id=1)
    buy_ad = Ad.objects.filter(type='buy').first()
    sell_ad = Ad.objects.filter(type='sell').first()
    return render(request, 'index.html', {
        'other_prices': row,
        'buy_ad': buy_ad,
        'sell_ad': sell_ad,
        'percentage': str(buy_ad.price / sell_ad.price * 100)[:5]
    })
