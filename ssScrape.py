#Python 2.* compatible
import mechanize
import bs4
import re
import sys
import string

prot_name = sys.argv[1]
seq = sys.argv[2]
output_file = sys.argv[3]

#prot_name = 'CD3zeta'
#seq = 'KNPQEGLYNELQKDK'
#seq = 'mkwkalftaailqaqlpiteaqsfglldpklcylldgilfiygviltalflrvkfsrsadapayqqgqnqlynelnlgrreeydvldkrrgrdpemggkpqrrknpqeglynelqkdkmaeayseigmkgerrrgkghdglyqglstatkdtydalhmqalppr'

for stringency in ['Low','Medium','High']:
	try:
		br = mechanize.Browser()
		response = br.open('http://scansite.mit.edu/motifscan_seq.phtml')

		br.form = list(br.forms())[0]

		#1. set protein ID
		pid_control = br.form.find_control('protein_id')
		pid_control.value = prot_name

		#2. set peptide sequence
		seq_control = br.form.find_control('sequence')
		seq_control.value = seq

		#3. set search to look for ALL motifs
		motifOpt_control = br.form.find_control('motif_option')
		motifOpt_control.value = ['all']

		#4. set stringency to LOW
		string_control = br.form.find_control('stringency')
		string_control.value = [stringency]

		#5. submit form and get response
		response = br.submit()

		#6. pass HTML response to BeautifulSoup for parsing
		soup = bs4.BeautifulSoup(response.read())
		#print soup.prettify()

		#7. iterate over all rows & parse. if the row is a header (denoted by red background color), get the motif type for the following entries.
			#otherwise, read the two descendants (columns) and parse the data.
		rows = soup.find_all('tr')

		hits = []

		for row in rows:
			for child in row.children:
				if child.has_attr('bgcolor'):
					#rows with red background define motif type
					if child['bgcolor']=='red':
						motif_fam = str(child.font.b)
						motif_fam = motif_fam.replace('<b>','').replace('</b>','')
					#rows with blue backgrounds have 2 columns: 
					#first is blue and identifies the motif
					elif child['bgcolor']=='blue':
						motif = str(child.font.b)
						motif = motif.replace('<b>','').replace('</b>','')
					#second column is light blue (6BBBFF) and identifies the interacting protein
					elif child['bgcolor']=='6BBBFF':
						interactor = str(child.a.b)
						interactor = interactor.replace('<b>','').replace('</b>','')
				#the u tag defines rows that just have descriptive headers
				elif len(child.select('u')) > 0:
					pass
				#the a tag defines rows with a URL string that can be parsed to get the motif match scores
				elif len(child.select('a')) > 0:
					url = child.a['href']
					r = re.match('.*site=([a-zA-Z][0-9]*)&.*score=([0-9]*\.[0-9]*)&.*percentile=([0-9.]*)&.*zscore=(\-{0,1}[0-9.]*)&.*sequence=([A-Z]*)',url)
					#if the match returns none, it matched the wrong url (row)
					if r != None:
						captured = r.groups()
						site = str(captured[0])
						site = site.replace('<b>','').replace('</b>','')
						score = captured[1]
						percentile = captured[2]
						zscore = captured[3]
						sequence = str(captured[4])
						hit = [motif_fam, motif, interactor, site, score, percentile, zscore, sequence, seq]
						hits.append(hit)
		break
	except:
		#If an error is encountered, repeat the request with the next highest stringency
		continue

#8. redirect stdout to the file specified in the arguments and write the results
open(output_file, 'w')

orig_stdout = sys.stdout
f = file(output_file, 'w')
sys.stdout = f

for i in range(0,len(hits)):
	sys.stdout.write(str(hits[i][0]))
	for j in range(1,len(hits[i])):
		sys.stdout.write('\t' +hits[i][j])
	sys.stdout.write('\n')