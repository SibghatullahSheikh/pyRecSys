from recsys.datasets import load_movielens_100k as load_data
from recsys.user_based import UserBasedRecommender as Recommender

data = load_data()
r = Recommender(data)
print r.recommend_items('1')
