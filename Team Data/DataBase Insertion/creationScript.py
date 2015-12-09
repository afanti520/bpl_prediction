# -*- coding : utf-8 -*-
import _mysql
import sys

if __name__ == '__main__':	
	try:
		database = _mysql.connect('localhost', 'root', 'root', 'EPL'); #login, password, database
		years=["1011","1112","1213","1314","1415","1516"]
		print("Creating ranking and championship tables.")
		for year in years:
			database.query(
				"CREATE TABLE IF NOT EXISTS ranking"+str(year)+" \
				( \
				Rank		 			int 			NOT NULL	, \
				Team 					varchar(30) 	NOT NULL , \
				Played 					int				NOT NULL , \
				Wins 					int				NOT NULL , \
				Draws		 			int 			NOT NULL , \
				Losses		 			int 			NOT NULL , \
				GoalsFor		 		int 			NOT NULL , \
				GoalsAgainst		 	int 			NOT NULL , \
				GoalsDIFF		 		int 			NOT NULL , \
				Points		 			int 			NOT NULL , \
				HomeAttack 				DECIMAL(5,4) 				 , \
				HomeDefense 			DECIMAL(5,4) 				 , \
				AwayAttack 				DECIMAL(5,4) 				 , \
				AwayDefense 			DECIMAL(5,4) 				 , \
				Beta 					DECIMAL(5,4) 				 , \
				BetaHome 				DECIMAL(5,4) 				 , \
				PRIMARY KEY (Team) \
				); \
				"
			);
			if (year !="1516"):
				database.query(
					"CREATE TABLE IF NOT EXISTS championship"+str(year)+" \
					( \
					id 					int				NOT NULL	AUTO_INCREMENT, \
					GameDate 			datetime 		NOT NULL , \
					HomeTeam 			varchar(30)		NOT NULL , \
					AwayTeam 			varchar(30)		NOT NULL , \
					FTHG		 		int 			NOT NULL , \
					FTAG		 		int 			NOT NULL , \
					HC		 			int 			NOT NULL , \
					AC		 			int 			NOT NULL , \
					HY		 			int 			NOT NULL , \
					AY		 			int 			NOT NULL , \
					HR		 			int 			NOT NULL , \
					AR		 			int 			NOT NULL , \
					B365H 				DECIMAL(3,2) 			NOT NULL , \
					B365D 				DECIMAL(3,2) 			NOT NULL , \
					B365A 				DECIMAL(3,2) 			NOT NULL , \
					BWH 				DECIMAL(3,2) 			NOT NULL , \
					BWD 				DECIMAL(3,2) 			NOT NULL , \
					BWA 				DECIMAL(3,2) 			NOT NULL , \
					MatchDay 			int 			NOT NULL , \
					PRIMARY KEY (id), \
					FOREIGN KEY (HomeTeam) REFERENCES ranking"+str(year)+"(Team) \
					); \
					"
				);
			else: # We didn't took the bookmaker's odds for the last season so the table is a bit different
				database.query(
					"CREATE TABLE IF NOT EXISTS championship"+str(year)+" \
					( \
					id 					int				NOT NULL	AUTO_INCREMENT, \
					GameDate 			datetime 		NOT NULL , \
					HomeTeam 			varchar(30)		NOT NULL , \
					AwayTeam 			varchar(30)		NOT NULL , \
					FTHG		 		int 			NOT NULL , \
					FTAG		 		int 			NOT NULL , \
					MatchDay 			int 			NOT NULL , \
					PRIMARY KEY (id), \
					FOREIGN KEY (HomeTeam) REFERENCES ranking"+str(year)+"(Team) \
					); \
					"
				);


	
		database.close();
		print("Done creating Table")
		
	except (_mysql.Error):
		
		print ("Mysql error ")
		sys.exit(1)
