# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

import os
import random
import math
import json
import dateutil.parser
import glob
from datetime import datetime

log = ""
jsondata = {}
jsondata['candidate'] = []
charlimit = 100
#e = 7.14285; #0.14 <- 85% of success
e = 2.71828; #0.37 <- less than 50% of success


#=======================
# ----  index page ----
#=======================
def index():
    return main()


def main():
    global log

    visitordata = loadJSON("private/secretary_problem/visitordata.json")
    visitorSelection = matching(visitordata)
    log += "<br/>--------------<br/>"

    eventdata = loadJSON("private/secretary_problem/eventdata.json")
    eventSelection = matching(eventdata)
    log += "<br/>--------------<br/>"

    coachdata = loadJSON("private/secretary_problem/coachdata.json")
    coachSelection = matching(coachdata)

    print ("================\nVisitor: {} <--{}--> Coach: {}".format(visitorSelection, eventSelection ,coachSelection))

    return dict(
                message=T('Event Matching'),
                visitorSelectionOut=visitorSelection,
                eventSelectionOut=eventSelection,
                cardOut=eventSelection,
                coachSelectionOut=coachSelection,
                logOut=log,

                coachCardOut=coachSelection
            )


# ---- Matching main call for index ----
def matching(dataObj):
    data = dataObj['candidate']
    dataTarget = dataObj['target']

    global log
    global charlimit

    candidateNum=len(data)
    candidateRank = list()
    candidateList = list()
    rcmdCandidateList = list()

    for i in range(candidateNum):
        #TODO: ranking is still random. Need to get rank from *.json files.
        candidateRank.append(random.randint(1,candidateNum))
        #candidateList.append(i+1)
        candidateList.append(data[i]["firstName"])

    print("Candidate:  {}\nTotal Rank: {}\n".format(candidateList, candidateRank))
    log += "<br/>Candidate:  {}<br/>Total Rank: {}<br/>".format(candidateList, candidateRank)

    samplesize = int(round(candidateNum / e))
    print ("Matching success rate is " + str(candidateNum / e))
    log += "<br/>Matching success rate is " + str(candidateNum / e)
    print ("sample size is " + str(samplesize))
    log += "<br/>sample size is " + str(samplesize)

    sample = candidateRank[ : samplesize]
    benchmark = int(max(sample))
    print ("maximum of the sample is " + str(benchmark))
    log += "<br/>maximum of the sample is " + str(benchmark)

    best = 1
    while samplesize <= len(candidateRank)-1:
        if candidateRank[samplesize] >= benchmark:
            best = samplesize
            break
        samplesize += 1

    if candidateRank[best] >= benchmark:
        bestCandidate=data[best]["firstName"]

        bestCandidateDic = buildOutput(data, best, dataTarget)

        print ("\nBest candidateRank found is " + bestCandidate + " with talent " + str(candidateRank[best]))
        log += "<br/>Best candidateRank found is " + bestCandidate + " with talent " + str(candidateRank[best])
        rcmdCandidate = sortingRecommand(data, data[best])

        print ">>>=====>>>" + str(rcmdCandidate)
        for n in range(len(rcmdCandidate)):
            rcmdCandidateList.append(buildOutput(rcmdCandidate, n, dataTarget))

        print ">>>==rcmdCandidateList===>>>" + str(rcmdCandidateList)
        return dict( bestCandidateOut=bestCandidateDic, rcmdCandidateOut=rcmdCandidateList )
    else:
        #print ("Could not find a best candidate, decreasing the best score.")
        #This is the failure case of Secretry Problem Algo.
        #Lets decrease samplesize until we find avaliable candidate.
        for i in range(samplesize):
            print(i)
            if candidateRank[i] == benchmark:
                #bestCandidate = data[i]["firstName"]

                bestCandidateDic = buildOutput(data, i, dataTarget)

                rcmdCandidate = sortingRecommand(data, data[i])

                print ">>>=====>>>" + str(rcmdCandidate)
                for n in range(len(rcmdCandidate)):
                    rcmdCandidateList.append(buildOutput(rcmdCandidate, n, dataTarget))

                print ">>>==rcmdCandidateList===>>>" + str(rcmdCandidateList)
                return dict( bestCandidateOut=bestCandidateDic, rcmdCandidateOut=rcmdCandidateList )


