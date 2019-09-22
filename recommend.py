import pandas as pd
import pymysql

def main():
   print(recommend(1, 'malayalam'))


# ****--------------------------------Add your code here -----------------------------------

def create_df(language):
    conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='samohtmanjaly2147',
            db='music'
        )
    
    with conn.cursor() as cursor:
        query = "SELECT * FROM " + language

        cursor.execute(query)
        cursor.fetchall()

        return pd.read_sql(query, conn)



def recommend(user_id, lang):
    data = create_df(lang)
    sort = data.sort_values('rating', ascending=False) 
    popularity_recommendations = sort.head(30)
    
    user_recommendations = popularity_recommendations 
    cols = user_recommendations.columns.tolist()
    user_recommendations = user_recommendations[cols]
    return user_recommendations

# ****--------------------------------------------------------------------------------------
if __name__ == '__main__':
    main()