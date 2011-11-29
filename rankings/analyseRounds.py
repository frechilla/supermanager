#!/usr/bin/python

import sys
import os
import re
import urllib
from HTMLParser import HTMLParser
from HTMLParser import HTMLParseError
from math import sqrt, pow

# common smanager tools
import common

# rounds set up
from rounds import *

# lists called round[0-9]+ are defined in 'rounds.py'
allRounds = (
round1,
round2,
round3,
round4,
round5,
round6,
round7,
round8,
round9,
round10)

# playersDict loaded from the players-long-file
playersDict = {}


class RoundHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.scriptTagOn = False
        self.teamHome = ""
        self.teamAway = ""
        self.trClass  = ""
        self.tdClass  = ""
        self.tdTagCount = 0
        self.currentPlayerID = ""
        self.currentPlayerVal = 99999
        self.valAway = {'b':0, 'e':0, 'a':0, 'p':0}
        self.valHome = {'b':0, 'e':0, 'a':0, 'p':0}

    def handle_starttag(self, tag, attrs):
        # attrs is a list of tuples (pairs)
        if (tag == "script"):
            self.scriptTagOn = True
            self.tdCount = 0

        elif (tag == "tr"):
            # new row. initialised col count
            self.tdTagCount = 0
            for elem in attrs:
                if elem[0] == 'class':
                    self.trClass = elem[1]
                    break
            else:
                self.trClass = ""

        elif (tag == "td"):
            self.tdTagCount = self.tdTagCount + 1
            for elem in attrs:
                if elem[0] == "class":
                    self.tdClass = elem[1]
                    break
            else:
                self.tdClass = ""

        elif (tag == "a"):
            if (self.tdClass == "naranjaclaro"):
                for elem in attrs:
                    if elem[0] == "href":
                        self.currentPlayerID = elem[1][elem[1].index('id=')+3:]
                        self.currentPlayerVal = 99999 # new player
                        break
                else:
                    print "Error: Player's id could not be retrieved"
                    pass
            

    def handle_endtag(self, tag):
        if (tag == "tr"):
            self.trClass = ""
            self.tdTagCount = 0
            self.currentPlayerVal = 99999
            self.currentPlayerID = ""
        elif (tag == "td"):
            if (self.currentPlayerID != "" ) and (self.trClass == "") and (self.tdClass == "blanco") and (self.tdTagCount == 22):
                if (self.currentPlayerVal == 99999):
                    self.currentPlayerVal = 0
                if (not playersDict.has_key(self.currentPlayerID)):
                    playerName = "UNKNOWN"
                    (playerPos, playerHeight) = common.GetPlayersPosAndHeightFromInternet(self.currentPlayerID)
                    if ((playerPos == "") or (playerHeight == "")):
                        print "Error retrieving player position from ACB web site"
                    elif (playerPos == "b"):
                        playersDict[self.currentPlayerID] = {'pos':"b", 'acb_pos':playerPos, 'height':playerHeight, 'name': playerName}
                    elif (playerPos == "a") or (playerPos == "e"):
                        playersDict[self.currentPlayerID] = {'pos':"a", 'acb_pos':playerPos, 'height':playerHeight, 'name': playerName}
                    else:
                        playersDict[self.currentPlayerID] = {'pos':"p", 'acb_pos':playerPos, 'height':playerHeight, 'name': playerName}

                if (playersDict.has_key(self.currentPlayerID)):
                    if (self.teamHome != "") and (self.teamAway == ""):
                        destinationDict = self.valHome
                    elif (self.teamHome != "") and (self.teamAway != ""):
                        destinationDict = self.valAway
                    else:
                        print "No team selected!"
                        self.tdClass = ""
                        return
                    
                    if (playersDict[self.currentPlayerID]['pos'] == "b"): # supermanager b's are taken as truth
                        destinationDict['b'] = destinationDict['b'] + self.currentPlayerVal
                    elif (playersDict[self.currentPlayerID]['acb_pos'] == "e") or \
                         (playersDict[self.currentPlayerID]['acb_pos'] == "b" and playersDict[self.currentPlayerID]['pos'] == "a"):
                        destinationDict['e'] = destinationDict['e'] + self.currentPlayerVal
                    elif (playersDict[self.currentPlayerID]['acb_pos'] == "a"):
                        destinationDict['a'] = destinationDict['a'] + self.currentPlayerVal
                    elif (playersDict[self.currentPlayerID]['acb_pos'] == "p") or (playersDict[self.currentPlayerID]['acb_pos'] == "f"):
                        destinationDict['p'] = destinationDict['p'] + self.currentPlayerVal
                    else:
                        print "Unhandled player position %s for %s" % \
                              (playersDict[self.currentPlayerID]['acb_pos'], playersDict[self.currentPlayerID]['name'])
                    
                else:
                    print "Don't know what position this guy is!"
                

