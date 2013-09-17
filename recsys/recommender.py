from collections import defaultdict


class WeightedRanking:
    def __init__(self):
        self.ranking_sum = defaultdict(float)
        self.weigth_sum  = defaultdict(float)
    
    def add_ranking(self, f, ranking, weight):
        self.ranking_sum[f] += ranking * weight
        self.weigth_sum[f] += weight
    
    def get_weighted_rankings(self):
        rankings = [(ranking / self.weigth_sum[f], f)
                    for f, ranking in self.ranking_sum.items()]
        rankings.sort(reverse=True)
        return rankings


def subset(results, limit):
    if limit is None: limit = len(results)
    return results[0:limit]


class Recommender:
    """
    table = {
        "key 1": {"feature 1": rating_1, "feature 2": rating_2, ...},
        "key 2": {"feature 1": rating_1, "feature 2": rating_2, ...},
        ...
    }
    """
    def __init__(self, table, metric):
        self.table = table
        self.metric = metric
    
    def score(self, a, b):
        # Get the common subset of features
        features = set(self.table[a].keys()) & set(self.table[b].keys())
        if len(features) == 0: return 0
        
        return self.metric([self.table[a][feature] for feature in features],
                           [self.table[b][feature] for feature in features])
    
    def similars(self, a, limit=10):
        scores = [(self.score(a, b), b) for b in self.table.keys() if b != a]
        scores = [s for s in scores if s[0] > 0]
        scores.sort(reverse=True)
        return subset(scores, limit)
    
    def recommend(self, a, limit=10):
        """
        calculate ratings for unrated features of a key as average of all the
        other ratings for that feature weighted by the similarity of the other
        key
        """
        wr = WeightedRanking()
        for b in self.table.keys():
            # Only different keys
            if b == a: continue
            
            key_sim = self.score(a, b)
            if key_sim <= 0: continue
            
            for f in self.table[b]:
                if f in self.table[a]: continue
                wr.add_ranking(f, self.table[b][f], key_sim)
        
        return subset(wr.get_weighted_rankings(), limit)

