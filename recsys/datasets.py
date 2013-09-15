from os.path import join, dirname, abspath
from collections import defaultdict


DATA_PATH = join(abspath(dirname(__file__)), 'data')

MOVIELENS100K_DATA = join(DATA_PATH, 'movielens100k.data')
MOVIELENS100K_ITEMS = join(DATA_PATH, 'movielens100k.item')

SAMPLE_MOVIES = join(DATA_PATH, 'sample_movies.csv')

ITEM_BASED_MODEL_PATH = join(DATA_PATH, '%s_item-based.model')


class RatingsData:
    def __init__(self, name):
        # Mandatory ratings data
        # {user_id: {item_id: rating, item_id:rating, ...}, ...}
        self.user_ratings = defaultdict(dict)
        self.item_ids = set()
        
        # Optional mapping between IDs and Names
        self.id_username = {}
        self.username_id = {}
        
        self.id_itemname = {}
        self.itemname_id = {}
        
        # Path to the generated Item Based Model Path
        self.item_based_model_path = ITEM_BASED_MODEL_PATH % name
    
    def add_rating(self, user_id, item_id, rating):
        item_id = int(item_id)
        self.user_ratings[int(user_id)][item_id] = float(rating)
        self.item_ids.add(item_id)
    
    def add_user_name(self, user_id, name):
        user_id = int(user_id)
        self.id_username[user_id] = name
        self.username_id[name] = user_id
    
    def add_item_name(self, item_id, name):
        item_id = int(item_id)
        self.id_itemname[item_id] = name
        self.itemname_id[name] = item_id
    
    def user_name(self, user_id):
        return self.id_username.get(int(user_id), str(user_id))
    
    def item_name(self, item_id):
        return self.id_itemname.get(int(item_id), str(item_id))
    
    def user_id(self, user_name):
        if user_name not in self.username_id: return int(user_name)
        return self.username_id[user_name]
    
    def item_id(self, item_name):
        if item_name not in self.itemname_id: return int(item_name)
        return self.itemname_id[item_name]
    
    def get_usernames(self):
        if not self.username_id:
            for user_id in self.user_ratings.keys():
                self.username_id[self.user_name(user_id)] = user_id
        return self.username_id.keys()
    
    def get_itemnames(self):
        if not self.itemname_id:
            for item_id in self.item_ids:
                self.itemname_id[self.item_name(item_id)] = item_id
        return self.itemname_id.keys()
    
    def __str__(self):
        s = []
        for user_id, ratings in self.user_ratings.iteritems():
            items = []
            for item_id, rating in ratings.iteritems():
                items.append('("%s", %.1f)'%(self.item_name(item_id), rating))
            s.append("%s: [%s]" % (self.user_name(user_id), ', '.join(items)))
        return '\n'.join(s)


def load_movielens_100k():
    data = RatingsData('movielens100k')
    
    for line in open(MOVIELENS100K_DATA):
        fields = line.split()
        if fields < 3: continue
        data.add_rating(fields[0], fields[1], fields[2])
    
    for line in open(MOVIELENS100K_ITEMS):
        fields = line.split('|')
        if fields < 2: continue
        data.add_item_name(fields[0], fields[1])
    
    return data


class NameId:
    def __init__(self):
        self.id = 0
        self.name_id = {}
    
    def get_id(self, name):
        if name not in self.name_id:
            self.name_id[name] = self.id
            self.id += 1
        
        return self.name_id[name]


def load_sample_movies():
    data = RatingsData('sample')
    user_names, item_names = NameId(), NameId()
    
    for line in open(SAMPLE_MOVIES):
        fields = line.split(';')
        if fields < 3: continue
        
        user_id = user_names.get_id(fields[0])
        data.add_user_name(user_id, fields[0])
        
        item_id = item_names.get_id(fields[1])
        data.add_item_name(item_id, fields[1])
        
        data.add_rating(user_id, item_id, fields[2])
    
    return data
