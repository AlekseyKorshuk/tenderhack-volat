# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from api.controller import *
from apps.app.controller import *
from django.views.generic import View
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.app.models import Auctions
import json
from django.db import models
import random
from django.shortcuts import redirect
import datetime

def index(request):
    ids = get_profiles_list()
    return redirect(f'/profile/{random.choice(ids)}')
    # return HttpResponse(html_template.render(context, request))


def team(request, *args, **kwargs):
    user_id = kwargs.get('user_id')

    html_template = loader.get_template('team.html')
    
    context = {
        'segment': 'team',
        'profile': {
            'company': {
                'id': user_id
            }
        },
    }
    return HttpResponse(html_template.render(context, request))


def how(request, *args, **kwargs):
    user_id = kwargs.get('user_id')

    html_template = loader.get_template('how.html')

    context = {
        'segment': 'how',
        'profile': {
            'company': {
                'id': user_id
            }
        },
    }
    return HttpResponse(html_template.render(context, request))


def profile(request, *args, **kwargs):

    user_id = kwargs.get('user_id')

    profile = get_profile(user_id)
    achievements_list = get_achievements(user_id)

    achievements = {
        'SignedDocument': {
            'items': [],
            'unlocked': False
        },
        'SignedDocumentOne': {
            'items': [],
            'unlocked': False
        },
        'SignedDocumentTen': {
            'items': [],
            'unlocked': False
        },
        'SignedDocumentHundred': {
            'items': [],
            'unlocked': False
        },
        'Rocket': {
            'items': [],
            'unlocked': False
        },
        'Flag': {
            'items': [],
            'unlocked': False
        },
    }

    for achievement in achievements_list:
        if achievement['unlocked']:
            achievements[
                achievement['iconName']
            ]['items'].append(achievement['displayName'])
            achievements[
                achievement['iconName']
            ]['unlocked'] = True

    html_template = loader.get_template('index.html')

    months, purchase_stats, total_spent, active = get_purchase_stats(profile)

    purchase_stats_count = [purchase_stats[key]['count'] for key in purchase_stats.keys()]
    purchase_stats_start_price = [int(purchase_stats[key]['start_price']) for key in purchase_stats.keys()]
    purchase_stats_end_price = [int(purchase_stats[key]['end_price']) for key in purchase_stats.keys()]

    try:
        delta_now = purchase_stats_start_price[-1] / purchase_stats_end_price[-1] * 100
    except:
        delta_now = purchase_stats_start_price[-1] * 100

    try:
        delta_before = purchase_stats_start_price[-2] / purchase_stats_end_price[-2] * 100
    except:
        delta_before = purchase_stats_start_price[-2] * 100

    if delta_now >= delta_before:
        try:
            start_end_price_difference = int(delta_now / delta_before)
        except:
            start_end_price_difference = 0
    else:
        try:
            start_end_price_difference = -1 * int(delta_now / delta_before)
        except:
            start_end_price_difference = 0

    for i in range(len(profile['items'])):
        profile['items'][i]['startPrice'] = f"{int(profile['items'][i]['startPrice']):,}".replace(',', ' ')
        if profile['items'][i]['auctionCurrentPrice']:
            profile['items'][i]['auctionCurrentPrice'] = f"{int(profile['items'][i]['auctionCurrentPrice']):,}".replace(',', ' ')

    # f"{value:,}".replace(',', ' ')
    context = {
        'segment': 'index',
        'profile': profile,
        'purchase_stats_count': purchase_stats_count,
        'months': months,
        'purchase_stats_count_max': max(purchase_stats_count),
        'purchase_stats_start_price': purchase_stats_start_price,
        'purchase_stats_end_price': purchase_stats_end_price,
        'start_end_price_difference': start_end_price_difference,
        'saved_last_month': int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]),
        'saved_last_month_display': f"{int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]):,}".replace(',', ' '),
        'spent_last_month': int(purchase_stats_end_price[-1]),
        'spent_last_month_display': f"{purchase_stats_end_price[-1]:,}".replace(',', ' '),
        'total_purchases': f"{len(profile['items']):,}".replace(',', ' '),
        'purchases_last_month': f"{purchase_stats_count[-1]:,}".replace(',', ' '),
        'total_spent': f"{total_spent:,}".replace(',', ' '),
        'purchases_active': active,
        'saved_price': int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]) - int(purchase_stats_start_price[-2] - purchase_stats_end_price[-2]),
        'saved_price_display': f"{abs(int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]) - int(purchase_stats_start_price[-2] - purchase_stats_end_price[-2])):,}".replace(',', ' '),
        'spent_price': f"{int(purchase_stats_start_price[-1] - purchase_stats_start_price[-2]):,}".replace(',', ' '),
        'purchases_display': profile['items'][:min(len(profile['items']), 5)],
        'achievements': achievements
    }

    return HttpResponse(html_template.render(context, request))


