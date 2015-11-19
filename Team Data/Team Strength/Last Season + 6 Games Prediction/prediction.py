import _mysql
import MySQLdb
import sys

GAMESTOADAPT=6
NEWTEAMLAMBDA=0.8

class DBPonderation(object):
	"""docstring for DBPonderation"""
	def __init__(self, database,season1,season2):
		super(DBPonderation, self).__init__()
		self.database = database
		self.season1=season1
		self.season2=season2
		self.cursor = database.cursor()
		self.table1Rows=[]
		self.table2Rows=[]

	def makePonderation(self):
		self.table1Rows=self.getRows(self.season1) # Previous Season
		self.table2Rows=self.getRows(self.season2) # Current Season
		for S2Team in self.table2Rows:
			newTeam=True
			for S1Team in self.table1Rows:
				if ( S2Team[0].strip(" ")== S1Team[0].strip(" ")): # If the team in season 2 is also in season 1 , we make the ponderation
					vec=[]
					newTeam=False
					for attrib in range (1 , len(S2Team)):
						res=((float(S1Team[attrib])*38 + float(S2Team[attrib])*GAMESTOADAPT)*1.0)/((38+GAMESTOADAPT)*1.0)
						vec.append(res)
					self.updateValue(S2Team[0],attrib,vec)
			if (newTeam == True): # IF its a new team in the cahmpionship
				vec=[]
				for attrib in range (1 , len(S2Team)):
					res=(NEWTEAMLAMBDA*38 + (float(S2Team[attrib])*GAMESTOADAPT)*1.0)/((38+GAMESTOADAPT)*1.0)
					vec.append(res)
				self.updateValue(S2Team[0],attrib,vec)
			


	def updateValue(self,team,attribNumb,vec):
		self.cursor.execute ("""
					   UPDATE ranking"""+str(self.season2)+"""
					   SET HomeAttack=%s, HomeDefense=%s, AwayAttack=%s, AwayDefense=%s, Beta=%s, BetaHome=%s
					   WHERE Team=%s
					""", (float("{0:.4f}".format(float(vec[0]))),float("{0:.4f}".format(float(vec[1]))), \
						  float("{0:.4f}".format(float(vec[2]))),float("{0:.4f}".format(float(vec[3]))), \
						  float("{0:.4f}".format(float(vec[4]))),float("{0:.4f}".format(float(vec[5]))), team))
		self.database.commit()


	def getRows(self,season):
		self.cursor.execute( 
			"SELECT Team, HomeAttack,HomeDefense,AwayAttack,AwayDefense,Beta,BetaHome \
		 	FROM ranking"+str(season)
		 	)
		rows=self.cursor.fetchall()
		res=[]
		for elem in rows:
			count=0
			tmp=[]
			while (count < len(elem)):
				tmp.append(str(elem[count]))
				count+=1
			res.append(tmp)
		return res