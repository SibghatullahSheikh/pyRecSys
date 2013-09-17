from recsys import load_sample_movies as load_data
from recsys import UserBasedRecommender as Recommender

data = load_data()
r = Recommender(data)
print r.recommend_items('Toby')
