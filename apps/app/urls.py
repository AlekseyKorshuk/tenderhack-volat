# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.app import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('profile/<int:user_id>', views.profile, name='home'),
    path('tables/<int:user_id>', views.tables, name='tables'),
    path('analysis/<int:user_id>', views.analysis, name='analysis'),
    path('team/<int:user_id>', views.team, name='team'),
    path('auctions/<int:customer_id>', views.PostJsonListView.as_view(), name='users-json-view'),
    path('profiles', views.ProfilesJsonView.as_view(), name='profiles'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
