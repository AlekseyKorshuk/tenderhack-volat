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
from numpy import median



def index(request):
    ids = get_profiles_list()
    return redirect(f'/profile/{random.choice(ids)}')
    # return HttpResponse(html_template.render(context, request))


def team(request, *args, **kwargs):
    user_id = kwargs.get('user_id')
    if user_id is None:
        user_id = random.choice(get_profiles_list())
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
    if user_id is None:
        user_id = random.choice(get_profiles_list())
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
    if user_id is None:
        user_id = random.choice(get_profiles_list())

    profile, is_supplier, result_user_id = get_profile(user_id)
    inn = getINNByProfile(profile)

    if not is_supplier:
        purchases_list = predictPurchases(inn)

        months, purchase_stats, total_spent, active = get_purchase_stats(profile)

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
            achievements[
                achievement['iconName']
            ]['items'].append(achievement['displayName'])
            if achievement['unlocked']:
                achievements[
                    achievement['iconName']
                ]['unlocked'] = True

        html_template = loader.get_template('index.html')
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
                profile['items'][i][
                    'auctionCurrentPrice'] = f"{int(profile['items'][i]['auctionCurrentPrice']):,}".replace(',', ' ')


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
            'saved_last_month_display': f"{int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]):,}".replace(
                ',', ' '),
            'spent_last_month': int(purchase_stats_end_price[-1]),
            'spent_last_month_display': f"{purchase_stats_end_price[-1]:,}".replace(',', ' '),
            'total_purchases': f"{len(profile['items']):,}".replace(',', ' '),
            'purchases_last_month': f"{purchase_stats_count[-1]:,}".replace(',', ' '),
            'total_spent': f"{total_spent:,}".replace(',', ' '),
            'purchases_active': active,
            'saved_price': int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]) - int(
                purchase_stats_start_price[-2] - purchase_stats_end_price[-2]),
            'saved_price_display': f"{abs(int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]) - int(purchase_stats_start_price[-2] - purchase_stats_end_price[-2])):,}".replace(
                ',', ' '),
            'spent_price': f"{int(purchase_stats_start_price[-1] - purchase_stats_start_price[-2]):,}".replace(',',
                                                                                                               ' '),
            'purchases_display': profile['items'][:min(len(profile['items']), 5)],
            'achievements': achievements
        }
    else:
        purchases_list = predictTrand(inn)
        months, purchase_stats, total_spent, active = get_contract_stats(profile)

        html_template = loader.get_template('supplier.html')

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
            achievements[
                achievement['iconName']
            ]['items'].append(achievement['displayName'])
            if achievement['unlocked']:

                achievements[
                    achievement['iconName']
                ]['unlocked'] = True

        purchase_stats_count = [purchase_stats[key]['count'] for key in purchase_stats.keys()]
        purchase_stats_start_price = [int(purchase_stats[key]['price']) for key in purchase_stats.keys()]

        for i in range(len(profile['items'])):
            profile['items'][i]['rubSum'] = f"{int(profile['items'][i]['rubSum']):,}".replace(',', ' ')


        context = {
            'segment': 'index',
            'profile': profile,
            'purchase_stats_count': purchase_stats_count,
            'months': months,
            'purchase_stats_count_max': max(purchase_stats_count),
            'purchase_stats_start_price': purchase_stats_start_price,
            'purchases_active': active,
            'total_purchases': f"{len(profile['items']):,}".replace(',', ' '),
            'purchases_last_month': f"{purchase_stats_count[-1]:,}".replace(',', ' '),
            'total_spent': f"{total_spent:,}".replace(',', ' '),
            'spent_price': f"{int(purchase_stats_start_price[-1] - purchase_stats_start_price[-2]):,}".replace(',',
                                                                                                               ' '),
            'spent_last_month_display': f"{purchase_stats_start_price[-1]:,}".replace(',', ' '),
            'purchases_display': profile['items'][:min(len(profile['items']), 5)],
            'achievements': achievements
        }

    notifications = getNotifications(purchases_list, is_supplier)
    context.update(
        {
            'notifications': notifications
        }
    )

    return HttpResponse(html_template.render(context, request))


