import requests, json, sys, time, bs4, colorama
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style
colorama.init()

def CheckSettings():
    with open('./settings.json') as f:
        data = json.load(f)

    # If placeholder is in our settings.json, we will return false as placeholder should be a real value.
    if data['settings']['school'] == "PLACEHOLDER":
        return False
    else:
        return True # Else, we return true.

# Pulls school from JSON to assist request functions.
def PullRuntimeSchool():
    with open('./settings.json') as f:
        data = json.load(f)

    return data['settings']['school']

# Checks for an extra space on input for error handling purposes.
def CheckExtraSpace(string):
    if string[0] == " ":
        return True
    else:
        return False

# Checks if an extra space in any of the list's entites.
def CheckProfessorInput(ProfessorList):
    spaceFlag = False

    for Professor in ProfessorList:
        tempProfessor = Professor.split(' ')
        if tempProfessor[0] == '':
            spaceFlag = True

    return spaceFlag

def RemoveNoneType(LegacyList):

    tempLegacyList = []

    for ID in LegacyList:
        if ID != None:
            tempLegacyList.append(ID)

    return tempLegacyList

# Uses requests to pull the legacyID for the professor.
def PullLegacyID(ProfessorName):

    LegacyEntity = []

    runTimeSchoolName = PullRuntimeSchool()
    requestURL = "https://www.ratemyprofessors.com/graphql"
    requestMethod = "POST"
    requestPayload = "{\"query\":\"query NewSearchTeachersQuery(\\r\\n  $query: TeacherSearchQuery!\\r\\n) {\\r\\n  newSearch {\\r\\n    teachers(query: $query) {\\r\\n      edges {\\r\\n        cursor\\r\\n        node {\\r\\n          id\\r\\n          legacyId\\r\\n          firstName\\r\\n          lastName\\r\\n          school {\\r\\n            name\\r\\n            id\\r\\n          }\\r\\n          department\\r\\n        }\\r\\n      }\\r\\n    }\\r\\n  }\\r\\n}\\r\\n\",\"variables\":{\"query\":{\"text\":\"" + ProfessorName  + "\"}}}"
    
    requestHeaders = {
        'Authorization': 'Basic dGVzdDp0ZXN0',
        'Host': 'www.ratemyprofessors.com',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", requestURL, headers=requestHeaders, data=requestPayload)

    if "department" in response.text:
        
        jsonResponse = json.loads(response.text)

        i = 0

        for _ in range(len(response.text.split("legacyId")) - 1):
            if jsonResponse["data"]["newSearch"]["teachers"]["edges"][i]["node"]["school"]["name"] == runTimeSchoolName:
                LegacyEntity.append(jsonResponse["data"]["newSearch"]["teachers"]["edges"][i]["node"]["firstName"] + " " + jsonResponse["data"]["newSearch"]["teachers"]["edges"][i]["node"]["lastName"])
                LegacyEntity.append(jsonResponse["data"]["newSearch"]["teachers"]["edges"][i]["node"]["legacyId"])
                return LegacyEntity
            i += 1
    else:
        return

# Pulls all the legacyIDs from RMP.
def PullLegacyForList(ProfessorList):

    LegacyIDList = []

    for Professor in ProfessorList:
        LegacyIDList.append(PullLegacyID(Professor))

    LegacyIDList = RemoveNoneType(LegacyIDList)

    return LegacyIDList

def PrintRatings(ProfessorEntites, ProfessorProfile):

    print()

# Pulls the ratings for each legacyID from RMP.
def PullRatings(LegacyID):
    import requests

    ProfessorProfile = []

    requestURL = "https://www.ratemyprofessors.com/ShowRatings.jsp?tid=" + str(LegacyID[1])

    payload={}

    headers = {
        'Host': 'www.ratemyprofessors.com'
    }

    response = requests.request("GET", requestURL, headers=headers, data=payload)

    soup = BeautifulSoup(response.text, "html.parser")
    
    mainRating = soup.findAll("div", class_="RatingValue__Numerator-qw8sqy-2 liyUjw")
    ProfessorProfile.append(((str((str(mainRating).split('<')[1])).split('>')[1])))

    for each_div in soup.findAll("div", class_="FeedbackItem__FeedbackNumber-uof32n-1 kkESWs"):
        ProfessorProfile.append((str((str(each_div).split('<')[1])).split('>')[1]))

    return ProfessorProfile

# Checks the menu input for the options.
def MenuInputCheck(input):
    menuOptions = ["0", "1", "2"]

    for option in menuOptions:
        if option == input:
            return True
    
    return False

# Menu Screen
def MenuScreen():

    if CheckSettings() == False:
        print("Please input your University in settings.json before starting this program.")
        time.sleep(2.021)
        sys.exit()

    print( Fore.CYAN + "Rate My Professor Lookup Tool\n")

    print("[0] - Exit")
    print("[1] - Search Multiple Professors")
    print("[2] - Search Single Professor")
    userInput = input()

    ProfessorList = []

    MenuFlag = MenuInputCheck(userInput)

    # While the menuFlag is false, we'll keep asking for the input until we get a true value from the user.
    while MenuFlag is False:
        print("[0] - Exit")
        print("[1] - Search Multiple Professors")
        print("[2] - Search Single Professor")
        userInput = input()

        MenuFlag = MenuInputCheck(userInput)


    # Decision routes from the input
    if userInput == "0":
        print("Exiting...")
        time.sleep(1.017)
        sys.exit()
    elif userInput == "1":

        print("-------------------")
        print("Multiple Professors")
        print("Please enter each professor name followed by a comma:")

        userInput = input()
        tempProfessorList = userInput.split(',')

        while len(tempProfessorList) < 2:

            print("\n")
            print("-------------------")
            print("Error - You've entered less than 2 professors, please select option [2] instead.")
            print("-------------------")
            print("\n")

            tempProfessorList.clear()

            print("Multiple Professors")
            print("Please enter each professor name followed by a comma:")
            userInput = input()
            tempProfessorList = userInput.split(',')

        if CheckProfessorInput(tempProfessorList) is True:
            for Professor in tempProfessorList:
                if CheckExtraSpace(Professor) is True:
                    tempProfessor = Professor.split(' ')
                    ProfessorList.append(tempProfessor[1] + " " + tempProfessor[2])
                else:
                    ProfessorList.append(Professor)
            
            return ProfessorList
        else:
            ProfessorList = tempProfessorList

    elif userInput == "2":
        print("-------------------")
        print("Single Professor")
        print("Please enter the professor name:")
        userInput = input()
        ProfessorList.append(userInput)
        return ProfessorList

    return ProfessorList

# Processes all of the professor profiles.
def ProcessRatings(ProfessorProfiles):

    tempProfessorProfiles = []
    
    for Professor in ProfessorProfiles:
        tempProfessorProfiles.append(PullRatings(Professor))

    return tempProfessorProfiles

# Prints all professor profiles with their respective ratings.
def PrintProfessorProfiles(ProfessorProfiles, ProfessorRatings):
    i = 0
    
    for Professor in ProfessorProfiles:
        print("\n")
        print("Professor Name: " + str(Professor[0]))
        print("Professor Rating: " + str(ProfessorRatings[i][0]) + "/5")
        print("Professor Difficulty: " + str(ProfessorRatings[i][2]))
        print(str(ProfessorRatings[i][1]) + " of students who rated would take this class again.")
        i += 1



if __name__ == "__main__":
    
    ProfessorEntites = MenuScreen()    
    ProfessorProfiles = PullLegacyForList(ProfessorEntites)
    ProfessorRatings = ProcessRatings(ProfessorProfiles)
    PrintProfessorProfiles(ProfessorProfiles, ProfessorRatings)