def tables(request, *args, **kwargs):

    page = request.GET.get('page', 1)


    user_id = kwargs.get('user_id')

    profile = get_profile(user_id)

    html_template = loader.get_template('tables.html')

    months, purchase_stats, total_spent, active = get_purchase_stats(profile)

    purchase_stats_count = [purchase_stats[key]['count'] for key in purchase_stats.keys()]
    purchase_stats_start_price = [int(purchase_stats[key]['start_price']) for key in purchase_stats.keys()]
    purchase_stats_end_price = [int(purchase_stats[key]['end_price']) for key in purchase_stats.keys()]

    try:
        delta_now = purchase_stats_start_price[-1] / purchase_stats_end_price[-1] * 100
    except:
        delta_now = purchase_stats_start_price[-1] * 100

    try:
        delta_before = purchase_stats_start_price[-2] / purchase_stats_end_price[-2] * 100
    except:
        delta_before = purchase_stats_start_price[-2] * 100

    if delta_now >= delta_before:
        try:
            start_end_price_difference = int(delta_now / delta_before)
        except:
            start_end_price_difference = 0
    else:
        try:
            start_end_price_difference = -1 * int(delta_now / delta_before)
        except:
            start_end_price_difference = 0

    paginator = Paginator(profile['items'], 8)
    try:
        purchases = paginator.page(page)
    except PageNotAnInteger:
        purchases = paginator.page(1)
    except EmptyPage:
        purchases = paginator.page(paginator.num_pages)

    for i in range(len(profile['items'])):
        profile['items'][i]['startPrice'] = f"{int(profile['items'][i]['startPrice']):,}".replace(',', ' ')
        if profile['items'][i]['auctionCurrentPrice']:
            profile['items'][i]['auctionCurrentPrice'] = f"{int(profile['items'][i]['auctionCurrentPrice']):,}".replace(',', ' ')

    context = {
        'segment': 'tables',
        'profile': profile,
        'purchase_stats_count': purchase_stats_count,
        'months': months,
        'purchase_stats_count_max': max(purchase_stats_count),
        'purchase_stats_start_price': purchase_stats_start_price,
        'purchase_stats_end_price': purchase_stats_end_price,
        'start_end_price_difference': start_end_price_difference,
        'saved_last_month': int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]),
        'spent_last_month': int(purchase_stats_end_price[-1]),
        'total_purchases': len(profile['items']),
        'purchases_last_month': purchase_stats_count[-1],
        'total_spent': total_spent,
        'purchases_active': active,
        'saved_price': int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]) - int(purchase_stats_start_price[-2] - purchase_stats_end_price[-2]),
        'spent_price': int(purchase_stats_start_price[-1] - purchase_stats_start_price[-2]),
        'purchases_display': purchases
    }

    return HttpResponse(html_template.render(context, request))


def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))


class PostJsonListView(View):
    def get(self, *args, **kwargs):
        customer_id = kwargs.get('customer_id')
        profile = get_profile(customer_id=customer_id)

        try:
            auctions = Auctions.objects.get(id=customer_id)
            if auctions.data == None or len(profile['items']) != len(auctions.data['data']):
                items = get_purchases_detailed(profile['items'])
                auctions.data = {'count': len(items), 'data': items}
                auctions.save()
            else:
                items = auctions.data['data']
        except Auctions.DoesNotExist:
            auctions = Auctions.objects.create(id=customer_id)
            items = get_purchases_detailed(profile['items'])
            auctions.data = {'count': len(items), 'data': items}
            auctions.save()

        return JsonResponse({'count': len(items), 'data': list(items)}, safe=False, json_dumps_params={'ensure_ascii': False})


def analysis(request, *args, **kwargs):

    user_id = kwargs.get('user_id')
    profile = get_profile(user_id)

    months, purchase_stats, total_spent, active = get_purchase_stats(profile)
    purchase_stats_count = [purchase_stats[key]['count'] for key in purchase_stats.keys()]

    try:
        auctions = Auctions.objects.get(id=user_id)
        items = auctions.data['data']
    except Exception as ex:
        print(ex)
        items = []

    html_template = loader.get_template('analysis.html')

    predicted_day = datetime.datetime(2021, 9, 24)
    now = datetime.datetime.today()
    difference_days = abs(predicted_day-now).days

    total_sum = 100500

    product_list = [
        {
            'id': 100,
            'imageId': 1934098657,
            'name': 'Салфетки бумажные, 100 шт., 24х24 см, МЯГКИЙ ЗНАК, белые, 100% целлюлоза',
            'currentValue': 10,
            'costPerUnit': 26,
            'score': 60,
            'skuId': 1208289
        }
    ]

    for i in range(len(product_list)):
        product_list[i]['totalCost'] = product_list[i]['currentValue'] * product_list[i]['costPerUnit']

    context = {
        'segment': 'analysis',
        'profile': profile,
        'date': predicted_day.strftime('%d.%m.%Y'),
        'difference_days': f"{difference_days:,}".replace(',', ' '),
        'total_sum': f"{total_sum:,}".replace(',', ' '),
        'total_purchases': f"{len(items):,}".replace(',', ' '),
        'purchases_last_month': f"{purchase_stats_count[-1]:,}".replace(',', ' '),
        'product_list': product_list
    }

    return HttpResponse(html_template.render(context, request))


class ProfilesJsonView(View):
    def get(self, *args, **kwargs):
        ids = get_profiles_list()
        return JsonResponse({'count': len(ids), 'data': ids}, safe=False, json_dumps_params={'ensure_ascii': False})