def tables(request, *args, **kwargs):

    page = request.GET.get('page', 1)
    user_id = kwargs.get('user_id')
    if user_id is None:
        user_id = random.choice(get_profiles_list())

    profile, is_supplier, result_user_id = get_profile(user_id)
    inn = getINNByProfile(profile)

    if not is_supplier:
        html_template = loader.get_template('tables.html')
        months, purchase_stats, total_spent, active = get_purchase_stats(profile)
        purchase_stats_count = [purchase_stats[key]['count'] for key in purchase_stats.keys()]
        for i in range(len(profile['items'])):
            profile['items'][i]['startPrice'] = f"{int(profile['items'][i]['startPrice']):,}".replace(',', ' ')
            if profile['items'][i]['auctionCurrentPrice']:
                profile['items'][i][
                    'auctionCurrentPrice'] = f"{int(profile['items'][i]['auctionCurrentPrice']):,}".replace(',', ' ')

        purchases_list = predictPurchases(inn)
    else:
        html_template = loader.get_template('tables-supplier.html')
        months, purchase_stats, total_spent, active = get_contract_stats(profile)
        purchase_stats_count = [purchase_stats[key]['count'] for key in purchase_stats.keys()]
        for i in range(len(profile['items'])):
            profile['items'][i]['rubSum'] = f"{int(profile['items'][i]['rubSum']):,}".replace(',', ' ')
        purchases_list = predictTrand(inn)

    paginator = Paginator(profile['items'], 8)

    try:
        purchases = paginator.page(page)
    except PageNotAnInteger:
        purchases = paginator.page(1)
    except EmptyPage:
        purchases = paginator.page(paginator.num_pages)

    context = {
        'segment': 'tables',
        'profile': profile,
        'purchases_display': purchases,
        'purchases_last_month': f"{purchase_stats_count[-1]:,}".replace(',', ' '),
    }

    notifications = getNotifications(purchases_list, is_supplier)
    context.update(
        {
            'notifications': notifications
        }
    )

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
        if customer_id is None:
            customer_id = random.choice(get_profiles_list())
        profile = get_profile(customer_id=customer_id)

        try:
            auctions = Auctions.objects.get(id=customer_id)
            if auctions.data == None or len(profile['items']) != len(auctions.data['data']):
                items = get_purchases_detailed(profile['items'], auctions.data)
                auctions.data = {'count': len(items), 'data': items}
                auctions.save()
            else:
                items = auctions.data['data']
        except Auctions.DoesNotExist:
            auctions = Auctions.objects.create(id=customer_id)
            items = get_purchases_detailed(profile['items'], None)
            auctions.data = {'count': len(items), 'data': items}
            auctions.save()

        return JsonResponse({'count': len(items), 'data': list(items)}, safe=False, json_dumps_params={'ensure_ascii': False})


def analysis(request, *args, **kwargs):

    user_id = kwargs.get('user_id')
    if user_id is None:
        user_id = random.choice(get_profiles_list())

    profile, is_supplier, result_user_id = get_profile(user_id)
    inn = getINNByProfile(profile)

    if not is_supplier:
        html_template = loader.get_template('analysis.html')
        purchases_list = predictPurchases(inn)


        # for i in range(len(purchases_list)):
        #     product_id = purchases_list[i]['id']
        #     print(product_id)
        #     prices = []
        #     data = auctions.loc[auctions['ИНН заказчика'] == str(inn)]
        #     for index, row in data.iterrows():
        #         for item in json.loads(row['СТЕ']):
        #             if item['Id'] == product_id:
        #                 prices.append(
        #                     float(item["Amount"] / item["Quantity"])
        #                 )
        #     print(prices)
        #
        #     purchases_list[i]['deltaPrice'] = float(median(prices)) - float(purchases_list[i]['minPrice'])

        context = {
            'segment': 'analysis',
            'profile': profile,
            'products_suggest': predictSuggestions(inn), #predictSuggestions(inn)
            'purchases_list': purchases_list,
        }

    else:
        html_template = loader.get_template('analysis-supplier.html')
        purchases_list = predictTrand(inn)
        context = {
            'segment': 'analysis',
            'profile': profile,
            'trend_prediction': purchases_list
        }

    notifications = getNotifications(purchases_list, is_supplier)

    context.update(getCategoriesStats(user_id, is_supplier, inn))

    context.update(
        {
            'notifications': notifications
        }
    )

    return HttpResponse(html_template.render(context, request))


class ProfilesJsonView(View):
    def get(self, *args, **kwargs):
        ids = get_profiles_list()
        return JsonResponse({'count': len(ids), 'data': ids}, safe=False, json_dumps_params={'ensure_ascii': False})


def parseData(request, *args, **kwargs):
    import threading

    t = threading.Thread(target=start, args=(), kwargs={})
    t.setDaemon(True)
    t.start()
    return HttpResponse("Parsing")