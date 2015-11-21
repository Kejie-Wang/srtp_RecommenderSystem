import math
import operator
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
        if user not in data:
            data[user] = set()
        data[user].add(item)

    return data

'''
@brief Split the data into M parts for a fixed seed
    one as the test and the remain M-1 parts as train
@:param data a dict, from user to item, the total data
@:param M the numbers of parts
@:param k the kth experiment(0<=k<=M-1)
@:param seed a fixed seed used to generate the same random list
@:return train, test the dict, from user to items
'''
def SplitData(data, M, k, seed):
    test = dict()
    train = dict()
    random.seed(seed)
    for user, items in data.items():
        for item in items:
            if random.randint(0, M) == k:
                if user not in test:
                     test[user] = set()
                test[user].add(item)
            else:
                if user not in train:
                    train[user] = set()
                train[user].add(item)

    return train, test

'''
calculate the similarity of the users based on the cosine formulate
s(A, B) = len(N(A)&N(B))/(len(N(A)) * len(N(B))
the time complexity of this algorithm is O(U*U)
@param train The train data set which is a dict(user-items list)
'''
def UserSimilarityBasedCosine(train):
    W = dict()
    for u in train.keys():
        for v in train.keys():
            if u == v:
                continue
            if u not in W:
                W[u] = dict()
            W[u][v] = len(train[u].union(train[v])) / math.sqrt(len(train[u]) * len(train[v]))

    return W

#calculate the similarity of the users based on the inverse table for item_users
def UserSimilarityBasedInverseTable(train):
    #build a inverse table
    item_users = dict()
    for u, items in train.items():
        for i in items:
            if i not in item_users:
                item_users[i] = set()
            item_users[i].add(u)

    #calculate the co-rated items between users
    N = dict()
    C = dict()

    for i, users in item_users.items():
        for u in users:
            #calculate the co-rated items to the specific user
            if u not in N:
                N[u] = 0
            N[u] += 1
            #calculate the co-rated items between users
            for v in users:
                if u == v:
                    continue
                if u not in C:
                    C[u] = dict()
                if v not in C[u]:
                    C[u][v] = 0
                C[u][v] += 1

    #calculte final similarity of the matrix W
    W = dict()
    for u, related_users in C.items():
            if u not in W:
                W[u] = dict()
            for v, cuv in related_users.items():
                W[u][v] = cuv / math.sqrt(N[u] * N[v])

    return W

#TopN Recommendation based on the user filter
#select K users who are most related to the given user
def UserCFRecommend(user,train, K, W):
    rank = dict()
    interacted_items = train[user]
    for v, wuv in sorted(W[user].items(), key = operator.itemgetter(1), reverse = True)[0:K]:
        for i in train[v]:
            #filter the item that user interacted before
            if i in interacted_items:
                continue
            if i not in rank:
                rank[i] = 0
            rank[i] += wuv

    #return rank
    return sorted(rank.items(), key = operator.itemgetter(1), reverse = True)

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
    W = UserSimilarityBasedInverseTable(train)
    for user in train.keys():
        if user not in test:
            continue
        tu = test[user]
        rank = UserCFRecommend(user, train, K, W)[0:N]

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

    #print len(all_items), len(recommend_items)
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
        precision, recall, coverage, ret = PrecisionRecallCoverage(train, test, 5, K)
        allPrecision += precision
        allRecall += recall
        allCoverage += coverage
        allRet += ret

    print allPrecision / 8.0, allRecall / 8.0, allCoverage / 8.0, allRet / 8.0