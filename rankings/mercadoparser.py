#!/usr/bin/python

import sys
import os
from HTMLParser import HTMLParser
from HTMLParser import HTMLParseError

class SMHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.scriptTagOn = False
        self.tdCount = 0

        self.__resetCurrentPlayer()
        self.nPlayers = 0

    def __resetCurrentPlayer(self):
        self.currentCOD  = ""
        self.currentName = ""
        self.currentPlayerStatsURL = ""
        self.currentPlayerURL = ""
        self.currentTeam = ""
        self.currentTeamRecord = ""
        self.currentAverage = -9999.99
        self.currentPrice = 0

    def __isCurrentPlayerSet(self):
        if (self.currentName == ""):
            return False
        if (self.currentTeam == ""):
            return False
        if (self.currentTeamRecord == ""):
            return False
        if (self.currentAverage == -9999.99):
            return False
        if (self.currentPrice == 0):
            return False

        return True

    def handle_starttag(self, tag, attrs):
        # attrs is a list of tuples (pairs)
	if (tag == "script"):
            self.scriptTagOn = True
        elif (tag == "tr"):
            self.tdCount = 0
	elif (tag == "td"):
            self.tdCount = self.tdCount + 1
        elif ((tag == "a") and (self.tdCount == 4)):
            for elem in attrs:
                if elem[0] == "href":
                    self.currentCOD = elem[1][elem[1].index('cod_jugador=')+12:]
                    self.currentPlayerStatsURL = elem[1]
                    self.currentPlayerURL = elem[1].replace("stspartidojug.php?cod_jugador", "jugador.php?id")
            

    def handle_endtag(self, tag):
        #print "Found the end of a %s tag" % tag
        if (self.__isCurrentPlayerSet()):
            print "%s:%s:%s" % (self.currentCOD, sys.argv[1], self.currentName)
            self.__resetCurrentPlayer()
	pass

    def handle_data(self, data):
        data = data.rstrip()
        if (data == ""):
            return

        if (self.tdCount == 4):
            self.currentName = data
        elif (self.tdCount == 6):
            self.currentTeam = data
        elif (self.tdCount == 7):
            self.currentTeamRecord = data
        elif (self.tdCount == 8):
            try:
                self.currentAverage = float(data.replace(",", "."))
            except ValueError:
                self.__resetCurrentPlayer()
                tdCount = 0
        elif (self.tdCount == 9):
            try:
                self.currentPrice = int(data.replace(".", ""))
            except ValueError:
                self.__resetCurrentPlayer()
                tdCount = 0
   

#########################
# PROCESS FILE FUNCTION #
def processHTMLFile(file):
    if not os.path.isfile(file):
        print file + " is not a file"
        return
    
    theParser = SMHTMLParser()
    # read the whole file into the buffer
    # we dont want to parse the file all at once since exceptions cant be 
    # handled in that way
    #fileBuffer = open(file, 'rU').read()
    # process it
    #theParser.feed(fileBuffer)

    file = open(elem, 'r')
    lineNumber = 0
    for line in file:
        lineNumber = lineNumber + 1

        line = line.rstrip() # remove \n at the end of line
        if (line == ""):
            continue


        if ( (line.find("<td") != -1) and (line.find("onMouseover=")) != -1):
            #print "strange javascript line found"
            theParser.tdCount = theParser.tdCount + 1
            continue

        #print "%s" % line

	if (theParser.scriptTagOn == False):
            try :
                theParser.feed(line)
            except HTMLParseError, ex:
                print "Exception: %s @ %d" % (ex.msg, lineNumber)
                pass
        else:
            if (line == "</script>"):
                theParser.scriptTagOn = False

    
    file.close()


########
# MAIN #

if len(sys.argv) != 3:
    print "usage: %s [b|a|p] [HTML-FILE]" % sys.argv[0]
    print "     : [b|a|p]     base|alero|pivot"
    print "     : [HTML-FILE]"
    print "Prints to stdout a list of colon-separated \":\" rows which contain player-id:[b|a|p]:name"
    raise SystemExit

for elem in sys.argv[2:]:
    processHTMLFile(elem)

