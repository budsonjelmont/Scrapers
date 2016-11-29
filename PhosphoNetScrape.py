#Python 2.* compatible
import urllib2
import bs4
import re
import sys
import string

target_id = sys.argv[1]
site = sys.argv[2]
output_file = sys.argv[3]

# target_id = 'P20963'
# site = 'S124'
# output_file = 'C:/Users/Judson/Desktop/pnetOutput.txt'

response = urllib2.urlopen('http://www.phosphonet.ca/kinasepredictor.aspx?uni=' + target_id + '&ps=' + site)

page = response.read()

soup = bs4.BeautifulSoup(page)

#resultTable = soup.findAll('table', { 'class' : 'table-Info table-KinaseInfo' })
resultTable = soup.find_all('table', class_='table-Info table-KinaseInfo')
if resultTable.__len__() > 1:
	print 'ERROR: multiple result tables found for upstream kinase table search'
	sys.exit()
elif resultTable.__len__() < 1:
	print 'No results returned'
	open(output_file, 'w')
	sys.exit()

hits = []

resultTable = resultTable[0]

#iterate over all <tr>
for row in resultTable.find_all('tr', attrs={'class': None}):
	#each row has 7 columns: 
	# Protein Kinase Match (ignore this)
	# Human Kinase Short Name
	# Human UniProt. ID
	# Kinase Predictor V2 Score
	# Human Kinase Short Name (col2)
	# Human UniProt. ID (col2)
	# Kinase Predictor V2 Score - Proximity (col2)
	count = 1
	for cols in row.find_all(attrs={'class': 'td-LeftAlign'}):
		if count == 1:
			kinase_nameCol1 = cols.a.contents[0]
		elif count == 2:
			kinase_idCol1 = cols.a.contents[0]
		elif count == 3:
			kinPredictor_scoreCol1 = cols.contents[0]
		elif count == 4:
			kinase_nameCol2 = cols.a.contents[0]
		elif count == 5:
			kinase_idCol2 = cols.a.contents[0]
		elif count == 6:
			kinPredictor_scoreCol2 = cols.font.contents[0]
		count = count + 1
	hit = [target_id, site, kinase_nameCol1, kinase_idCol1, kinPredictor_scoreCol1, kinase_nameCol2, kinase_idCol2, kinPredictor_scoreCol2]
	hits.append(hit)

# redirect stdout to the file specified in the arguments and write the results
open(output_file, 'w')

orig_stdout = sys.stdout
f = file(output_file, 'w')
sys.stdout = f

for i in range(0,len(hits)):
	sys.stdout.write(str(hits[i][0]))
	for j in range(1,len(hits[i])):
		sys.stdout.write('\t' + str(hits[i][j]))
	sys.stdout.write('\n')