#                print "%s - %s -> %s: %d" % (playersDict[self.currentPlayerID]['pos'], playersDict[self.currentPlayerID]['acb_pos'], playersDict[self.currentPlayerID]['name'], self.currentPlayerVal)
            self.tdClass = ""


    def handle_data(self, data):
        data  = data.rstrip()

        if (data != "") and (self.trClass == "estverde") and (self.tdClass == "estverdel"):
            # this is the current team
            m = re.search('([\D]*)[\d]+', data)
            if (m != None):
                teamName = m.groups(0)[0].rstrip()
            else:
                teamName = "UNKNOWN"
            
            if (self.teamHome == ""):
                self.teamHome = teamName
            elif (self.teamAway == ""):
                self.teamAway = teamName
            else:
                print "Fatal error parsing: Team name was found, but home and away team have been already set"
                print "Offending team name: \"%s\"" % teamName

        elif (self.trClass == "") and (self.tdClass == "blanco") and (self.tdTagCount == 22):
            try:
                self.currentPlayerVal = int(data)
            except ValueError:
                print "Fatal error parsing. Val could not be converted into integer for %s" % (self.currentPlayerID)


def DictToHTMLTableLong(averageDict, sigmaDict):
    """ returns a string with a HTML table with val per team splitted up by b/e/a/p
    """
    rv = ""
    rv += '<TABLE border="1" class="sortable" width="1065" style=\'table-layout:fixed\'>' + '\n'
    rv += '<col width="275">' + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="50">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="50">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="50">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="50">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="50">'  + '\n'
    rv += "<tr>"              + '\n'
    rv += "<th>equipo</th>"   + '\n'
    rv += "<th align=\"center\">total</th>"    + '\n'
    rv += "<th>&delta;</th>"  + '\n'
    rv += "<th align=\"center\">1</th>"        + '\n'
    rv += "<th>&sigmaf;</th>" + '\n'
    rv += "<th>&#37;</th>"    + '\n'
    rv += "<th>&delta;</th>"  + '\n'
    rv += "<th align=\"center\">2</th>"        + '\n'
    rv += "<th>&sigmaf;</th>" + '\n'
    rv += "<th>&#37;</th>"    + '\n'
    rv += "<th>&delta;</th>"  + '\n'
    rv += "<th align=\"center\">3</th>"        + '\n'
    rv += "<th>&sigmaf;</th>" + '\n'
    rv += "<th>&#37;</th>"    + '\n'
    rv += "<th>&delta;</th>"  + '\n'
    rv += "<th align=\"center\">4-5</th>"      + '\n'
    rv += "<th>&sigmaf;</th>" + '\n'
    rv += "<th>&#37;</th>"    + '\n'
    rv += "<th>&delta;</th>"  + '\n'
    rv += "</tr>"             + '\n'
    
    # delta calculation
    nteams = 0
    b_mean = 0
    e_mean = 0
    a_mean = 0
    p_mean = 0
    for team in averageDict:
        nteams += 1        
        b_mean += averageDict[team]['b']
        e_mean += averageDict[team]['e']
        a_mean += averageDict[team]['a']
        p_mean += averageDict[team]['p']
    
    b_mean = float(b_mean) / nteams
    e_mean = float(e_mean) / nteams
    a_mean = float(a_mean) / nteams
    p_mean = float(p_mean) / nteams
    
    currentCol = 0
    for team in averageDict:
        currentCol += 1
        if (currentCol % 2 == 0):
            rv += '<tr class="even">'   + '\n'
        else:
            rv += '<tr class="odd">'    + '\n'
            
        rv += "  <td>" + team + "</td>" + '\n'
        addition = averageDict[team]['b'] + \
                   averageDict[team]['e'] + \
                   averageDict[team]['a'] + \
                   averageDict[team]['p']
        
        # total
        rv += "  <td>" + str(round(addition, 2)) + "</td>" + '\n'
        rv += "  <td class=\"delta\">"
        if (addition > (b_mean + e_mean + a_mean + p_mean)):
            rv += "+"
        rv += str(round(addition - (b_mean + e_mean + a_mean + p_mean), 2)) + "</td>" + '\n'   
        
        # 1
        rv += "  <td>" + str(round(averageDict[team]['b'], 2)) + "</td>" + '\n'
        rv += "  <td>" + str(round(sigmaDict[team]['b'], 2)) + "</td>"   + '\n'
        percentage = float(averageDict[team]['b']) * float(100 / addition)
        rv += "  <td class=\"percentage\">" + str(round(percentage, 2)) + "</td>" + '\n'   
        rv += "  <td class=\"delta\">"
        if (averageDict[team]['b'] > b_mean):
            rv += "+"
        rv += str(round(averageDict[team]['b'] - b_mean, 2)) + "</td>" + '\n'
        
        # 2
        rv += "  <td>" + str(round(averageDict[team]['e'], 2)) + "</td>" + '\n'
        rv += "  <td>" + str(round(sigmaDict[team]['e'], 2)) + "</td>"   + '\n' 
        percentage = float(averageDict[team]['e']) * float(100 / addition)
        rv += "  <td class=\"percentage\">" + str(round(percentage, 2)) + "</td>" + '\n'   
        rv += "  <td class=\"delta\">"
        if (averageDict[team]['e'] > e_mean):
            rv += "+"
        rv += str(round(averageDict[team]['e'] - e_mean, 2)) + "</td>" + '\n'
        
        # 3
        rv += "  <td>" + str(round(averageDict[team]['a'], 2)) + "</td>" + '\n'
        rv += "  <td>" + str(round(sigmaDict[team]['a'], 2)) + "</td>"   + '\n'
        percentage = float(averageDict[team]['a']) * float(100 / addition)
        rv += "  <td class=\"percentage\">" + str(round(percentage, 2)) + "</td>" + '\n'   
        rv += "  <td class=\"delta\">"
        if (averageDict[team]['a'] > a_mean):
            rv += "+"
        rv += str(round(averageDict[team]['a'] - a_mean, 2)) + "</td>" + '\n'
        
        # 4-5
        rv += "  <td>" + str(round(averageDict[team]['p'], 2)) + "</td>" + '\n'
        rv += "  <td>" + str(round(sigmaDict[team]['p'], 2)) + "</td>"   + '\n'
        percentage = float(averageDict[team]['p']) * float(100 / addition)
        rv += "  <td class=\"percentage\">" + str(round(percentage, 2)) + "</td>" + '\n'   
        rv += "  <td class=\"delta\">"
        if (averageDict[team]['p'] > p_mean):
            rv += "+"
        rv += str(round(averageDict[team]['p'] - p_mean, 2)) + "</td>" + '\n'
        
        rv += "</tr>"  + '\n'
    rv += '</TABLE>' + '\n'
    return rv

