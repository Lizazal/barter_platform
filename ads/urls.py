from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.ad_list, name='ad_list'),  # список объявлений, поиск по объявлениям
    path('create/', views.create_ad, name='create_ad'),  # создание
    path('<int:ad_id>/edit/', views.edit_ad, name='edit_ad'),  # редактирование
    path('<int:ad_id>/delete/', views.delete_ad, name='delete_ad'),  # удаление
    path('proposals/create/', views.create_proposal, name='create_proposal'),  # создание предложения
    path('proposals/<int:proposal_id>/update/', views.update_proposal_status,
         name='update_proposal_status'),  # обновление предложения
    path('proposals/', views.proposal_list, name='proposal_list'),  # просмотр и фильтрация предложений
    path('proposals/<int:proposal_id>/cancel/', views.cancel_proposal, name='cancel_proposal'),  # отмена предложения
]
