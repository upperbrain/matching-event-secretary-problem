import json
#pip install python-dateutil
import dateutil.parser
import random
import glob
from datetime import datetime


jsondata = {}
jsondata['candidate'] = []

'''
Load JSON file
'''
def loadJSON(jsonfilename):
    with open(jsonfilename, "r") as json_data:
        return json.load(json_data)


def writeJSON(jsondata,jsonfilename):
    with open(jsonfilename, "w") as outfile:
        json.dump(jsondata, outfile)


def getLocationScore(eventdata,userdata):
	print(eventdata['latitude'])
	print(eventdata['longitude'])
	#location distance calcuation needs here,
	#for prototype, I just give random score
	return random.randint(1,5)


def getDataRangeScore(eventdata,userdata):
	#you need to install - pip install python-dateutil 
	#Eventbrite API's date format is IOS-8601(UTC), and
	#python-dateutil will convets it.
	eventStartDate = dateutil.parser.parse(eventdata['start'])
	print(eventStartDate)
	#eventStripTime = datetime.strptime(eventStartDate, "%b %d %H:%M:%S %Y")
	#print(eventStripTime)
	userBookingDate = dateutil.parser.parse(userdata['start'])
	print(userBookingDate)
	#same day = 4, one day off = 3, two day off = 2, three days off = 1, over four days = 0
	difference = eventStartDate - userBookingDate
	print(difference.days)
	if (difference.days == 0):
		#print("score: 4")
		dateScore = 4
	elif (difference.days == 3):
		#print("score: 3")
		dateScore = 3
	elif (difference.days == 2):
		#print("score: 2")
		dateScore = 2
	elif (difference.days == 1):
		#print("score: 1")
		dateScore = 1
	else:
		#print("score: 0")
		dateScore = 0

	return dateScore;



def getInterestScore(eventdata,userdata):
	interestScore = 0

	mainCat = eventdata['categories']
	subCat = eventdata['subcategories']

	print(userdata)
	interestNum = len(userdata)
	interestList = list()
	for i in range(interestNum):
		interestList.append(userdata[i])
		if(userdata[i]['category'] == mainCat or userdata[i]['category'] == subCat):
			interestScore = interestScore + userdata[i]['rank']

	return interestScore



def getPricevalueScore(eventdata,userdata):
	print(eventdata['fixed']['major_value'])
	print(eventdata['maximum']['major_value'])
	print(eventdata['minimum']['major_value'])
	return random.randint(1,5)



def getNamne(eventdata):
	#print(eventdata)
	return eventdata

def getIndex(eventdata):
	#print(eventdata)
	return eventdata


def process(eventLoad):
	eventData = eventLoad['score_category']
	#print(eventScores)
	userLoad = loadJSON("visitor_scorecard.json")
	userData = userLoad['score_category']
	
	#get event name
	eventIdx = getIndex(eventLoad['index'])
	print("index: " + str(eventIdx) + "\n-----------\n")

	#get event name
	eventName = getNamne(eventLoad['name'])
	print("firstName: " + str(eventName) + "\n-----------\n")

	#get score of distance between human target & event
	locationScore = getLocationScore(eventData['location'], userData['location'])
	print("locationScore: " + str(locationScore) + "\n-----------\n")

	#get score of data range between human target and event
	dateScore = getDataRangeScore(eventData['date'], userData['date'])
	print("dateScore: " + str(dateScore) + "\n-----------\n")

	interestScore = getInterestScore(eventData['interest'], userData['interest'])
	print("interestScore: " + str(interestScore) + "\n-----------\n")

	pricevalueScore = getPricevalueScore(eventData['fee_rates'], userData['fee_rates'])
	print("priceScore: " + str(pricevalueScore) + "\n-----------\n")

	rank = locationScore + dateScore + interestScore + pricevalueScore

	global jsondata
	
	jsondata['candidate'].append({  
	    "index": str(eventIdx),
	    "firstName": str(eventName),
	    "locationScore": str(locationScore),
	    "dateScore": str(dateScore),
	    "interestScore": str(interestScore),
	    "priceScore": str(pricevalueScore),
	    "rank": str(rank)
	})

	jsonfilename = 'eventdata_killme.json'

	writeJSON(jsondata, jsonfilename)



def scoring():
	for filename in glob.glob('events/event_*.json'):
		print filename
		eventLoad = loadJSON(filename)
		process(eventLoad)




scoring()
