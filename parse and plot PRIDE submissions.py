# parse the submission list created by 'Get PRIDE submission metadata.py'
# and generate a plot illustrating the cumulative PRIDE submissions by year

import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt

## read in PRIDE submission list
myfile = 'PRIDE submission list.txt'
df = pd.read_csv(myfile, sep='\t', header=(0), encoding='iso-8859-1')

## get column of submission dates...
## ...as strings:
# dates = df.date 
## ...as time objects:
dates = [ datetime.datetime.strptime(d,'%Y-%m-%d') for d in df.date ]

## list of timepoints that will be plotted on graph
start_time = datetime.datetime.strptime('2004-01-01', '%Y-%m-%d')
dateinc = pd.date_range(start=start_time, end=pd.datetime.today(), freq='AS').tolist()
dateinc.append(pd.datetime.today()) 

## make data frame to hold submission counts
zero_data = np.zeros(shape=(len(dateinc),1), dtype=np.int)
submissiondat = pd.DataFrame(zero_data, index=dateinc)
submissiondat.columns = ['Submissions']

## populate data frame with cumulative counts of submissions by year
for timestamp in dates:
	for d in submissiondat.index:
		if timestamp <= d:
			submissiondat.loc[d,'Submissions'] += 1

## make time series plot with matplotlib
submissiondat.plot(figsize=(15, 6),color='red',linewidth=3)
plt.suptitle('Total PRIDE submissions: 2004-present', fontsize=20)
plt.ylabel('Submitted datasets', fontsize=18)
plt.legend().set_visible(False)

# convert x axis ticks to Month Year format & specify which labels should be shown
custom_tick_locs = submissiondat.index[range(0,15,2)]
custom_tick_labels = map(lambda x: x.strftime('%B %Y'), submissiondat.index[range(0,15,2)])
plt.xticks(custom_tick_locs, custom_tick_labels)

# draw gridlines
plt.rc('grid', linestyle="dashed", color='lightgray')
plt.grid(True)

# view plot
plt.show()

# save plot
#plt.savefig('Total PRIDE submissions: 2004-present.png',format='png')