# ---- build output dic -----
def buildOutput(data, i, dataTarget):

    # we need this, since eventdata.json and visitordata/coachdata.json are diff
    try:
        bestCandidateId = data[i]["id"]
    except:
        bestCandidateId = ''


    bestCandidateIndex = data[i]["index"]
    bestCandidateName = data[i]["firstName"]
    bestCandidateRank = data[i]["rank"]


    if bestCandidateId != '':
        #load raw event json file from event id info
        if dataTarget == 'event':
            bestCandidateRaw = loadJSON("private/event_raw_data/event_"+ str(bestCandidateIndex) +"_"+ str(bestCandidateId) +".json")
        elif dataTarget == 'coach':
            bestCandidateRaw = loadJSON("private/coach_raw_data/coach_"+ str(bestCandidateIndex) +"_"+ str(bestCandidateId) +".json")
        elif dataTarget == 'visitor':
            bestCandidateRaw = loadJSON("private/event_raw_data/event_"+ str(bestCandidateIndex) +"_"+ str(bestCandidateId) +".json")

        bestCandidateImg = bestCandidateRaw['logo']['url'].encode('utf-8')
        bestCandidateDesRaw = bestCandidateRaw['description']['text'].encode('utf-8').strip()
        bestCandidateDes = (bestCandidateDesRaw[:charlimit] + '..') if len(bestCandidateDesRaw) > charlimit else bestCandidateDesRaw
        bestCandidateUrl = bestCandidateRaw['url'].encode('utf-8').strip()
    else:
        bestCandidateImg = ''
        bestCandidateDes = ''
        bestCandidateUrl = ''

    dic = {
            "bestCandidateIndex": str(bestCandidateIndex),
            "bestCandidateName":str(bestCandidateName),
            "bestCandidateRank": str(bestCandidateRank),
            "bestCandidateImg": bestCandidateImg,
            "bestCandidateDes":bestCandidateDes,
            "bestCandidateUrl":bestCandidateUrl
          }

    return dic


# ---- Load JSON file for human target data ----
def loadJSON(jsonfilename):
    with open(jsonfilename, "r") as json_data:
        return json.load(json_data)


# ---- Sorting based recommandation ----
def sortingRecommand(data, bestCandidateIdx):
    global log

    recommandList = list()
    candidateNum=len(data)
    candidateList = list()

    for i in range(candidateNum):
        if bestCandidateIdx != data[i]:
            candidateList.append(data[i])

    candidateList.sort(reverse=True, key=sortRank)
    log += "Sorted candidateList:" + str(candidateList)

    return candidateList


# ---- sorting callback function ----
def sortRank(elem):
    return elem['rank']


# ---- Get main iamge from event id ----
def getImageFromEventId(eventid):
    #get event id at first
    return ''



#=======================
# ----  coach page ----
#=======================
def coach():
    global log

    visitordata = loadJSON("private/secretary_problem/visitordata.json")
    visitorSelection = matching(visitordata)
    log += "<br/>--------------<br/>"

    coachdata = loadJSON("private/secretary_problem/coachdata.json")
    coachSelection = matching(coachdata)

    return dict(
                message=T('Coach To Visitor Matching and Scoring'),
                visitorSelectionOut=visitorSelection,
                coachSelectionOut=coachSelection,
                cardOut=coachSelection,
                logOut=log
            )



#=======================
# ----  score page ----
#=======================
def score():
    global log

    scoring()

    return dict(
                message=T('Calculating score of Event and Visitor'),
                logOut=log
            )


def writeJSON(jsondata,jsonfilename):
    with open(jsonfilename, "w") as outfile:
        json.dump(jsondata, outfile)


def getLocationScore(eventdata,userdata):
    global log

    log += "</br>" + eventdata['latitude']
    log += "</br>" + eventdata['longitude']
    ## TODO:
    #location distance calcuation needs here,
    #for prototype, I just give random score
    return random.randint(1,5)


def getDataRangeScore(eventdata,userdata):
    global log
    #you need to install - pip install python-dateutil
    #Eventbrite API's date format is IOS-8601(UTC), and
    #python-dateutil will convets it.
    #eventStartDate = dateutil.parser.parse(eventdata['start'])
    eventStartDate = dateutil.parser.parse(eventdata['start']['local'])
    log += "</br>" + str(eventStartDate)
    #eventStripTime = datetime.strptime(eventStartDate, "%b %d %H:%M:%S %Y")
    #print(eventStripTime)
    userBookingDate = dateutil.parser.parse(userdata['start'])
    log += "</br>" + str(userBookingDate)
    #same day = 4, one day off = 3, two day off = 2, three days off = 1, over four days = 0
    #print("{0} <-> {1}".format(eventStartDate, userBookingDate))
    difference = eventStartDate - userBookingDate
    log += "</br> difference days: " + str(difference.days)

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
    global log

    interestScore = 0

    mainCat = eventdata['categories']
    subCat = eventdata['subcategories']

    log += "</br>" + str(userdata)

    interestNum = len(userdata)
    interestList = list()
    for i in range(interestNum):
        interestList.append(userdata[i])
        if(userdata[i]['category'] == mainCat or userdata[i]['category'] == subCat):
            interestScore = interestScore + userdata[i]['rank']

    return interestScore


