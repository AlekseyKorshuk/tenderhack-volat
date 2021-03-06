# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.app import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    path('parse', views.parseData, name='parseData'),
    path('profile/<int:user_id>', views.profile, name='home'),
    path('profile', views.profile, name='home'),
    path('tables/<int:user_id>', views.tables, name='tables'),
    path('tables', views.tables, name='tables'),
    path('analysis/<int:user_id>', views.analysis, name='analysis'),
    path('analysis', views.analysis, name='analysis'),
    path('team/<int:user_id>', views.team, name='team'),
    path('team', views.team, name='team'),
    path('how/<int:user_id>', views.how, name='how'),
    path('inn/<str:inn>', views.inn, name='inn'),
    path('how', views.how, name='how'),
    path('auctions/<int:customer_id>', views.PostJsonListView.as_view(), name='users-json-view'),
    path('profiles', views.ProfilesJsonView.as_view(), name='profiles'),
    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

]
