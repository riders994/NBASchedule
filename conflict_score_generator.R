library(XML)

#Setting global vars and results
teamAbrevs = c("ATL","BOS","BKN","CHA","CHI","CLE","DAL","DEN","DET","GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NOR","NYK","OKC","ORL","PHI","PHO","POR","SAC","SAS","TOR","UTH","WAS")
dfList = list()
masterDates = c()

for(team in teamAbrevs){

  #1.0 Pulling the table

  tab = readHTMLTable(paste("http://www.espn.com/nba/team/schedule/_/name/", team, "/seasontype/2", sep = ""))
  
  #1.1 Unlisting
  
  tab = tab[[1]]
  year = rep("2018",82)
  
  #2.0 Cleaning Table
  #2.1 Remove Columns, Rows
  
  tab = tab[-grep("OPPONENT",tab$V2),]
  tab = tab[,c(2,1)]
  
  #2.2 Rename Columns
  
  names(tab)=c("Opponent","Day")
  
  #2.3 Add in Year
  
  year[(min(grep("Jan", tab$Day))):82] = "2019"
  
  #2.4 Add in Real Dates
  
  dates = as.Date(paste(tab$Day,year), format = "%a, %b %d %Y")
  tab$Date = dates
  row.names(tab)=c()
  
  #3.0 Add in to Main Results
  
  dfList[[(length(dfList)+1)]] = tab
  masterDates = c(masterDates, dates)
}

allDates = unique(masterDates)
teamAbrevs[29] = "UTA";
names(dfList) = teamAbrevs
span = length(allDates)


#Set up Conflict DF
#1.0 Set up receivers and vars

Conflicts = as.data.frame(matrix(ncol=0,nrow=span))
dates = as.character(allDates)

for(i in 1:30){
  Conflicts = cbind(Conflicts, as.numeric(allDates %in% dfList[[(i)]][,3]))
}
names(Conflicts) = teamAbrevs
row.names(Conflicts) = dates
mConflicts = Conflicts * rowSums(resTeamDates[,1:30])
teamTotals = colSums(mConflicts)
m = mean(teamTotals)
mConflicts = rbind(mConflicts, teamTotals)
row.names(mConflicts)[(span + 1)]="TeamTotals"
teamAbrevs[which(teamTotals<m)]
teamAbrevs[which(teamTotals < median(teamTotals))]
teamAbrevs[order(teamTotals)]

K = as.matrix(mConflicts)
teamTotals = teamTotals-82
teamMean = teamTotals/m
teamMean
resmat = matrix(0,ncol=30,nrow=30)

for(i in 1:29){
  dat = dfList[[(i)]][,3]
  for(j in (i+1):30)
  {
    resmat[i,j] = sum(dat %in% dfList[[(j)]][,3])
    resmat[j,i] = sum(dat %in% dfList[[(j)]][,3])
  }
}
as.data.frame(teamAbrevs)
TeamCons = as.data.frame(teamAbrevs)
TeamCons = as.data.frame(resmat)
names(TeamCons) = teamAbrevs
row.names(TeamCons) = teamAbrevs
View(TeamCons)
