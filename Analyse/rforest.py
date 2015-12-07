from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import NearestNeighbors


from numpy import genfromtxt, savetxt
from joblib import Parallel, delayed
import multiprocessing
import csv
import pandas as pd
import numpy as np

num_cores = multiprocessing.cpu_count()

iterations = 100

team_names = ['Man United', 'Man City','Arsenal','Chelsea','Liverpool','West Ham','Leicester','Everton','Swansea','Crystal Palace','Tottenham','West Brom','Southampton','Aston Villa','Stoke','Newcastle','Sunderland']
team_names = [team_name.lower().replace(" ", "_") for team_name in team_names]

def get_probabilities(team_name):
    #create the training & test sets, skipping the header row with [1:]
    #dataset = genfromtxt(open('trainsets/arsenal_train.csv','r'), dtype='int', delimiter=',', skip_header=1)[1:]
    dataset = genfromtxt('trainsets/'+team_name+'_train.csv', dtype='int', delimiter=',', skip_header=1)[1:]    
    target = [x[-1] for x in dataset]
    train = [x[0:-1] for x in dataset]
    test = genfromtxt('testsets/'+team_name+'_test.csv', dtype='int', delimiter=',', skip_header=1)[1:]
    
    rf_result = np.zeros((test.shape[0], 3))
    for i in range(iterations):
        
        #create and train the random forest
        #multi-core CPUs can use:
        rf = RandomForestClassifier(n_estimators=10, n_jobs=4)
        #single cpu usage, rf = RandomForestClassifier(n_estimators=100)
        rf.fit(train, target)
        rf_result = rf_result + rf.predict_proba(test)

    rf_result = rf_result/iterations

    #create and train the random forest
    #multi-core CPUs can use:
    sgd = SGDClassifier(loss='log', n_jobs=4)
    #single cpu usage, rf = RandomForestClassifier(n_estimators=100)
    sgd.fit(train, target)

    gbc = GradientBoostingClassifier(n_estimators=10)
    #single cpu usage, rf = RandomForestClassifier(n_estimators=100)
    gbc.fit(train, target)




    savetxt('results/'+team_name+'_rf.csv', rf.predict(test), delimiter=',', fmt='%f')
    savetxt('results/'+team_name+'_rf_proba.csv', rf_result, delimiter=',', fmt='%f')

    savetxt('results/'+team_name+'_sgd.csv', sgd.predict(test), delimiter=',', fmt='%f')
 #   savetxt('results/'+team_name+'_sgd_proba.csv', sgd.predict_proba(test), delimiter=',', fmt='%f')

    savetxt('results/'+team_name+'_gbc.csv', gbc.predict(test), delimiter=',', fmt='%f')
    savetxt('results/'+team_name+'_gbc_proba.csv', gbc.predict_proba(test), delimiter=',', fmt='%f')


def main():
    #create the training & test sets, skipping the header row with [1:]
    #dataset = genfromtxt(open('trainsets/arsenal_train.csv','r'), dtype='int', delimiter=',', skip_header=1)[1:]
    dataset = genfromtxt('trainsets/arsenal_train.csv', dtype='int', delimiter=',', skip_header=1)[1:]    
    target = [x[-1] for x in dataset]
    train = [x[0:-1] for x in dataset]
    test = genfromtxt('testsets/arsenal_test.csv', dtype='int', delimiter=',', skip_header=1)[1:]
    
    #create and train the random forest
    #multi-core CPUs can use:
    rf = RandomForestClassifier(n_estimators=100, n_jobs=4)
    #single cpu usage, rf = RandomForestClassifier(n_estimators=100)
    rf.fit(train, target)

    savetxt('results/arsenal.csv', rf.predict(test), delimiter=',', fmt='%f')


def joint_probabilities(home_team, away_team, matchday):
    alpha = 0.5
    home_lose = -1
    draw = -1
    home_win = -1
    try:
        with open('results/'+home_team+'_proba.csv') as f:
            home_probs = [[float(elem.strip()) for elem in line.split(",")] for line in f.readlines()]


        with open('results/'+away_team+'_proba.csv') as f:
            away_probs = [[float(elem.strip()) for elem in line.split(",")] for line in f.readlines()]

            home_prob = home_probs[matchday-1]
            away_prob = away_probs[matchday-1]

            home_win = (alpha * home_prob[2]) + ((1 - alpha) * away_prob[0])
            home_lose = (alpha * home_prob[0]) + ((1 - alpha) * away_prob[2])
            draw = (alpha * home_prob[1]) + ((1 - alpha) * away_prob[1])

    except FileNotFoundError:
        print('file does not exist')


    return [home_lose, draw, home_win] 

def get_joint_probabilities(filename):
    headings = ["date", "home", "away", "homescore", "awayscore", "matchday"]
    matches = pd.read_csv(filename, header=None, names=headings)
    joint_df = pd.DataFrame(columns=["home", "away", "homescore", "awayscore", "matchday", "home_lose", "draw", "home_win"])
    for index, row in matches.iterrows():

        home_team =row['home'].lower().replace(' ', '_')
        away_team = row['away'].lower().replace(' ', '_')
        matchday = row['matchday']
        if matchday ==14:
            break
        
        probs = joint_probabilities(home_team, away_team, matchday)

        joint_df = joint_df.append({"home": home_team, "away": away_team,"homescore": row["homescore"], "awayscore": row["awayscore"], "matchday": matchday, "home_lose": probs[0], "draw": probs[1], "home_win":probs[2]}, ignore_index=True)
        #=IF(C2-D2>0;1;IF(C2-D2<0;-1;1))
        #=IF(F2>G2;IF(F2>H2;-1;1);IF(G2>H2;0;1))
    try:
        joint_df.to_csv("joint_probabilities.csv", index=False)
    except UnicodeEncodeError:
        print("couldn't write word, ecoding error")
    


if __name__=="__main__":
    Parallel(n_jobs=num_cores)(delayed(get_probabilities)(team_name) for team_name in team_names)
    get_joint_probabilities('championship1516.csv')
    #main()
    #get_probabilities('west_ham')