def DictToHTMLTable(averageDict, sigmaDict):
    """ returns a string with a HTML table with val per team splitted up by b/a/p
        Same as DictToHTMLTableLong but e/a are merged together in a single column
    """
    rv = ""
    rv += '<TABLE border="1" class="sortable" width="925" style=\'table-layout:fixed\'>' + '\n'
    rv += '<col width="275">' + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="50">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="50">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="50">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="45">'  + '\n'
    rv += '<col width="50">'  + '\n'
    rv += "<tr>"              + '\n'
    rv += "<th>equipo</th>"   + '\n'
    rv += "<th align=\"center\">total</th>"    + '\n'
    rv += "<th>&delta;</th>"  + '\n'
    rv += "<th align=\"center\">1</th>"        + '\n'
    rv += "<th>&sigmaf;</th>" + '\n'
    rv += "<th>&#37;</th>"    + '\n'
    rv += "<th>&delta;</th>"  + '\n'
    rv += "<th align=\"center\">2-3</th>"      + '\n'
    rv += "<th>&sigmaf;</th>" + '\n'
    rv += "<th>&#37;</th>"    + '\n'
    rv += "<th>&delta;</th>"  + '\n'
    rv += "<th align=\"center\">4-5   </th>"   + '\n'
    rv += "<th>&sigmaf;</th>" + '\n'
    rv += "<th>&#37;</th>"    + '\n'
    rv += "<th>&delta;</th>"  + '\n'
    rv += "</tr>"             + '\n'
    
    # delta calculation
    nteams = 0
    b_mean = 0
    e_mean = 0
    a_mean = 0
    p_mean = 0
    for team in averageDict:
        nteams += 1        
        b_mean += averageDict[team]['b']
        e_mean += averageDict[team]['e']
        a_mean += averageDict[team]['a']
        p_mean += averageDict[team]['p']
    
    b_mean = float(b_mean) / nteams
    e_mean = float(e_mean) / nteams
    a_mean = float(a_mean) / nteams
    p_mean = float(p_mean) / nteams
    
    currentCol = 0
    for team in averageDict:
        currentCol += 1
        if (currentCol % 2 == 0):
            rv += '<tr class="even">'   + '\n'
        else:
            rv += '<tr class="odd">'    + '\n'
            
        rv += "  <td>" + team + "</td>" + '\n'
        addition = averageDict[team]['b'] + \
                   averageDict[team]['e'] + \
                   averageDict[team]['a'] + \
                   averageDict[team]['p']

        # total
        rv += "  <td>" + str(round(addition, 2)) + "</td>" + '\n'
        rv += "  <td class=\"delta\">"
        if (addition > (b_mean + e_mean + a_mean + p_mean)):
            rv += "+"
        rv += str(round(addition - (b_mean + e_mean + a_mean + p_mean), 2)) + "</td>" + '\n'     
        
        # 1
        rv += "  <td>" + str(round(averageDict[team]['b'], 2)) + "</td>" + '\n'
        rv += "  <td>" + str(round(sigmaDict[team]['b'], 2)) + "</td>"   + '\n'
        percentage = float(averageDict[team]['b']) * float(100 / addition)
        rv += "  <td class=\"percentage\">" + str(round(percentage, 2)) + "</td>" + '\n'        
        rv += "  <td class=\"delta\">"
        if (averageDict[team]['b'] > b_mean):
            rv += "+"
        rv += str(round(averageDict[team]['b'] - b_mean, 2)) + "</td>" + '\n'
        
        # 2-3
        rv += "  <td>" + str(round(averageDict[team]['ea'], 2)) + "</td>" + '\n'
        rv += "  <td>" + str(round(sigmaDict[team]['ea'], 2)) + "</td>"   + '\n'
        percentage = float(averageDict[team]['ea']) * float(100 / addition)
        rv += "  <td class=\"percentage\">" + str(round(percentage, 2)) + "</td>" + '\n'        
        rv += "  <td class=\"delta\">"
        if (averageDict[team]['ea'] > (e_mean + a_mean)):
            rv += "+"
        rv += str(round(averageDict[team]['ea'] - (e_mean + a_mean), 2)) + "</td>" + '\n'
        
        #4-5
        rv += "  <td>" + str(round(averageDict[team]['p'], 2)) + "</td>" + '\n'
        rv += "  <td>" + str(round(sigmaDict[team]['p'], 2)) + "</td>"   + '\n'
        percentage = float(averageDict[team]['p']) * float(100 / addition)
        rv += "  <td class=\"percentage\">" + str(round(percentage, 2)) + "</td>" + '\n'  
        rv += "  <td class=\"delta\">"
        if (averageDict[team]['p'] > p_mean):
            rv += "+"
        rv += str(round(averageDict[team]['p'] - p_mean, 2)) + "</td>" + '\n'
        
        rv += "</tr>"  + '\n'
    rv += '</TABLE>' + '\n'
    return rv
    
