// Declare global variables
var project = app.project;

// Check project assets for existence of specified item
function verifyExist(itemName) {
    for (var i = 1; i <= project.numItems; i++) {
        var currentItem = project.items[i];
        if (currentItem.name === itemName) {
            return project.items[i];
        }
    }
    return null; // Composition not found in this item
}

// Function to read a file and return its content as a string
function readFile(filePath) {
    var file = new File(filePath);
    if (!file.exists) {
        throw new Error('File not found: ' + file);
    }
    file.open('r');
    var content = file.read();
    file.close();
    return content;
}

// A simple JSON parser
function parseJSON(jsonString) {
    try {
        return eval('(' + jsonString + ')');
    } catch (e) {
        throw new Error('Invalid JSON');
    }
}

// Function to load pattern data from a JSON file
function loadJSONData(fileName, data) {
    var filePath = new File($.fileName).parent.fullName + '/' + fileName; // Replace with your JSON file path
    try {
        var content = readFile(filePath);
        return parseJSON(content);
    } catch (e) {
        $.writeln('Error loading pattern data: ' + e.message);
    }
}

// Call functions to load data from reference JSONs
var patternData = loadJSONData('patterns.json', patternData);
var playerData = loadJSONData('players.json', playerData);

// Main comp creation
function mainComp(videoResolution, totalDuration, fps) {

    var itemNameToCheck = "Main Comp"; // Replace with the name of the composition you want to check

    // Loop through all items in the project to find the composition
    var mainCompExist = verifyExist(itemNameToCheck);

    // If the loop finishes and no matching composition is found, create the comp
    if (!mainCompExist) {
        project.items.addComp(itemNameToCheck, videoResolution[0], videoResolution[1], 1, totalDuration, fps);
    }
}

// Recursive function to process patterns
function processPatterns(sectionKey, measureKey, playerKey, player, playerLayout) {
    for (var patternKey in player) {
        if (player.hasOwnProperty(patternKey)) {
            var patternValue = player[patternKey];
            
            // Perform actions on the pattern here
            // alert("Section: " + sectionKey + ", Measure: " + measureKey + ", Player: " + playerKey + ", Pattern: " + patternKey + ", Value: " + patternValue);
        }
    }
}

// Recursive function to process players
function processPlayers(sectionKey, measureKey, measure) {
    for (var playerKey in measure) {
        if (measure.hasOwnProperty(playerKey)) {
            var player = measure[playerKey];
            
            // Perform actions on players here (if needed)
            var playerLayout = playerData[playerKey]['layout']

            // Process patterns for this player
            processPatterns(sectionKey, measureKey, playerKey, player, playerLayout);
        }
    }
}

// Recursive function to process measures
function processMeasures(sectionKey, section) {
    for (var measureKey in section) {
        if (section.hasOwnProperty(measureKey)) {
            var measure = section[measureKey];
            
            // Perform actions on measures here (if needed)

            // Process players for this measure
            processPlayers(sectionKey, measureKey, measure);
        }
    }
}

function processSections(timelineData) {
    // Iterate over the sections (first-level keys)
    for (var sectionKey in timelineData) {
        if (timelineData.hasOwnProperty(sectionKey)) {
            var section = timelineData[sectionKey];

            // Perform actions on sections here (if needed)

            // Process measures for this section
            processMeasures(sectionKey, section);
        }
    }
}

// Main function
function main() {

    // Import project detail JSON
    var detailPath = new File($.fileName).parent.fullName + '/project_details.json';
    try {
        var detailContent = readFile(detailPath);
        var detailData = parseJSON(detailContent);
    } catch (e) {
        throw new Error('Error: ' + e.message);
    }

    // Save project details to variables
    var patternFPS = detailData['pattern_fps'];
    var projectLength = detailData['project_length'];
    var fps = detailData['fps'];
    var videoResolution = detailData['video_resolution'];

    // Import timeline JSON
    var timelinePath = new File($.fileName).parent.fullName + '/timeline.json';
    try {
        var timelineContent = readFile(timelinePath);
        var timelineData = parseJSON(timelineContent);
    } catch (e) {
        throw new Error('Error: ' + e.message);
    }

    // Check for main comp first, create it if it doesn't exist
    mainComp();

    // Note Object searching from the root of the project
    var itemNameToCheck = prompt("What is the name of your note object?", "");
    var noteObject = verifyExist(itemNameToCheck);

    // If the note object does not exist, throw an error
    if (!noteObject) {
        throw new Error("The note object " + itemNameToCheck + " was not found.");
    }

    // Check if the item is indeed a composition, and if so save the resolution for later use
    if (noteObject instanceof CompItem) {
        var noteResolution = [myComp.width, myComp.height];
    } else {
        throw new Error("\"" + itemNameToCheck + "\" is not a composition.");
    }

    // Grab the duration of the note object
    var noteDuration = noteObject.duration;
    var totalDuration = projectLength + noteDuration;

    //Begin construction of note-based compositions
    processSections(timelineData);

}

main();