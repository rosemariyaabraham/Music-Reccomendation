import pandas as pd
import pymysql
import scipy.sparse as sparse
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances,cosine_distances

def main():
   print(filtering(1,'malayalam'))

#__________________________code_____________________________

def create_df(language):
    conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='samohtmanjaly2147',
            db='music'
        )
    
    with conn.cursor() as cursor:
        query = "SELECT * FROM " + language +'id'

        cursor.execute(query)
        cursor.fetchall()

        return pd.read_sql(query, conn)

def item_label(n, sortprod):
    for i, j in zip(sortprod, range(len(sortprod))):
        if n==i:
            return j

def user_label(n, sortuser):
    for i,j in zip(sortuser, range(len(sortuser))):
        if n==i:
            return j

def predict(ratings, similarity, type='user'):
    if type == 'user':
        mean_user_rating = ratings.mean(axis=1)
        ratings_diff = (ratings - mean_user_rating[:, np.newaxis])
        pred = mean_user_rating[:, np.newaxis] + similarity.dot(ratings_diff) / np.array([np.abs(similarity).sum(axis=1)]).T
    elif type == 'item':
        mean_item_rating = ratings.mean(axis=0)
        ratings_diff = (ratings - mean_item_rating)
        pred = mean_item_rating + ratings_diff.dot(similarity) / np.array([np.abs(similarity).sum(axis=1)])
    return pred

def create_testdf(language):
    conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='samohtmanjaly2147',
            db='music'
        )
    
    with conn.cursor() as cursor:
        query = "SELECT * FROM " + language +'test'

        cursor.execute(query)
        cursor.fetchall()

        return pd.read_sql(query, conn)

def filtering(userid,lang):
    data = create_df(lang)
    sparse_item_user = sparse.csr_matrix((data['count'].astype(float), (data['songID'], data['userID'])))
    sparse_user_item = sparse.csr_matrix((data['count'].astype(float), (data['userID'], data['songID'])))

    value = sparse_user_item.data
    column_index = sparse_user_item.indices
    row_pointers = sparse_item_user.indices

    row_index = np.sort(row_pointers)
    column_indexsort = np.sort(column_index)
    column_unique = np.unique(column_indexsort)
    row_unique = np.unique(row_index)
    
    d = {'userID':row_index,'songID':column_index,'count':value}
    df = pd.DataFrame(d)
    dfsort = df.sort_values(by=['userID','songID'])
    sortprod = dfsort.songID.unique()
    sortuser = dfsort.userID.unique()

    #prodlabel = [item_label(song, sortprod) for song in dfsort.songID]
    #userlabel = [user_label(song, sortprod) for song in dfsort.userID]
    prodlabel = list(map(item_label, dfsort.songID))
    userlabel = list(map(user_label, dfsort.userID))
    dfsort["label1"] = prodlabel
    dfsort["label2"] = userlabel
 
    n_users = dfsort.userID.unique().shape[0]
    n_items = dfsort.songID.unique().shape[0]
    data_matrix = np.zeros((n_users, n_items))
    
    for i in dfsort.itertuples():
        data_matrix[i[5], i[4]] = i[3]
        
    user_similarity = pairwise_distances(data_matrix, metric='cosine')
    user_similarity_df = pd.DataFrame(user_similarity, index = row_unique, columns = row_unique)
    user_similarity_df = 1 - user_similarity_df
    
    item_similarity = pairwise_distances(data_matrix.T, metric='cosine')
    item_similarity_df = pd.DataFrame(item_similarity, index=column_unique, columns=column_unique)
    item_similarity_df = 1 - item_similarity_df
    item_prediction = predict(data_matrix, item_similarity_df.values, type='item')
    item_prediction_df = pd.DataFrame(item_prediction, index=row_unique, columns=column_unique)
    user_prediction = predict(data_matrix, user_similarity_df.values, type='user')
    user_prediction_df = pd.DataFrame(user_prediction, index=row_unique, columns=column_unique)
    
    testdata = create_testdf(lang)
    item_pred_sub = pd.DataFrame(columns=['userID', 'song_list'])
    item_pred_sub['userID'] = testdata['userID'].values
    sub_list = []
    for user in item_pred_sub['userID'].values:
        sub_list.append(item_prediction_df.loc[user].sort_values(ascending=False)[0:10].index.values.tolist())

    item_pred_sub['song_list'] = sub_list
    
    show_song=[]
    for i in item_pred_sub:
        if userid == item_pred_sub.userID[i]:
            show_song=show_song.append(item_pred_sub.song_list[i])
    
    return show_song
    


    #__________________________code_____________________________
    if __name__ == '__main__':
        main()