########
# MAIN #

if len(sys.argv) != 3:
    print "usage: %s players-long-file output-html-file" % sys.argv[0]
    print "     : players-long-file  generated by mercadoparserToLong.py"
    print "     : output-html-file  where the output will be written. It will be replaced if it exists already"
    print "Prints a nice HTML file with the stats received per team per position"
    raise SystemExit

# first of all load the players-long-file contents into the global dictionary
common.LoadPlayerLongFile(playersDict, sys.argv[1])

# val dictionary
totalValDict = {}

roundNumber = 0
for thisRound in allRounds:
    roundNumber = roundNumber + 1
    for thisMatchURL in thisRound:
        print "Parsing %s..." % thisMatchURL

        theParser = RoundHTMLParser()
        f = urllib.urlopen(thisMatchURL)
        theParser.reset()
        for line in f.readlines():
            line = line.rstrip()

            if (theParser.scriptTagOn == False):
                try :
                    theParser.feed(line)
                except HTMLParseError, ex:
                    print "Exception: %s" % (ex.msg)
            else:
                if (line.find("</script>") != -1):
                    theParser.scriptTagOn = False

        f.close()
        
        # theParser conatinas all the info we need from this match
        if (not totalValDict.has_key(theParser.teamHome)):
            print "Initialising val dictionary for %s" % theParser.teamHome
            totalValDict[theParser.teamHome] = []
        if (not totalValDict.has_key(theParser.teamAway)):
            print "Initialising val dictionary for %s" % theParser.teamAway
            totalValDict[theParser.teamAway] = []

        totalValDict[theParser.teamHome].append({'b': theParser.valAway['b'], \
                                                 'e': theParser.valAway['e'], \
                                                 'a': theParser.valAway['a'], \
                                                 'p': theParser.valAway['p'], \
                                                 'where' : 'home',            \
                                                 'vs' : theParser.teamAway})
                                                 
        totalValDict[theParser.teamAway].append({'b': theParser.valHome['b'], \
                                                 'e': theParser.valHome['e'], \
                                                 'a': theParser.valHome['a'], \
                                                 'p': theParser.valHome['p'], \
                                                 'where' : 'away',            \
                                                 'vs' : theParser.teamHome})
        

