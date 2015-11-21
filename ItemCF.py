import math
import operator
import random

'''
train, test: a dict, from user to item
item: a dict, from an item to the rating
'''
def ReadData(name, splitStr = '\t'):
    data = dict()
    try:
        fp = open(name)
        for line in fp:
            t = line.split(splitStr)
            user = t[0]
            item = t[1]
            rating = t[2]
            if user not in data:
                data[user] = dict()
            data[user][item] = rating
    except:
        print "Open file error"
        exit()
    return data

'''
@brief Split the data into M parts, one as the test set and the other M-1 parts as the train set
@:param data The source data which is a dict from a user to the related items which is a dict from the item to the rating
@:param M The number of part
@:param k The kth experiment
@:param seed The random seed used to sure the random sequence is fixed
@:return train, test a dict from the user to the item which is a dict from item to rating
'''
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
                    train[user] = dict()
                train[user][item] = rating

    return train, test

def ItemSimilarity(train):
    #calculate co-rated users between items
    C = dict()
    N = dict()
    for u, items in train.items():
        for i, iRating in items.items():
            if i not in N:
                N[i] = 0
            N[i] += 1
            for j, jRating in items.items():
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
    #pi is the rating that the user rates for the item i, wj is the similarity between items i and j
    for i, pi in ru.items():
        for j, wj in sorted(W[i].items(), key=operator.itemgetter(1), reverse=true)[0:K]:
            #filter items which are already in the train set
            if j in ru:
                continue
            rank[j] += pi*wj

    return rank

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


#main
#train = ReadData("ml-100k//u4.base")
#test = ReadData("ml-100k//u4.test")
data = ReadData("ml-100k//u.data", '\t')

for K in [2, 5, 10, 20, 40, 60, 80, 160]:
    print "k = ", K
    allPrecision = 0
    allRecall = 0
    allCoverage = 0
    allRet = 0
    for k in range(8):
        train, test = SplitData(data, 8, k, 100)
        precision, recall, coverage, ret = PrecisionRecallCoverage(train, test, 15, K)
        allPrecision += precision
        allRecall += recall
        allCoverage += coverage
        allRet += ret

    print allPrecision / 8.0, allRecall / 8.0, allCoverage / 8.0, allRet / 8.0