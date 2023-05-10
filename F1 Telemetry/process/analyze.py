
import math
from PIL import Image, ImageDraw, ImageFont


# Class that allows the production of stat cards for drivers in a race.
class Analyze:
    
    def __init__(self, leagueName, leagueDay, raceName):
        self.leagueName = leagueName
        self.leagueDay = leagueDay
        self.raceName = raceName
        
        # The directory that data will be loaded/saved to.
        self.directory = "data/" + self.leagueDay + "/" + self.raceName + "/";

        # Variables used to store data about the performance of drivers in a race.
        self.drivers = []
        self.numLaps = 0


    # Fills an array with driver data from the race.
    def ReadData(self):
        
        f = open(self.directory + "stats/overall/race.txt", "r")
        f.readline() # Discards race name
        self.numLaps = f.readline()
        raceParticipants = f.readline().strip().split(",")
        f.close()
        
        # For all race participants, a bew driver dictionary wil be created.
        for driver in raceParticipants:
            f = open(self.directory + "stats/drivers/" + driver + ".txt", "r")
            
            newDriver = { 
                # Basic driver data
                "teamId": int(f.readline()),
                "name": f.readline().strip(),
    
                # Pace data
                "fastestLap": int(f.readline()),
                "raceTime": float(f.readline()),
    
                # Racecraft data
                "gridPos": int(f.readline()),
                "finishPos": int(f.readline()),
    
                # Safety data
                "warnings": int(f.readline()),
                "penalties": int(f.readline()),
                "finishStatus": int(f.readline()),
                "lapsCompleted": int(f.readline()),
    
                # Pitstop data
                "pitStops": int(f.readline()),
                "pitStatus": [int(x) for x in f.readline().strip().split(",") if x != ""],
    
                # Consistency and pace data
                "lapTimes": [int(x) for x in f.readline().strip().split(",") if x != ""],
    
                # Racecraft data
                "carPos": [int(x) for x in f.readline().strip().split(",") if x != ""],
                
                # Stats
                "overall": 0,
                "pace": 0,
                "consistency": 0,
                "racecraft": 0,
                "safety": ""
            }
            
            # Makes sure driver has completed the race.
            if newDriver["finishStatus"] == 3:
                self.drivers.append(newDriver)

    # Calculates stats for the performance of each driver.
    def ProcessData(self):
        
        # Calculates consistency stat for each driver.
        for driver in self.drivers:
            driver["consistency"] = self.FindDriverConsistency(driver);
            
        # Calculates pace stat for each driver.
        self.FindDriverPace()
            
        # Calculates racecraft stat for each driver.
        for driver in self.drivers:
            driver["racecraft"] = self.FindDriverRacecraft(driver);
            
        # Calculates safety stat for each driver.
        for driver in self.drivers:
            driver["safety"] = self.FindDriverSafety(driver);
            
        # Calculates overall stat for each driver.
        for driver in self.drivers:
            driver["overall"] = self.FindDriverOverall(driver);
    
    # Saves the calculated stats for each driver.
    def SaveData(self):
        
        # Creates stat card for each driver.
        for driver in self.drivers:
            self.CreateNewStatCard(driver)
            
        file = "";
        # Loops through driver data and adds their stats.
        for driver in self.drivers:
            file += driver["name"] + "," + self.FindTeamName(driver["teamId"]) + "," + str(driver["finishPos"]) + "," + str(driver["overall"]) + "," + str(driver["pace"]) + "," + str(driver["consistency"]) + "," + str(driver["racecraft"]) + "," + driver["safety"] + "\n"; 

        # Saves driver stats
        with open(self.directory + "stats/overall/ratings.txt", "w") as f:
            f.write(file)


    # Finds the average laptimes for each driver.
    def FindAverageLaps(self):

        sessionAveragePace = []
        for driver in self.drivers:

            fastestLaps = [];
            # Gets a certain number of fastest laps for each driver.
            for i in range(int(len(driver["lapTimes"]) * 0.75)):
                if (min(driver["lapTimes"]) == None):
                    i -= 1;
                else:
                    fastestLaps.append(min(driver["lapTimes"]));

                # Removes fastest lap from list.
                driver["lapTimes"].remove(min(driver["lapTimes"]));
                
            # Calculates average and adds it to list with other drivers.
            averagePace = sum(fastestLaps) / len(fastestLaps);
            sessionAveragePace.append({"name": driver["name"], "averagePace": averagePace})
        
        # Returns list with slowest drivers at the head.
        return (sorted(sessionAveragePace, key=lambda x:x["averagePace"], reverse=True));
    
    # Gets the name of the driver who holds the fastest laptime.
    def FindFastestLap(self):
        
        fastestLap = {"name": self.drivers[0]["name"], "laptime": self.drivers[0]["fastestLap"]};
        for driver in self.drivers:
            #Finds fastest lap in session.
            if (driver["fastestLap"] < fastestLap["laptime"]):
                fastestLap["name"] = driver["name"];
                fastestLap["laptime"] = driver["fastestLap"];
        
        return fastestLap["name"];
    
    # Calculates pace stat for each driver based on their ranking compared to others.
    def FindDriverPace(self):
        
        basePoints = 50;
        pointsToAdd = ((40 / len(self.drivers)) * 1.1);
        fastestLapPointsAllocated = False;

        # Gives out points for each driver depending on average pace.
        for driver in self.FindAverageLaps():
            basePoints += pointsToAdd;

            for d in self.drivers:
                if (driver["name"] == d["name"]):
                    if (d["finishPos"] == len(self.drivers)):
                        d["pace"] += basePoints-pointsToAdd;
                    else:
                        d["pace"] += basePoints;
                    
                # Gives out points for driver with fastest lap.
                if self.FindFastestLap() == d["name"] and not fastestLapPointsAllocated:
                    d["pace"] += pointsToAdd * 4;
                    fastestLapPointsAllocated = True;

                d["pace"] = self.RoundRating(d["pace"]);
    
    # Calculates consistency stat for each driver.
    def FindDriverConsistency(self, driver):

        basePoints = 50;
        pointsToAdd = 50 / (float(self.numLaps) * 0.6);
        consistencyThreshold = (driver["raceTime"] / float(self.numLaps)) * 0.01;

        # Gives out points for each lap that is close in time to the next.
        for i in range(len(driver["lapTimes"]) - 1):
            if ((abs(driver["lapTimes"][i] - driver["lapTimes"][i+1]) / 2500) <= consistencyThreshold):
                basePoints += pointsToAdd; 
                    
        return self.RoundRating(basePoints);
    
    # Calculates racecraft stat for each driver.
    def FindDriverRacecraft(self, driver):

        basePoints = 52;
        pointsPerPosition = 2;
        pointsPerOvertake = 1;
        overtakeLimit = 10;

        # Calculates points based on driver postion.
        basePoints += (20 - driver["finishPos"]) * pointsPerPosition;
        overtakes = driver["gridPos"] - driver["finishPos"];
        
        # Makes sure drivers do not gain too many points for overtakes.
        if overtakeLimit < overtakes:
            basePoints += overtakeLimit * pointsPerOvertake;
            
        # Assigns negative points if driver has dropped positions.
        elif overtakes < 0:
            if -overtakeLimit < overtakes:
                basePoints += overtakes * pointsPerPosition;
            else:
                basePoints += -(overtakeLimit * pointsPerPosition)
                
            if basePoints < 50:
                basePoints = 50
                
        # Gives driver points for overtakes.
        else:
            basePoints += overtakes * pointsPerOvertake
        
        return self.RoundRating(basePoints);

    # Calculates safety stat for each driver.
    def FindDriverSafety(self, driver):

        points = 100;
        rating = "";
        # Calculates points deduction based on the number of warnings/penalties received.
        points -= (driver["warnings"] * 5) + (driver["penalties"] * 20)
        
        # Gives a rating based on number of points left.
        if (points == 100):
            rating = "S+";
        elif (95 <= points):
            rating = "S=";
        elif (90 <= points):
            rating = "S-"

        elif (85 <= points):
            rating = "A+";
        elif (80 <= points):
            rating = "A=";
        elif (75 <= points):
            rating = "A-"

        elif (70 <= points):
            rating = "B+";
        elif (65 <= points):
            rating = "B=";
        elif (60 <= points):
            rating = "B-"
        
        elif (55 <= points):
            rating = "C+";
        elif (50 <= points):
            rating = "C=";
        elif (45 <= points):
            rating = "C-"

        elif (40 <= points):
            rating = "D+";
        elif (35 <= points):
            rating = "D=";
        elif (30 <= points):
            rating = "D-"

        elif (25 <= points):
            rating = "E+";
        elif (20 <= points):
            rating = "E=";
        elif (15 <= points):
            rating = "E-"

        elif (10 <= points):
            rating = "F+";
        elif (5 <= points):
            rating = "F=";
        else:
            rating = "F-"

        return rating;

    # Calculates overall stat for each driver.
    def FindDriverOverall(self, driver):

        # Returns the mean of pace, consistency and racecraft stats.
        return self.RoundRating((driver["pace"] + driver["consistency"] + driver["racecraft"]) / 3);

    # Creates an image showing stats and details for each driver.
    def CreateNewStatCard(self, driver):
        WHITE = (255,255,255)

        # Loads in template image.
        img  = Image.open("process\img\statCardTemplate.png")
        draw = ImageDraw.Draw(img)
        
        # Labels
        label1 = self.leagueName + " " + self.leagueDay
        label2 = "Race: " + self.raceName
        font = ImageFont.truetype("arial.ttf", 15)
        draw.text((img.width/2-font.getlength(label1)/2, img.height/20), label1, WHITE, font=font, stroke_width=0) # top
        draw.text((img.width/2-font.getlength(label2)/2, img.height-img.height/20-15), label2, WHITE, font=font, stroke_width=0) # bottom

        # Overall rating
        font = ImageFont.truetype("ariblk.ttf", 100)
        draw.text((65, 105), str(driver["overall"]), WHITE, font=font, stroke_width=0)

        # Player
        font = ImageFont.truetype("ariblk.ttf", 60)
        if len(driver["name"]) > 10:
            font = ImageFont.truetype("ariblk.ttf", 50)
        draw.text((30, 580), driver["name"], WHITE, font=font, stroke_width=0)

        # Position
        font = ImageFont.truetype("arial.ttf", 50)
        if driver["finishStatus"] == 3:
            draw.text((30, 660), "P" + str(driver["finishPos"]), WHITE, font=font, stroke_width=0)
        else:
            draw.text((30, 660), "DNF", WHITE, font=font, stroke_width=0)

        # Ratings
        font = ImageFont.truetype("ariblk.ttf", 50)
        draw.text((80, 765), str(driver["pace"]), WHITE, font=font, stroke_width=0)
        draw.text((200, 765), str(driver["consistency"]), WHITE, font=font, stroke_width=0)
        draw.text((320, 765), str(driver["racecraft"]), WHITE, font=font, stroke_width=0)
        draw.text((440, 765), str(driver["safety"]), WHITE, font=font, stroke_width=0)

        # Labels for ratings
        font = ImageFont.truetype("arial.ttf", 25)
        draw.text((80, 830), "PAC", WHITE, font=font, stroke_width=0)
        draw.text((200, 830), "CON", WHITE, font=font, stroke_width=0)
        draw.text((320, 830), "RAC", WHITE, font=font, stroke_width=0)
        draw.text((440, 830), "SAF", WHITE, font=font, stroke_width=0)

        # Team's car
        carImg = Image.open("process/img/" + self.FindTeamName(driver["teamId"]) + ".png")
        img.paste(carImg, (0,0), carImg)

        # Saves unique image to a new file with driver's name.
        img.save(self.directory + "images/drivers/" + driver["name"] + ".png")
    
    
    # Makes sure the rating of a stat is even.
    def RoundRating(self, value):

        value = math.floor(value);
        newVal = value;

        # Makes number even.
        if not value % 2 == 0:
            newVal = value+1;
        
        # Makes sure value is under 100 and over 50.
        if 100 <= newVal:
            return 98
        else:
            return newVal;
    
    # Returns the team name that a driver is related to.
    def FindTeamName(self, id):

        team = "";
        if (id == 0):
            team = "mercedes";
        elif (id == 1):
            team = "ferrari";
        elif (id == 2):
            team = "redbull";
        elif (id == 3):
            team = "williams";
        elif (id == 4):
            team = "astonmartin";
        elif (id == 5):
            team = "alpine";
        elif (id == 6):
            team = "alphatauri";
        elif (id == 7):
            team = "haas";
        elif (id == 8):
            team = "mclaren";
        elif (id == 9):
            team = "alfaromeo";
        return team;
    

# Can be used to re-analyse the data, if you want to edit the driver files.
"""
# Analyzes the data
a = Analyze("EWRL", "TUESDAY", "SUZUKA")
a.ReadData()
a.ProcessData()
a.SaveData()
"""