"""
    print "=============="
    print "round %d" % (roundNumber)

    for teamItem in  totalValDict.items():
        key, data = teamItem
        print "%s playing %s %s: %d %d %d %d" % ( \
                    key, \
                    data[roundNumber - 1]['vs'], \
                    data[roundNumber - 1]['where'],\
                    data[roundNumber - 1]['b'], \
                    data[roundNumber - 1]['e'], \
                    data[roundNumber - 1]['a'], \
                    data[roundNumber - 1]['p'])
"""

# stats dictionaries
averageDict = {}
averageHomeDict  = {}
averageAwayDict  = {}
for teamItem in  totalValDict.items():
    teamname, data = teamItem
    if (not averageDict.has_key(teamname)):
        averageDict[teamname]      = {'b' : 0, 'e' : 0, 'a' : 0, 'p' : 0, 'ea' : 0}
        averageHomeDict[teamname]  = {'b' : 0, 'e' : 0, 'a' : 0, 'p' : 0, 'ea' : 0}
        averageAwayDict[teamname]  = {'b' : 0, 'e' : 0, 'a' : 0, 'p' : 0, 'ea' : 0}
    
    roundsTotal = 0
    roundsAway  = 0
    roundsHome  = 0
    for roundData in data:
        averageDict[teamname]['b'] += roundData['b']
        averageDict[teamname]['e'] += roundData['e']
        averageDict[teamname]['a'] += roundData['a']
        averageDict[teamname]['p'] += roundData['p']
        averageDict[teamname]['ea'] += roundData['e'] + roundData['a']
        roundsTotal = roundsTotal + 1
        
        if (roundData['where'] == 'away'):
            averageAwayDict[teamname]['b'] += roundData['b']
            averageAwayDict[teamname]['e'] += roundData['e']
            averageAwayDict[teamname]['a'] += roundData['a']
            averageAwayDict[teamname]['p'] += roundData['p']
            averageAwayDict[teamname]['ea'] += roundData['e'] + roundData['a']
            roundsAway = roundsAway + 1
        elif (roundData['where'] == 'home'):
            averageHomeDict[teamname]['b'] += roundData['b']
            averageHomeDict[teamname]['e'] += roundData['e']
            averageHomeDict[teamname]['a'] += roundData['a']
            averageHomeDict[teamname]['p'] += roundData['p']
            averageHomeDict[teamname]['ea'] += roundData['e'] + roundData['a']
            roundsHome = roundsHome + 1
        else:
            print "Error. this round wasn't played home or away"

            
    averageDict[teamname]['b'] = float(averageDict[teamname]['b']) / roundsTotal
    averageDict[teamname]['e'] = float(averageDict[teamname]['e']) / roundsTotal
    averageDict[teamname]['a'] = float(averageDict[teamname]['a']) / roundsTotal
    averageDict[teamname]['p'] = float(averageDict[teamname]['p']) / roundsTotal
    averageDict[teamname]['ea'] = float(averageDict[teamname]['ea']) / roundsTotal
    
    averageAwayDict[teamname]['b'] = float(averageAwayDict[teamname]['b']) / roundsAway
    averageAwayDict[teamname]['e'] = float(averageAwayDict[teamname]['e']) / roundsAway
    averageAwayDict[teamname]['a'] = float(averageAwayDict[teamname]['a']) / roundsAway
    averageAwayDict[teamname]['p'] = float(averageAwayDict[teamname]['p']) / roundsAway
    averageAwayDict[teamname]['ea'] = float(averageAwayDict[teamname]['ea']) / roundsAway
    
    averageHomeDict[teamname]['b'] = float(averageHomeDict[teamname]['b']) / roundsHome
    averageHomeDict[teamname]['e'] = float(averageHomeDict[teamname]['e']) / roundsHome
    averageHomeDict[teamname]['a'] = float(averageHomeDict[teamname]['a']) / roundsHome
    averageHomeDict[teamname]['p'] = float(averageHomeDict[teamname]['p']) / roundsHome
    averageHomeDict[teamname]['ea'] = float(averageHomeDict[teamname]['ea']) / roundsHome
    
    print "%s (h: %d a: %d)" % (teamname, roundsHome, roundsAway)
    print "  TOTAL: %g %g %g %g" % (averageDict[teamname]['b'], averageDict[teamname]['e'], averageDict[teamname]['a'], averageDict[teamname]['p'])
    print "  AWAY:  %g %g %g %g" % (averageAwayDict[teamname]['b'], averageAwayDict[teamname]['e'], averageAwayDict[teamname]['a'], averageAwayDict[teamname]['p'])
    print "  HOME:  %g %g %g %g" % (averageHomeDict[teamname]['b'], averageHomeDict[teamname]['e'], averageHomeDict[teamname]['a'], averageHomeDict[teamname]['p'])


