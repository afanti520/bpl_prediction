#creating training sets
from collections import OrderedDict
import pandas as pd

path = "./trainsets/"

def inc(word_dict, words):
    for word in words:
        if word in word_dict:
            word_dict[word] += 1
    
    return word_dict


def get_df(collection, words, res): 
    df = pd.DataFrame(columns=["win", "draw"])
    word_dict = OrderedDict((word, 0) for word in words)
    word_dict['w/l/d'] = res
    i=1
    while(i<=38):
        for tweet in collection.find({"matchday": i}):
            word_dict = inc(word_dict, tweet['text'])           
            df = df.append(word_dict, ignore_index=True)
            
        
        i+=1
  
def getTrainSets(teams, words, res):
    for team in teams:
        col_win = db[team_name+'_win']
        col_lose = db[team_name+'_lose']
        col_draw = db[team_name+'_draw']
        df_main = pd.DataFrame()
        df_win = get_df(col_win, words, 1)
        df_lose = get_df(col_lose, words, -1)
        df_draw = get_df(col_draw, words, 0)
        df_main.append(df_win, ignore_index=True)
        df_main.append(df_lose, ignore_index=True)
        df_main.append(df_draw, ignore_index=True)
        df.to_csv(path+team+"_train.csv")
        
        
    