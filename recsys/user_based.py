from metrics import DEFAULT_METRIC
from recommender import Recommender


class UserBasedRecommender(Recommender):
    def __init__(self, data, metric=DEFAULT_METRIC):
        Recommender.__init__(self, data.user_ratings, metric)
        self.data = data
    
    def user_similarity(self, a, b):
        """
        How similar are the users a and b?
        """
        a_id, b_id = map(self.data.user_id, (a, b))
        return self.score(a_id, b_id)
    
    def similar_users(self, username, limit=10):
        """
        Return a list of users similar to username
        """
        user_id = self.data.user_id(username)
        return [(score, self.data.user_name(uid))
                for score, uid in self.similars(user_id, limit)]
    
    def recommend_items(self, username, limit=10):
        """
        Recommend to username a list of items he did not rate and that he could
        like, based on the ratings of users similar to him.
        """
        user_id = self.data.user_id(username)
        return [(score, self.data.item_name(item_id))
                for score, item_id in self.recommend(user_id, limit)]