# standard deviation calc
sigmaTotalDict = {}
sigmaHomeDict  = {}
sigmaAwayDict  = {}
for teamItem in  totalValDict.items():
    teamname, data = teamItem
    if (not sigmaTotalDict.has_key(teamname)):
        sigmaTotalDict[teamname] = {'b' : 0, 'e' : 0, 'a' : 0, 'p' : 0, 'ea' : 0}
        sigmaHomeDict[teamname]  = {'b' : 0, 'e' : 0, 'a' : 0, 'p' : 0, 'ea' : 0}
        sigmaAwayDict[teamname]  = {'b' : 0, 'e' : 0, 'a' : 0, 'p' : 0, 'ea' : 0}
    
    roundsTotal = 0
    roundsAway  = 0
    roundsHome  = 0
    for roundData in data:
        sigmaTotalDict[teamname]['b'] +=  pow(roundData['b'] - averageDict[teamname]['b'], 2.0)
        sigmaTotalDict[teamname]['e'] +=  pow(roundData['e'] - averageDict[teamname]['e'], 2.0)
        sigmaTotalDict[teamname]['a'] +=  pow(roundData['a'] - averageDict[teamname]['a'], 2.0)
        sigmaTotalDict[teamname]['p'] +=  pow(roundData['p'] - averageDict[teamname]['p'], 2.0)
        sigmaTotalDict[teamname]['ea'] += pow((roundData['e'] + roundData['a']) - averageDict[teamname]['ea'], 2.0)
        roundsTotal = roundsTotal + 1
        
        if (roundData['where'] == 'away'):
            sigmaAwayDict[teamname]['b'] += pow(roundData['b'] - averageAwayDict[teamname]['b'], 2.0)
            sigmaAwayDict[teamname]['e'] += pow(roundData['e'] - averageAwayDict[teamname]['e'], 2.0)
            sigmaAwayDict[teamname]['a'] += pow(roundData['a'] - averageAwayDict[teamname]['a'], 2.0)
            sigmaAwayDict[teamname]['p'] += pow(roundData['p'] - averageAwayDict[teamname]['p'], 2.0)
            sigmaAwayDict[teamname]['ea'] += pow((roundData['e'] + roundData['a']) - averageAwayDict[teamname]['ea'], 2.0)
            roundsAway = roundsAway + 1
        elif (roundData['where'] == 'home'):
            sigmaHomeDict[teamname]['b'] += pow(roundData['b'] - averageHomeDict[teamname]['b'], 2.0)
            sigmaHomeDict[teamname]['e'] += pow(roundData['e'] - averageHomeDict[teamname]['e'], 2.0)
            sigmaHomeDict[teamname]['a'] += pow(roundData['a'] - averageHomeDict[teamname]['a'], 2.0)
            sigmaHomeDict[teamname]['p'] += pow(roundData['p'] - averageHomeDict[teamname]['p'], 2.0)
            sigmaHomeDict[teamname]['ea'] += pow((roundData['e'] + roundData['a']) - averageHomeDict[teamname]['ea'], 2.0)
            roundsHome = roundsHome + 1
        else:
            print "Error. this round wasn't played home or away"

            
    sigmaTotalDict[teamname]['b'] = sqrt(float(sigmaTotalDict[teamname]['b']) / roundsTotal)
    sigmaTotalDict[teamname]['e'] = sqrt(float(sigmaTotalDict[teamname]['e']) / roundsTotal)
    sigmaTotalDict[teamname]['a'] = sqrt(float(sigmaTotalDict[teamname]['a']) / roundsTotal)
    sigmaTotalDict[teamname]['p'] = sqrt(float(sigmaTotalDict[teamname]['p']) / roundsTotal)
    sigmaTotalDict[teamname]['ea']= sqrt(float(sigmaTotalDict[teamname]['ea']) / roundsTotal)
    
    sigmaAwayDict[teamname]['b'] = sqrt(float(sigmaAwayDict[teamname]['b']) / roundsAway)
    sigmaAwayDict[teamname]['e'] = sqrt(float(sigmaAwayDict[teamname]['e']) / roundsAway)
    sigmaAwayDict[teamname]['a'] = sqrt(float(sigmaAwayDict[teamname]['a']) / roundsAway)
    sigmaAwayDict[teamname]['p'] = sqrt(float(sigmaAwayDict[teamname]['p']) / roundsAway)
    sigmaAwayDict[teamname]['ea']= sqrt(float(sigmaAwayDict[teamname]['ea']) / roundsAway)
    
    sigmaHomeDict[teamname]['b'] = sqrt(float(sigmaHomeDict[teamname]['b']) / roundsHome)
    sigmaHomeDict[teamname]['e'] = sqrt(float(sigmaHomeDict[teamname]['e']) / roundsHome)
    sigmaHomeDict[teamname]['a'] = sqrt(float(sigmaHomeDict[teamname]['a']) / roundsHome)
    sigmaHomeDict[teamname]['p'] = sqrt(float(sigmaHomeDict[teamname]['p']) / roundsHome)
    sigmaHomeDict[teamname]['ea']= sqrt(float(sigmaHomeDict[teamname]['ea']) / roundsHome)
    
    

