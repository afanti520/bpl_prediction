import _mysql
import MySQLdb
import sys
from math import exp
from math import factorial
from random import *

class Lambda(object):
	"""Get the Lambda for every game and make the comparaison with the real result for each reason.
	   No Prediction Here, just stats for every season and compare them with a basic Poisson LambdaAway with the real result
	"""
	def __init__(self, season,database,xmin,xmax,printOrNot):
		super(Lambda, self).__init__()
		self.season = season
		self.database=database
		self.lambdaHome=0
		self.lambdaAway=0
		self.seasonGame=[]
		self.successScore=0   # How good we predicted the score result (2-0 , ... )
		self.successOutCome=0 # How good we predicted wins looses or draws
		self.realDraw=0
		self.predictedDraw=0
		self.cursor = database.cursor()
		self.xmin=xmin
		self.xmax=xmax
		self.printOrNot=printOrNot
		
	def getGames(self):
		self.cursor.execute( 
			"SELECT id, HomeTeam, AwayTeam, FTHG, FTAG, MatchDay \
		 	FROM championship"+str(self.season)+" WHERE MatchDay="+str(self.xmax+1)
		 	)
		attributes=self.cursor.fetchall()
		for attrib in attributes:
			tmp=[]
			tmp.append(str(attrib[0]))
			tmp.append(str(attrib[1]))
			tmp.append(str(attrib[2]))
			tmp.append(str(attrib[3]))
			tmp.append(str(attrib[4]))
			tmp.append(str(attrib[5]))
			self.seasonGame.append(tmp)

	def getTeamAttr(self,homeTeam,awayTeam):
		homeTeamAttr=[]
		awayTeamAttr=[]
		self.cursor.execute ("""
					   SELECT Attack, Defense, Beta, BetaHome
					   FROM ranking"""+str(self.season)+"""
					   WHERE Team=%s
					""", (homeTeam))
		attributes=self.cursor.fetchall()
		for attrib in attributes:
			homeTeamAttr.append(str(attrib[0]))
			homeTeamAttr.append(str(attrib[1]))
			homeTeamAttr.append(str(attrib[2]))
			homeTeamAttr.append(str(attrib[3]))

		self.cursor.execute ("""
					   SELECT Attack, Defense, Beta, BetaHome
					   FROM ranking"""+str(self.season)+"""
					   WHERE Team=%s
					""", (awayTeam))
		attributes=self.cursor.fetchall()
		for attrib in attributes:
			awayTeamAttr.append(str(attrib[0]))
			awayTeamAttr.append(str(attrib[1]))
			awayTeamAttr.append(str(attrib[2]))
			awayTeamAttr.append(str(attrib[3]))
		return(homeTeamAttr,awayTeamAttr)

	def calculateLambda(self):
		"""
		Get the LambdaHome = Beta * BetaHome * Offence(HomeTeam) * Defense(AwayTeam)
		Get the LambdaAway = Beta * Offence(AwayTeam) * Defense(HomeTeam)
		"""
		self.getGames()
		count=1
		for game in self.seasonGame:
			attrib=self.getTeamAttr(game[1],game[2]) # id = 0, HomeTeam = 1, AwayTeam = 2, FTHG = 3, FTAG = 4, MatchDay = 5
			#Attack=00, Defense=01, Beta=02, BetaHome=03
			#Attack=10, Defense=11, Beta=12
			self.lambdaHome=exp(float(attrib[0][0])-float(attrib[1][1])+float(attrib[0][3]))
			self.lambdaAway=exp(float(attrib[1][0])-float(attrib[0][1]))
			#print(self.lambdaHome,self.lambdaAway)
			proba=self.probabilities()
			#proba=self.probabilitiesImproved()
			#self.printStat(game,proba)   # Decomment to see answer in terminal
			self.compareProb(game,proba)
			count+=1

		return(round((self.successScore*100.0)/(len(self.seasonGame)*1.0)), \
			   round((self.successOutCome*100.0)/(len(self.seasonGame)*1.0)))

	def printResult(self):
		print("Score Success : "+str(round((self.successScore*100.0)/(len(self.seasonGame)*1.0)))+"%")
		print("Prediction Result : "+str(round((self.successOutCome*100.0)/(len(self.seasonGame)*1.0)))+"%")

	def compareProb(self,game,proba):
		if (game[3]>game[4]) : #If the Home Team Win
			if (proba[0] > proba[1] and proba[0]> proba[2]): #If we Predicted a Win
				self.successOutCome+=1
		elif (game[3]==game[4]) : #If there is a draw
			self.realDraw+=1
			if (proba[2] > proba[1] and proba[2]> proba[0]): #If we Predicted a draw
				self.successOutCome+=1
		else : #If the away team won
			if (proba[1] > proba[0] and proba[1]> proba[2]): #If we Predicted a win for the home team
				self.successOutCome+=1
		if (int(proba[3])==int(game[3]) and int(proba[4])==int(game[4])): # If the predicted score is the same than the game score
				self.successScore+=1


	def printStat(self,game,proba):
		#if ("-1" in str(game[3])): # It means its a game from the current seaon that has not been played yet
		#print(proba)
		print("MATCH : "+game[1]+" ---- "+game[2])
		print("Home Win : "+str(round(proba[0]))+"%")
		print("Away Win : "+str(round(proba[1]))+"%")
		print("Draw : "	   +str(round(proba[2]))+"%")
		print("Expected score is : "+str(proba[3])+"-"+str(proba[4]))
		print("Real score is : "+str(game[3]+"-"+str(game[4])))
		#print("Real Score is still unknown")
		print("-----------------------------------------")

	def probabilities(self):
		homeWin=0
		awayWin=0
		draw=0
		prob=[[0 for x in range(10)] for x in range(10)]
		for homeGoal in range(0,10):
			for awayGoal in range(0,10):
				home=self.poisson(self.lambdaHome,homeGoal)
				away=self.poisson(self.lambdaAway,awayGoal)
				score=home*away
				lowBound=max(((-1*1.0)/(home)),((-1*1.0)/(away)))
				upBound =min(((1*1.0)/(home*away)),1)
				p=(lowBound+upBound)/(2*1.0)
				if (homeGoal > awayGoal ): #If the Home team wins
					homeWin+=(home*away)
				elif (homeGoal == awayGoal):
					if (homeGoal==0 and awayGoal==0): # 0-0 Case : x=0 and y=0 --> gamma= 1-home*away*p
						gamma=1-home*away*p
						draw+=(gamma*home*away)
					else:
						draw+=(home*away)
				else:
					awayWin+=(home*away)
				prob[homeGoal][awayGoal]=home*away
		score=0
		homeGoal=0
		awayGoal=0
		for i in range(10):
			for j in range(10):
				if prob[i][j]>score:
					score=prob[i][j]
					homeGoal=i
					awayGoal=j
		return (homeWin*100,awayWin*100,draw*100,homeGoal,awayGoal)

	"""
	home = pymc.Normal('home', 0, .0001, value=0)
	mu_att = pymc.Normal('mu_att', 0, .0001, value=0)
	mu_def = pymc.Normal('mu_def', 0, .0001, value=0)

	
	"""

	"""
	def probabilitiesImproved(self):
		home=[]
		away=[]
		for homeGoal in range(0,6):
			for awayGoal in range(0,6):
				home.append(self.poisson(self.lambdaHome,homeGoal))
				away.append(self.poisson(self.lambdaAway,awayGoal))
		meanX=0
		meanY=0
		for i in range(0,len(home)):
			meanX+=home[i]
			meanY+=away[i]
		#print(meanX,meanY)
		meanX=meanX/(len(home)*1.0)
		meanY=meanY/(len(home)*1.0)
		#print(meanX,meanY)
		covariance=0
		for i in range(0,len(home)):
			res=(home[i]-meanX)*(away[i]-meanY)
			covariance+=res
		covariance=covariance/((len(home)-1)*1.0)
		homeWin=0
		awayWin=0
		draw=0
		homeScore=0
		maxProbHome=0
		awayScore=0
		maxProbAway=0

		for homeGoal in range(0,6):
			for awayGoal in range(0,6):
				lambda3=covariance
				Pxy=self.poissonImproved(self.lambdaHome,self.lambdaAway,lambda3,homeGoal,awayGoal)
				#away=self.poissonImproved(self.lambdaAway,self.lambdaHome,lambda3,awayGoal,homeGoal)
				if (Pxy > maxProbHome):
					homeScore=homeGoal
					maxProbHome=Pxy
				if (Pxy > maxProbAway ):
					awayScore=awayGoal
					maxProbAway=Pxy
				if (homeGoal > awayGoal ): #If the Home team wins
					homeWin+=Pxy
				elif (homeGoal == awayGoal):
					draw+=Pxy
				else:
					awayWin+=Pxy
		return (homeWin*100,awayWin*100,draw*100,homeScore,awayScore)
	"""
	def poisson(self,lambda_,x):
		return ((exp(-lambda_)*(lambda_**x))/(factorial(x)))
	"""
	def poissonImproved(self,l1,l2,l3,x,y):
		resOne=exp(-(l1+l2+l3))
		resTwo=((l1**x)*(l2**y))/((factorial(x))*(factorial(y)))
		res3=0
		minimum=min(x,y)
		for k in range(minimum+1): # 0 - minimum
			binomal1=self.binomalCoef(x,k)
			binomal2=self.binomalCoef(y,k)
			third=factorial(k)
			fourth=((l3*1.0)/(l1*l2*1.0))**k
			res3+=binomal1*binomal2*third*fourth
		proba=resOne*resTwo*res3
		return(proba)

	def binomalCoef(self,x,y):
		if y == 1 or y == x:
			return 1
		if y>x:
			return 0
		else:
			a = factorial(x)
			b = factorial(y)
			div = ((a*1.0)/(b*(x-y)*1.0))
			return div
	"""
