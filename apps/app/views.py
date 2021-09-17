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


def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('index.html')
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
        'spent_last_month': int(purchase_stats_end_price[-1]),
        'total_purchases': len(profile['items']),
        'purchases_last_month': purchase_stats_count[-1],
        'total_spent': total_spent,
        'purchases_active': active,
        'saved_price': int(purchase_stats_start_price[-1] - purchase_stats_end_price[-1]) - int(purchase_stats_start_price[-2] - purchase_stats_end_price[-2]),
        'spent_price': int(purchase_stats_start_price[-1] - purchase_stats_start_price[-2]),
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

    context = {
        'segment': 'analysis',
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
        'purchases_display': profile['items'][:min(len(profile['items']), 5)],
        'achievements': achievements
    }

    return HttpResponse(html_template.render(context, request))