# truncates the file if it exists
out = open (sys.argv[2], 'w')
print >>out, """<HTML>
  <HEAD>
    <script src="sorttable.js"></script>
    <TITLE>Valoraciones por posicion</TITLE>
    <style type="text/css">
th, td {'
  padding: 3px !important;
}

table.sortable td.delta {
    background-color: #eee;
}

/* Sortable tables */
table.sortable thead {
    background-color:#eee;
    color:#666666;
    font-weight: bold;
    cursor: default;
}
    </style>
  </HEAD>
  <BODY>    
"""

print >>out, '<H3>TOTAL</H3>'
print >>out, DictToHTMLTableLong(averageDict, sigmaTotalDict)
print >>out, '<br/>'
print >>out, DictToHTMLTable(averageDict, sigmaTotalDict)
print >>out, '<br/>'
print >>out, '<br/>'
print >>out, '<H3>HOME</H3>'
print >>out, DictToHTMLTableLong(averageHomeDict, sigmaHomeDict)
print >>out, '<br/>'
print >>out, DictToHTMLTable(averageHomeDict, sigmaHomeDict)
print >>out, '<br/>'
print >>out, '<br/>'
print >>out, '<H3>AWAY</H3>'
print >>out, DictToHTMLTableLong(averageAwayDict, sigmaAwayDict)
print >>out, '<br/>'
print >>out, DictToHTMLTable(averageAwayDict, sigmaAwayDict)
print >>out, '<br/>'

