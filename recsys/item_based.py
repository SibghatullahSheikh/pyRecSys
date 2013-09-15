"""
Item-Based Collaborative Filtering Recommendation Algorithms
http://www.ra.ethz.ch/cdstore/www10/papers/pdf/p519.pdf

In a typical E-Commerce scenario, we usually have a set of item that is static
compared to the number of users that changes most often. The static nature of
items leads us to the idea of precomputing the item similarities. One possible
way of precomputing the item similarities is to compute all-to-all similarity
and then performing a quick table look-up to retrieve the required similarity
values. This method, although saves time, requires an O(n2) space for n items.
The fact that we only need a small fraction of similar items to compute
predictions leads us to an alternate model-based scheme. In this scheme, we
retain only a small number of similar items. For each item j we compute the k
most similar items, where k  n and record these item numbers and their
similarities with j. We term k as the model size. Based on this model building
step, our prediction generation algorithm works as follows. For generating
predictions for a user u on item i, our algorithm first retrieves the
precomputed k most similar items corresponding to the target item i. Then it
looks how many of those k items were purchased by the user u, based on this
intersection then the prediction is computed using basic item-based
collaborative filtering algorithm.
"""
from os.path import exists
from collections import defaultdict
from json import loads, dumps

from metrics import DEFAULT_METRIC
from recommender import Recommender, WeightedRanking, subset


class ItemBasedRecommender(Recommender):
    def __init__(self, data, metric=DEFAULT_METRIC, model_size=50):
        self.items = defaultdict(dict)
        for user, ratings in data.user_ratings.iteritems():
            for item, rating in ratings.iteritems():
                self.items[item][user] = rating
        Recommender.__init__(self, self.items, metric)
        self.data = data
        self.model_size = model_size
        
        self.item_similars = {}
        if exists(data.item_based_model_path):
            self.load_model(data.item_based_model_path)
        else:
            self.learn_model(data.item_based_model_path)
    
    def learn_model(self, f):
        print "Learning Item Based Model: %s" % f
        c, tot = 0, len(self.items.keys())
        with open(f, 'w') as model:
            for item_id in self.items.keys():
                c += 1
                if c%100 == 0: print "%.0f%%" % (float(c)/float(tot)*100.)
                s = self.similars(item_id, self.model_size)
                self.item_similars[item_id] = s
                model.write(dumps([item_id] + s) + '\n')
    
    def load_model(self, f):
        print "Loading Item Base Model: %s" % f
        with open(f) as model:
            for line in model:
                data = loads(line)
                self.item_similars[data[0]] = data[1:]
    
    def item_similarity(self, a, b):
        """
        How similar are the items a and b?
        """
        a_id, b_id = map(self.data.item_id, (a, b))
        return self.score(a_id, b_id)
    
    def similar_items(self, itemname, limit=10):
        """
        Return a list of items similar to itemname
        """
        item_id = self.data.item_id(itemname)
        return [(score, self.data.item_name(iid))
                for score, iid in self.similars(item_id, limit)]
    
    def recommend_users(self, itemname, limit=10):
        """
        Return a list of users that have not rated this item that could like
        it, based on the ratings of similar users.
        """
        item_id = self.data.item_id(itemname)
        return [(score, self.data.user_name(user_id))
                for score, user_id in self.recommend(item_id, limit)]
    
    def recommend_items(self, username, limit=10):
        """
        Recommend to username a list of items he did not rate and that he could
        like, based on the ratings he gave to similar items.
        """
        user_id = self.data.user_id(username)
        user_ratings = self.data.user_ratings[user_id]
        
        wr = WeightedRanking()
        
        # items rated by this user
        for item_a, rating in user_ratings.iteritems():
            
            # items similar to this one
            for score, item_b in self.item_similars[item_a]:
                if item_b in user_ratings: continue
                wr.add_ranking(item_b, rating, score)
        
        items = subset(wr.get_weighted_rankings(), limit)
        return [(score, self.data.item_name(iid)) for score, iid in items]
