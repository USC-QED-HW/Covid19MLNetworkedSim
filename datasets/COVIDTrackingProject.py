import requests
states = {'AK': 'Alaska','AL': 'Alabama','AR': 'Arkansas','AS': 'American Samoa','AZ': 'Arizona','CA': 'California','CO': 'Colorado','CT': 'Connecticut','DC': 'District of Columbia','DE': 'Delaware','FL': 'Florida','GA': 'Georgia','GU': 'Guam','HI': 'Hawaii','IA': 'Iowa','ID': 'Idaho','IL': 'Illinois','IN': 'Indiana','KS': 'Kansas','KY': 'Kentucky','LA': 'Louisiana','MA': 'Massachusetts','MD': 'Maryland','ME': 'Maine','MI': 'Michigan','MN': 'Minnesota','MO': 'Missouri','MP': 'Northern Mariana Islands','MS': 'Mississippi','MT': 'Montana','NC': 'North Carolina','ND': 'North Dakota','NE': 'Nebraska','NH': 'New Hampshire','NJ': 'New Jersey','NM': 'New Mexico','NV': 'Nevada','NY': 'New York','OH': 'Ohio','OK': 'Oklahoma','OR': 'Oregon','PA': 'Pennsylvania','PR': 'Puerto Rico','RI': 'Rhode Island','SC': 'South Carolina','SD': 'South Dakota','TN': 'Tennessee','TX': 'Texas','UT': 'Utah','VA': 'Virginia','VI': 'Virgin Islands','VT': 'Vermont','WA': 'Washington','WI': 'Wisconsin','WV': 'West Virginia','WY': 'Wyoming'}
final = {'AK': [],'AL': [],'AR': [],'AS': [],'AZ': [],'CA': [],'CO': [],'CT': [],'DC': [],'DE': [],'FL': [],'GA': [],'GU': [],'HI': [],'IA': [],'ID': [],'IL': [],'IN': [],'KS': [],'KY': [],'LA': [],'MA': [],'MD': [],'ME': [],'MI': [],'MN': [],'MO': [],'MP': [],'MS': [],'MT': [],'NC': [],'ND': [],'NE': [],'NH': [],'NJ': [],'NM': [],'NV': [],'NY': [],'OH': [],'OK': [],'OR': [],'PA': [],'PR': [],'RI': [],'SC': [],'SD': [],'TN': [],'TX': [],'UT': [],'VA': [],'VI': [],'VT': [],'WA': [],'WI': [],'WV': [],'WY': []}

def main():
	output=open("CovidTrackingProject.csv","w+")
	output.write("fips,date,state,county,cases,deaths\n")

	page = requests.get('https://covidtracking.com/api/v1/states/daily.json')
	content = str(page.content)
	current = 0
	datePlace = content.find('date"',current)
	while datePlace != -1:
		#print(datePlace)
		dateBad = content[datePlace+6 : datePlace+14]
		date = dateBad[:4] + "-" + dateBad[4:6] + "-" + dateBad[6:8]
		stateBad = content[datePlace+24 : datePlace+26]
		state = states[stateBad]
		cases = content[datePlace+39 : content.find(',"',datePlace+39)]
		startD = content.find('death',datePlace+39)+7
		endD = content.find(',"',startD)
		deaths = content[startD : content.find(',"',startD)]
		if deaths == 'null':
			deaths='0'
		build="00000,"+date+","+state+","+"n/a,"+cases+","+deaths+"\n"
		final[stateBad].append(build)
		#print(build)
		datePlace = content.find('date"',datePlace+1)

	for a in final:
		list.sort(final[a])
		for b in final[a]:
			output.write(b)

if __name__ == "__main__":
	main()
