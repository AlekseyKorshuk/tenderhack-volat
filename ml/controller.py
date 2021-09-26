import json
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import dateutil.relativedelta as relativedelta



class IdToCategory:
    _dict = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(IdToCategory, cls).__new__(cls)
        return cls.instance

    def convert(self, id_, pd_categories):
        if self._dict is None:
            self._load_dict(pd_categories)
        if id_ in self._dict.keys():
            return self._dict[id_]
        return None

    def _load_dict(self, pd_categories):
        self._dict = {}
        for index, row in pd_categories.iterrows():
            item_id = row['ID СТЕ']
            item_category = row['Категория']
            self._dict[item_id] = item_category


class Preloaded:
    users_distance = None
    id_to_index = None
    categories = None
    pd_user_features = None
    id_buy_share = None
    index_to_id = None

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Preloaded, cls).__new__(cls)
        return cls.instance

    def load_everything(self, pd_data, pd_cat_data):
        if (self.users_distance is not None and self.id_to_index is not None and
                self.categories is not None and self.pd_user_features is not None and
                self.id_buy_share is not None):
            return

        IdToCategory()._load_dict(pd_cat_data)
        df1 = pd_data.drop(['КПП поставщика'], axis=1)
        df1 = df1[df1.isna().any(axis=1)]
        clean_data = pd_data.drop(df1.isna().any(axis=1).index)

        id_item_sum = {}
        for index, data in clean_data.loc[:, ['ИНН заказчика', 'СТЕ', 'Дата публикации КС на ПП']].iterrows():
            ctes_raw = data['СТЕ']
            publication_date_raw = data['Дата публикации КС на ПП']
            buyer_inn = data['ИНН заказчика']

            ctes = json.loads(ctes_raw)
            publication_date = publication_date_raw.date()
            if buyer_inn not in id_item_sum.keys():
                id_item_sum[buyer_inn] = {}
            for item in ctes:
                item_id = item['Id']
                item_quantity = item['Amount']
                if item_id is None:
                    continue
                if item_id not in id_item_sum[buyer_inn].keys():
                    id_item_sum[buyer_inn][item_id] = 0
                id_item_sum[buyer_inn][item_id] += item_quantity

        self.id_buy_share = {}
        for user_id, buys in id_item_sum.items():
            total_amount = 0
            buy_share = {}
            for item_id, amount in buys.items():
                total_amount += amount
            for item_id, amount in buys.items():
                buy_share[item_id] = amount / total_amount
            self.id_buy_share[user_id] = buy_share

        id_category_share = {}
        for id_, buy_share in self.id_buy_share.items():
            category_share = {}
            for item_id, item_share in buy_share.items():
                item_category = IdToCategory().convert(item_id, pd_cat_data)
                if item_category is None:
                    print("None category for", item_id)
                if item_category not in category_share.keys():
                    category_share[item_category] = 0
                category_share[item_category] += item_share
            id_category_share[id_] = category_share

        self.categories = []
        for buy_share in self.id_buy_share.values():
            for item_id in buy_share.keys():
                item_category = IdToCategory().convert(item_id, pd_cat_data)
                if item_category not in self.categories:
                    self.categories.append(item_category)

        user_features = {}
        self.id_to_index = {}
        self.index_to_id = {}
        i = 0
        for id_, category_share in id_category_share.items():
            features = []
            for category in self.categories:
                if category in category_share.keys():
                    features.append(category_share[category])
                else:
                    features.append(0)
            user_features[id_] = features
            self.id_to_index[id_] = i
            self.index_to_id[i] = id_
            i += 1

        self.pd_user_features = pd.DataFrame.from_dict(user_features, orient='index', columns=self.categories)

        self.users_distance = cosine_similarity(self.pd_user_features)


def items_user_did_not_try(user_inn, contracts, pd_cat_data, recoms_num=4, similar_business_threashold=0.55):
    neighbors_raw = Preloaded().users_distance[Preloaded().id_to_index[user_inn]]
    neighbors = {}
    for index, similarity in enumerate(neighbors_raw):
        neighbors[Preloaded().index_to_id[index]] = similarity
    del neighbors[user_inn]
    neighbors = sorted(neighbors.items(), key=lambda item: item[1], reverse=True)

    similar_neighbors = {}
    for key, value in neighbors:
        if value < similar_business_threashold:
            break
        similar_neighbors[key] = value

    similar_group_features = np.zeros(len(Preloaded().categories))
    for key in similar_neighbors.keys():
        similar_group_features += Preloaded().pd_user_features.loc[key]
    similar_group_features /= len(similar_neighbors)

    not_tried_features = pd.Series(similar_group_features).where(Preloaded().pd_user_features.loc[user_inn] == 0)
    not_tried_features = not_tried_features.where(similar_group_features != 0)
    not_tried_category = not_tried_features.nlargest(4)

    category_items_to_recommend = {}
    for id_ in similar_neighbors.keys():
        for item_id in Preloaded().id_buy_share[id_].keys():
            item_category = IdToCategory().convert(item_id, pd_cat_data)
            if item_category in not_tried_category.keys():
                if item_category not in category_items_to_recommend.keys():
                    category_items_to_recommend[item_category] = set()
                category_items_to_recommend[item_category].add(item_id)

    output = []
    ind_to_cat = {}
    i = 0
    items_num = 0
    for cat, items in category_items_to_recommend.items():
        ind_to_cat[i] = cat
        i += 1
        items_num += len(items)

    taken = 0
    i = 0
    while taken < recoms_num and items_num > 0:
        if len(category_items_to_recommend[ind_to_cat[i]]) > 0:
            taken += 1
            items_num -= 1
            output.append(category_items_to_recommend[ind_to_cat[i]].pop())
        i = (i + 1) % 4

    return output


