# Retrieves metadata [accession, submission date, title, # of assays ] for every 
# submission in PRIDE and writes them out to a text file. If -np flag is not set,
# the script then calls 'parse and plot PRIDE submissions.py' to plot the total
# submissions by year using matplotlib

# TO RUN: execute script from within the directory containing both this script AND 'parse and plot PRIDE submissions.py'

import argparse
import sys
import json
import urllib.request
import math
import pandas as pd
import time

# create the argument parser
parser = argparse.ArgumentParser(description='')
# Add optional switches
parser.add_argument('-r', '--recordsPerQuery', type=int, action='store', 
	dest='recordsPerQuery', metavar='NUM', default=50,
	help='Number of results to get per query (default=50)')
parser.add_argument('-p', dest='doPlot', action='store_true', default='True')
parser.add_argument('-np', dest='doPlot', action='store_false', default='False')
parser.set_defaults(feature=True)

# parse the arguments
args = parser.parse_args()
recordsPerQuery = args.recordsPerQuery
doPlot = args.doPlot

print('Retrieving ' + str(recordsPerQuery) + ' records per query....')

### query for total # of records
url = 'http://www.ebi.ac.uk/pride/ws/archive/project/count?'

request = urllib.request.Request(url)
response = urllib.request.urlopen(request).read()

result = json.loads(response.decode('utf8'))

print(str(result) + ' current submissions in PRIDE...')

# calculate total number of pages you need to retrieve
totalpages = math.ceil(result/recordsPerQuery)

# declare data frame that will hold results
df = pd.DataFrame()

# iterate over pages, get records, and build the data table
for page in range(0,totalpages):
	print('Retrieving page ' + str(page+1) + ' of ' + str(totalpages))
	query = 'query=&page='+str(page)+'&show='+str(recordsPerQuery)
	url = 'http://www.ebi.ac.uk/pride/ws/archive/project/list?' + query
	
	request = urllib.request.Request(url)
	response = urllib.request.urlopen(request).read()
	
	result = json.loads(response.decode('utf8'))
	projects = result['list']
	
	accessions = []
	titles = []
	dates = []
	numAssays = []
	
	# for each of the provided project accessions retrieve the record and print some details
	for project in projects:
		try:
			accessions.append(project['accession'])
			titles.append(project['title'])
			dates.append(project['publicationDate'])
			numAssays.append(str(project['numAssays']))
		except (Exception):
			print('Error for project: ' + project['accession'] + ' perhaps this project does not exist?')
		
	currentdf=pd.DataFrame({'accession': accessions,'title': titles, 'date': dates, 'numAssays': numAssays})
	df = df.append(currentdf, ignore_index = True)
	
	# sleep 10 seconds between requests because we're considerate
	time.sleep(10)

# write data frame out to text file
df.to_csv('PRIDE submission list.txt',sep='\t',header=True)

# launch follow-up script to parse the PRIDE submission list generated
# in this script and plot the cumulative number of submission by year
if doPlot:
	print('Plotting...')
	exec(open('./parse and plot PRIDE submissions.py').read())