def getPricevalueScore(eventdata,userdata):
    global log

    log += "</br>getPricevalueScore is not integrated, since fixed_rate is not done in api aggregation."
    return random.randint(1,5)


def getNamne(eventdata):
    ## TODO: make human readable name
    return eventdata


# 1. load all event json files(events/event_xx.json).
# 2. score the categories and make rank
# 3. save scoring data to eventdata.json
def process(eventLoad):
    global log
    global jsondata

    eventData = eventLoad['score_category']
    userLoad = loadJSON("private/secretary_problem/score/visitor_scorecard.json")
    userData = userLoad['score_category']

    #get event name
    eventIdx = eventLoad['index']
    log += "</br>" + "<b>index:</b> " + str(eventIdx)

    eventId = eventLoad['id']
    log += "</br>" + "<b>id:</b> " + str(eventId)

    #get event name
    eventName = getNamne(eventLoad['name'])
    log += "</br>" + "<b>firstName:</b> " + str(eventName)

    #get score of distance between human target & event
    locationScore = getLocationScore(eventData['location'], userData['location'])
    log += "</br>" + "<b>locationScore:</b> " + str(locationScore)

    #get score of data range between human target and event
    dateScore = getDataRangeScore(eventData['date'], userData['date'])
    log += "</br>" + "<b>dateScore:</b> " + str(dateScore)

    interestScore = getInterestScore(eventData['interest'], userData['interest'])
    log += "</br>" + "<b>interestScore:</b> " + str(interestScore)

    pricevalueScore = getPricevalueScore(eventData['fee_rates'], userData['fee_rates'])
    log += "</br>" + "<b>priceScore:</b> " + str(pricevalueScore)

    rank = locationScore + dateScore + interestScore + pricevalueScore
    log += "</br>" + "<b>rank:</b> " + str(rank)

    jsondata['candidate'].append({
        "index": str(eventIdx),
        "id": str(eventId),
        "firstName": str(eventName),
        "locationScore": str(locationScore),
        "dateScore": str(dateScore),
        "interestScore": str(interestScore),
        "priceScore": str(pricevalueScore),
        "rank": str(rank)
    })

    jsonfilename = 'private/secretary_problem/eventdata.json'
    writeJSON(jsondata, jsonfilename)


def scoring():
    global log
    global jsondata

    for filename in glob.glob('private/secretary_problem/score/events/event_*.json'):
        log += "</br>" + str(filename)
        eventLoad = loadJSON(filename)
        process(eventLoad)

    #this is place to add target for event
    jsonfilename = 'private/secretary_problem/eventdata.json'
    jsondata = loadJSON(jsonfilename)
    jsondata['target'] = "event"
    writeJSON(jsondata, jsonfilename)



#=======================
# ---  interest page ---
#=======================
#https://fontawesome.com/v4.7.0/icon/coffee
def interest():
    global log

    data = {
            "interests" :
                        [
                            {"item": "Music", "index":"0", "id":"0", "img":"fa fa-music"},
                            {"item": "Art", "index":"1", "id":"1", "img":"fa fa-picture-o"},
                            {"item": "Food & Drink", "index":"2", "id":"2", "img":"fa fa-coffee"}
                        ]
            }

    visitordata = loadJSON("private/secretary_problem/visitordata.json")
    visitorSelection = matching(visitordata)
    log += "<br/>--------------<br/>"

    eventdata = loadJSON("private/secretary_problem/eventdata.json")
    eventSelection = matching(eventdata)
    log += "<br/>--------------<br/>"

    return dict(
                message=T('Interests'),
                cardOut=data['interests'],
                logOut=log
            )



#=======================
# -- voice into page --
#=======================
def voice_intro():
    global log

    return dict(
                message=T('Voice Introduction'),
                logOut=log
            )