def periods_info(user_inn, pd_data):
    df1 = pd_data.drop(['КПП поставщика'], axis=1)
    df1 = df1[df1.isna().any(axis=1)]
    clean_data = pd_data.drop(df1.isna().any(axis=1).index)

    user_orders = clean_data.loc[clean_data['ИНН заказчика'] == user_inn]

    id_buy_dates = {}
    for index, data in user_orders.loc[:, ['СТЕ', 'Дата публикации КС на ПП']].iterrows():
        ctes_raw = data['СТЕ']
        publication_date_raw = data['Дата публикации КС на ПП']

        ctes = json.loads(ctes_raw)
        publication_date = publication_date_raw.date()
        for item in ctes:
            item_id = item['Id']
            item_quantity = item['Quantity']
            if item_id is None:
                continue
            item_category = IdToCategory().convert(item_id, pd_data)
            if item_category not in id_buy_dates.keys():
                id_buy_dates[item_category] = []
            id_buy_dates[item_category].append((publication_date, item_quantity, item_id))

    for cat, notes in id_buy_dates.items():
        id_buy_dates[cat] = sorted(notes)

    period_info = {}
    threashold_x_period = 2
    for cat, notes in id_buy_dates.items():
        last_buy = notes[len(notes) - 1][0]
        last_item = notes[len(notes) - 1][2]
        prev_day = None
        periods_sum = 0
        periods_num = 0
        season_quantity = None
        current_quantity = 0
        prev_season_period = None
        demiseason_len = None

        is_season = True
        for note in notes:
            cur_day = note[0]
            quantity = note[1]
            if prev_day is not None and cur_day != prev_day:
                period = (cur_day - prev_day).days
                if periods_num > 0:
                    cur_avg_period = float(periods_sum) / periods_num
                    if period > threashold_x_period * cur_avg_period:
                        # season ended up
                        demiseason_len = period
                        prev_season_period = cur_avg_period
                        season_quantity = current_quantity
                        current_quantity = 0
                        periods_sum = 0
                        periods_num = 0
                        is_season = False
                if is_season:
                    periods_sum += period
                    periods_num += 1
                is_season = True
            current_quantity += quantity
            prev_day = cur_day

        cat_period = None
        next_buy = None
        is_enough = False
        if season_quantity:
            is_enough = current_quantity >= season_quantity
        if prev_season_period:
            cat_period = prev_season_period
        if periods_num >= 2:
            cat_period = periods_sum / periods_num
        if cat_period:
            if demiseason_len and (datetime.date.today() - last_buy).days > threashold_x_period * cat_period:
                next_buy = last_buy + relativedelta.relativedelta(day=int(demiseason_len))
            else:
                next_buy = last_buy + relativedelta.relativedelta(day=int(cat_period))
            period_info[cat] = (cat_period, demiseason_len, season_quantity, current_quantity,
                                last_buy, last_item, is_enough, next_buy)

    return period_info


import numpy as np
import sklearn.linear_model as linearRegr

def sorted_data(data):
  data_copy = data
  for key in data:
    array = data[key]
    data_copy[key] = sorted(array, key = lambda tup: datetime.datetime.strptime(tup[0], "%d.%m.%Y"))
  return data_copy

def predict_next(x_space, y_space):
  regr = linearRegr.LinearRegression()
  lin_model = regr.fit(np.array(x_space).reshape(-1, 1), y_space)
  return lin_model.predict(np.array([len(x_space)]).reshape(-1, 1))

def maximum_tuple_in_dict(d):
  to_be_sorted = []
  for key in d:
    if d[key][1] < 50:
      to_be_sorted.append((key, d[key][1]))
  to_be_sorted = sorted(to_be_sorted, key = lambda tup: tup[1], reverse = True)
  output = []
  for i in range(len(to_be_sorted) if len(to_be_sorted) < 5 else 5):
    dic = {}
    key = to_be_sorted[i][0]
    dic["name"] = key
    dic["data"] = d[key][0]
    dic["percentage"] = d[key][1]
    output.append(dic)
  return output

def predict_categories_trend(data, categories):
  DAYS_IN_MONTH = 30
  MONTHS_IN_PAST = 11
  DAYS_IN_PAST = MONTHS_IN_PAST * DAYS_IN_MONTH
  initial_date = datetime.datetime.now().date() - datetime.timedelta(DAYS_IN_PAST)
  data = sorted_data(data)

  categories_to_spaces = {}
  for key in data:
    if not key in categories:
      continue
    x_space = []
    y_space = []
    for tuple in data[key]:
      current = datetime.datetime.strptime(tuple[0], "%d.%m.%Y").date()
      if (datetime.datetime.now().date() - current).days < DAYS_IN_PAST:
        x_space.append((current - initial_date).days)
        y_space.append(tuple[1])
    if len(x_space) < 3:
      continue
    approx = np.polyfit(x_space, y_space, 4)
    p = np.poly1d(approx)
    # fig, ax = plt.subplots()
    # ax.plot(x_space, p(x_space))
    # ax.plot(x_space, y_space)
    months = []
    for i in range(11):
      months.append(p(i*DAYS_IN_MONTH))
    months.append(predict_next(x_space, p(x_space))[0])
    percent = (months[len(months)-1]-months[len(months)-2])/(months[len(months)-2])*100
    categories_to_spaces[key] = (months, percent)
  return maximum_tuple_in_dict(categories_to_spaces)


