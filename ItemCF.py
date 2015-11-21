import math
import random

'''
train, test: a dict, from user to item
item: a set, a list of item
'''
def ReadData(name, splitStr = '\t'):
    try:
        fp = open(name)
    except:
        print "Open file error"
        exit()

    data = dict()
    for line in fp:
        t = line.split(splitStr)
        user = t[0]
        item = t[1]
        rating = t[2]
        if user not in data:
            data[user] = dict()
        data[user][item] = rating

    return data

def SplitData(data, M, k, seed):
    test = dict()
    train = dict()
    random.seed(seed)
    for user, items in data.items():
        for item, rating in items.items():
            if random.randint(0, M) == k:
                if user not in test:
                     test[user] = dict()
                test[user][item] = rating
            else:
                if user not in train:
                    train[user] = set()
                train[user].add(item)

    return train, test

def ItemSimilarity(train):
    #calculate co-rated users between items
    C = dict()
    N = dict()
    for u, items in train.items():
        for i in items:
            if i not in N:
                N[i] = 0
            N[i] += 1
            for j in items:
                if i == j:
                    continue
                if i not in C:
                    C[i] = dict()
                if j not in C[i]:
                    C[i][j] = 0
                C[i][j] += 1
    #calculate final similariuty matrix W
    W = dict()
    for i, related_items in C.items():
        for j, cij in related_items.items():
            W[i][j] = cij / math.sqrt(N[i] * N[j])

    return W

def ItemCFRecommendation(train, user, W, K):
    rank = dict()
    ru = train[user]
    for i, pi in ru:




def PrecisionRecallCoverage(train, test, N, K):
    hit = 0
    n_recall = 0
    n_precision = 0
    recommend_items = set()
    all_items = set()
    for user in train.keys():
        for item in train[user]:
            all_items.add(item)
    item_popularity = dict()
    for user, items in train.items():
        for item in items:
            if item not in item_popularity:
                item_popularity[item] = 0
            item_popularity[item] += 1
    ret = 0
    n = 0
    W = ItemSimilarity(train)
    for user in train.keys():
        if user not in test:
            continue
        tu = test[user]
        rank = ItemCFRecommendation(user, train, K, W)[0:N]

        for item, cuv in rank:
            if item in tu:
                hit += 1
        n_recall += len(tu)
        n_precision += len(rank)

        for item, cuv in rank:
            recommend_items.add(item)

        for item, cuv in rank:
            ret += math.log(1 + item_popularity[item])
            n += 1

    print len(all_items), len(recommend_items)
    precision = hit / 1.0 / n_precision
    recall = hit / 1.0 / n_recall
    coverage = len(recommend_items) / 1.0 / len(all_items)
    ret /= 1.0*n

    return precision, recall, coverage, ret