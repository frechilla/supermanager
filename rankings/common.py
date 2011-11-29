import sys
import os
import re
import urllib

def GetPlayersPosAndHeightFromInternet(playerId):
    """ retrieve player's position and height from ACB website (bypassing smanager)
        returns a list made up of 2 elements, (position, height)
            position is a letter "b", "e", "a", "p|f"
            height is in meters, for example 1.92

            if it couldn't be retrieved from the internet website it returns
            a list of 2 empty strings
    """
    regexComp = re.compile('[\ \t]*<td class="datojug">(\w+)[\ \t]*\|[\ \t]* ([0-9\.]+)')
    prevLineFound = False
    params = urllib.urlencode({'id' : playerId})
    f = urllib.urlopen('http://www.acb.com/jugador.php?%s' % params)
    for urlline in f.readlines():
        urlline = urlline.rstrip()
        if (urlline.find(r'<td class="titulojug">posici') != -1):
            prevLineFound = True
        elif(prevLineFound == True):
            result = regexComp.search(urlline)
            if (result != None):
                f.close()
                return (result.group(1).lower(), result.group(2))
        else:
            prevLineFound = False

    else:
        f.close()
        return ("", "")


def LoadPlayerLongFile(theDictionary, filename):
    """ Loads a player-long file into the dictionary passed as a parameter
        This players-long file's format conatins a list of rows, each one of them
        contains a colon(:) separated list of:
          player-id:[b|a|p]:[b|e|a|p|f]:height:name
            player-id, is a 3 character string (so far)
            [b|a|p], is the position described in supermanager.acb.com
            [b|e|a|p|f], is the position as described in acb.com (player's file)
            height, in meters (for example: 1.92)
            name, full name of the player
        
        if file doesnt exist it will raise a systemexit exception
        any error the function finds it will raise a systemexit error
    """
    if not os.path.isfile(filename):
        print filename + " is not a file"
        raise SystemExit
    
    f = open(sys.argv[1], 'r')
    for line in f:
        line = line.rstrip() # remove \n at the end of line

        elems = line.split(':')
        if (len(elems) != 5):
            print "Error reading players-long-file @ %s" % line
            raise SystemExit

        if theDictionary.has_key(elems[0]):
            print "key %s already exists in dictionary" % elems[0]
            raise SystemExit
            
        theDictionary[elems[0]] = {'pos':elems[1], 'acb_pos':elems[2], 'height':elems[3], 'name':elems[4]}

    f.close()