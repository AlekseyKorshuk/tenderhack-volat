# Tender Hack | VOLAT

# Веб-сайт-личный кабинет для Заказчиков и Поставщиков

## Использование:
1. `python manage.py runserver`
2. Зайти на localhost:8000

## Рекомендательные модели:
- /ml/controller.py/items_user_did_not_try - Новые товары, которые интересны схожим по распределению средств по категориям заказчикам.
- /ml/controller.py/periods_info - Даты и объемы регулярной покупки конкретного товара с учетом динамически рассчитываемой сезонности на основании исторических данных пользователя.
- /ml/controller.py/predict_categories_trend - Подготовка к ожидаемому росту спроса на категории товаров, над которыми работает поставщик, с указанием величины спроса в виде количества товара и ожидаемой даты

## Стек:

### Общее
- Python 3.7
- Рекомендательные алгоритмы
- pandas
- numpy
- sklearn
### Интерфейс (web-сайт)
- Django
- JQuery
- Bootstrap
- HTML
- CSS
- JavaScript

## Details:
https://docs.google.com/document/d/1C1mAvBU0f8J1H5kfrlHvvDJDiUPy_-SfXcNTp_4i4FM/edit?usp=sharing
