import numpy as np
import pandas as pd

def prefilter_items(data, item_features):
    # Уберем самые популярные товары (их и так купят)
    popularity = data.groupby('item_id')['user_id'].nunique().reset_index() / data['user_id'].nunique()
    popularity.rename(columns={'user_id': 'share_unique_users'}, inplace=True)

    top_popular = popularity[popularity['share_unique_users'] > 0.5].item_id.tolist()
    data = data[~data['item_id'].isin(top_popular)]

    # Уберем самые НЕ популярные товары (их и так НЕ купят)
    top_notpopular = popularity[popularity['share_unique_users'] < 0.01].item_id.tolist()
    data = data[~data['item_id'].isin(top_notpopular)]

    # Уберем товары, которые не продавались за последние 12 месяцев
    not_sales_more_12_month = data[data['week_no'] > 12].item_id.to_list()
    data = data[~data['item_id'].isin(not_sales_more_12_month)]

    # Уберем не интересные для рекоммендаций категории (department)
    # Под "не интересные для рекомендаций" я подразумеваю те категории, где менее 10 позиций
    # Создаю список категорий(department), где меньше 10 позиций
    my_dict = dict(item_features['department'].value_counts())
    departments_less_10_positions = []
    for k, v in my_dict.items():
        if v < 10:
            departments_less_10_positions.append(k)
    not_interesting_department = item_features[ item_features['department'].isin(
        departments_less_10_positions)].item_id.to_list()
    data = data[~data['item_id'].isin(not_interesting_department)]

    # Уберем слишком дешевые товары (на них не заработаем). 1 покупка из рассылок стоит 60 руб.
    # Под "слишком дешевые" подразумевааем менее 1
    data['price'] = data['sales_value'] / (np.maximum(data['quantity'], 1))

    too_cheap = data[data['price'] < 1].item_id.to_list()
    data = data[~data['item_id'].isin(too_cheap)]

    # Уберем слишком дорогие товарыs
    too_expensive = data[data['price'] > 100].item_id.to_list()
    data = data[~data['item_id'].isin(too_cheap)]

    return data