print >>out, """
    <p> Y ahora que he visto todo, &iquest;qu&eacute; cojones significa? Pues b&aacute;sicamente hay dos tablas para el total de los partidos, dos para los partidos en casa y dos para los de fuera. Los contenidos de las tablas son:
      <ul>
        <li>Primera tabla</li>
        <ul>
          <li><b>equipo</b>:   Adivina...</li>
          <li><b>total</b>:    Valoraci&oacute;n recibida total</li>
          <li><b>&delta;</b>:  Diferencia de la valoraci&oacute;n recibida total por este equipo menos la media de las valoraciones recibidas por TODOS LOS EQUIPOS. Si el valor es positivo este equipo recibe m&aacute;s que la media. Si es negativo el equipo recibe menos que la media</li>
          <li><b>1</b>:        Valoraci&oacute;n recibida de los bases </li>
          <li><b>&sigmaf;</b>: Desviaci&oacute;n t&iacute;pica de la valoraci&oacute;n recibida por los bases. Al que le interese, segun la <a href="http://es.wikipedia.org/wiki/Desviaci%C3%B3n_est%C3%A1ndar">estad&iacute;stica</a> hay un 68% de posibilidades de que en un partido al azar este equipo reciba entre [media - desviaci&oacute;n] y [media + desviaci&oacute;n] . Y hay un 95% de posibilidades de que el equipo reciba entre [media - (desviacion^2) ] y [media + (desviacion^2)]</li>
          <li><b>&#37;</b>:    Porcentaje de valoracion que este equipo recibe de los bases sobre el total de valoracion recibido por ESTE EQUIPO</li>
          <li><b>&delta;</b>:  Diferencia de la valoraci&oacute;n recibida por este equipo por los bases menos la media de las valoraciones recibidas de los bases por TODOS LOS EQUIPOS. Si el valor es positivo este equipo recibe m&aacute;s que la media en los bases. Si es negativo el equipo recibe menos que la media</li>
          <li><b>2</b>:        Valoraci&oacute;n recibida de los escoltas</li>
          <li><b>&sigmaf;</b> - <b>&#37;</b> - <b>&delta;</b>: Igual que en el caso de los bases, pero se aplica a los escoltas
          <li><b>3</b>:        Valoraci&oacute;n recibida de los aleros</li>
          <li><b>&sigmaf;</b> - <b>&#37;</b> - <b>&delta;</b>: Igual que en el caso de los bases, pero se aplica a los aleros
          <li><b>4-5</b>:      Valoraci&oacute;n recibida de los pivots</li>
          <li><b>&sigmaf;</b> - <b>&#37;</b> -  <b>&delta;</b>: Igual que en el caso de los bases, pero se aplica a los pivots
        </ul>
        <li>Segunda tabla</li>
        <ul>
           <li>Esta tabla es igual que la primera, pero tiene escoltas y aleros en la misma columna</li>
        </ul>
      </ul>
    </p>
  </BODY>
</HTML>"""

out.close()

