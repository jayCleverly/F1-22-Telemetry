const { F122UDP } = require("f1-22-udp")


// Choices from app visuals.
var arguments = process.argv
var leagueDay = arguments[2];
var sprintRace = arguments[3] == "true"; // Checks to see if there is a sprint race.
var raceName = arguments[4];

// Creates directory for where data will be stored.
var directory = "data/" + leagueDay + "/" + raceName + "/"; // Sets new directory for race


// Connects to f1 22 udp parser.
const f122 = new F122UDP()
f122.address = require("ip").address(); // Sets ip address to current machine's address.

f122.start();
console.log("\n___COLLECTING AT " + f122.address + "___\n(Please do not close this window)");

// Variables used to store data about the race.
var sessionData = [];
var sessionType;
var totalLaps;
var playerCount = 1;


// Used to collect general data about the race.
f122.on("session", data => {

    sessionType = data.m_sessionType;
    totalLaps = data.m_totalLaps;
})


// Used to collect data about participants of race
f122.on("participants", data => {

    // Determines if session is main race.
    if ((!sprintRace && sessionType == 10) || (sprintRace && sessionType == 11)) { // When sprint race 10 is sprint

        var participants = data.m_participants;
        var emptyArray = new Array(totalLaps).fill(null);
        
        // Checks that participant is an actual player.
        participants.map(a => { if (a.m_teamId != 255 && sessionData.length != 20) {
            
            /* Make sure all players are assigned different names 
               if they haven't turned on udp setting. */
            if (a.m_name == "Player") {
                a.m_name = "Player" + playerCount;

            // Gets rid of any special characters (found in PEREZ).
            } else if (a.m_name == "PÉREZ") {
                a.m_name = "PEREZ"
            }

            // Creates new object for each driver to store data in.
            sessionData.push({
                            // Basic driver data
                            "teamId": a.m_teamId,
                            "name": a.m_name,

                            // Pace data
                            "fastestLap": 0,
                            "raceTime": 0,

                            // Racecraft data
                            "gridPos": 0,
                            "finishPos": 0,

                            // Safety data
                            "warnings": 0,
                            "penalties": 0,
                            "finishStatus": 0,
                            "lapsCompleted": 0,

                            // Pitstop data
                            "pitStops": 0,
                            "pitStatus": emptyArray.slice(),

                            // Consistency and pace data
                            "lapTimes": emptyArray.slice(),

                            // Racecraft data
                            "carPos": emptyArray.slice(),
            })
            playerCount++;
        }})
    }
})


// Used to collect data about each driver's laps.
f122.on("lapData", data => {

    // Determines if session is main race.
    if ((!sprintRace && sessionType == 10) || (sprintRace && sessionType == 11)) {

        var lapData = data.m_lapData;
        var index = 0;

        // Checks to see if driver is a real player.
        lapData.map(a => { if (a.m_carPosition != 0) {
            var carToUpdate = sessionData.at(index);

            // Driver is completing laps.
            if (carToUpdate.lapsCompleted == a.m_currentLapNum-2) {
                LogData(carToUpdate, a.m_currentLapNum-2, a)

            // Driver has finished race.
            } else if (a.m_resultStatus == 3) {
                LogData(carToUpdate, totalLaps-1, a)
            }
            index++;
        }})
        console.log("");
    }
}) 


// Used to collect overall data about the race.
f122.on("finalClassification", data => {

    // Determines if session is main race.
    if ((!sprintRace && sessionType == 10) || (sprintRace && sessionType == 11)) {

        var results = data.m_classificationData;
        var index = 0;

        // Checks to see if driver is a real player.
        results.map(a => { if (a.m_gridPosition != 0) {
            var carToUpdate = sessionData.at(index);

            // Pace data
            carToUpdate.fastestLap = a.m_bestLapTimeInMS;
            carToUpdate.raceTime = a.m_totalRaceTime;

            // Safety data
            carToUpdate.penalties = a.m_numPenalties;
            carToUpdate.finishStatus = a.m_resultStatus;
            carToUpdate.lapsCompleted = a.m_numLaps;

            // Racecraft data
            carToUpdate.gridPos = a.m_gridPosition;
            carToUpdate.finishPos = a.m_position;

            // Pitsop data
            carToUpdate.pitStops = a.m_numPitStops;

            index++;
        }});

        // Stops udp parser.
        f122.stop();
        SaveData();
    }
})


// Logs data each lap for a driver.
function LogData(object, index, dataStream) {

    // Consistency data
    object.lapTimes[index] = dataStream.m_lastLapTimeInMS;

    // Racecraft data
    object.carPos[index] = dataStream.m_carPosition;

    // Safety data
    object.warnings = dataStream.m_warnings;
    object.lapsCompleted++;

    // Pitstop data
    object.pitStatus[index] = dataStream.m_pitStatus;
}

// Saves session data to files.
function SaveData() {

    const fs = require("fs");

    // Creats new directories for race.
    fs.mkdirSync(directory + "stats/drivers", { recursive: true });
    fs.mkdirSync(directory + "stats/overall", { recursive: true });
    fs.mkdirSync(directory + "images/drivers", { recursive: true });
    fs.mkdirSync(directory + "images/overall", { recursive: true });

    var raceFile = raceName + "\n" + totalLaps + "\n";
    // Loops through driver data.
    for (var driver of sessionData) {
        var driverFile = "";

        // Adds each driver stat to file.
        for (var key in driver) {
            driverFile += driver[key] + "\n";
        }

        // Creates a new file for each driver.
        fs.writeFileSync(directory + "stats/drivers/" + driver.name + ".txt", driverFile, err => {
            if (err) {
                console.log(err);
            }
        })
        raceFile += driver.name + ",";
    }

    raceFile = raceFile.slice(0, -1) // Removes last comma
    // Writes overall session data to a file.
    fs.writeFileSync(directory + "stats/overall/race.txt", raceFile, { flag: "w" }, err => {
        if (err) {
            console.log(err);
        }
    });
}
