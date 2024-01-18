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

    // Main comp creation
function mainComp() {

    var itemNameToCheck = "Main Comp"; // Replace with the name of the composition you want to check

    // Loop through all items in the project to find the composition
    var mainCompExist = verifyExist(itemNameToCheck);

    // If the loop finishes and no matching composition is found, create the comp
    if (!mainCompExist) {
        var newComp = project.items.addComp(itemNameToCheck, videoResolution[0], videoResolution[1], 1, totalDuration, fps);
    }
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
patternData = loadJSONData('patterns.json', patternData);
playerData = loadJSONData('players.json', playerData);

// Recursive function to process patterns
function processPatterns(sectionKey, measureKey, playerKey, player) {
    for (var patternKey in player) {
        if (player.hasOwnProperty(patternKey)) {
            var patternValue = player[patternKey];
            
            // Perform actions on the pattern here
            alert("Section: " + sectionKey + ", Measure: " + measureKey + ", Player: " + playerKey + ", Pattern: " + patternKey + ", Value: " + patternValue);
        }
    }
}

// Recursive function to process players
function processPlayers(sectionKey, measureKey, measure) {
    for (var playerKey in measure) {
        if (measure.hasOwnProperty(playerKey)) {
            var player = measure[playerKey];
            
            // Perform actions on players here (if needed)

            // Process patterns for this player
            processPatterns(sectionKey, measureKey, playerKey, player);
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
    var timelinePath = new File($.fileName).parent.fullName + '/timeline.json'; // Replace with your JSON file path
    try {
        var timelineContent = readFile(timelinePath);
        var timelineData = parseJSON(timelineContent);
    } catch (e) {
        $.writeln('Error: ' + e.message);
    }

    var project = app.project;

    // Main comp creation
    var compNameToCheck = "Main comp"; // Replace with the name of the composition you want to check

    // Loop through all items in the project to find the composition
    for (var i = 1; i <= project.numItems; i++) {
        var currentItem = project.item(i);
        if (currentItem instanceof CompItem && currentItem.name === compNameToCheck) {
            break; // You can break out of the loop once you find the composition
        }
    }

    // If the loop finishes and no matching composition is found
    if (i > project.numItems) {
        var newComp = app.project.items.addComp("Main comp", 3840, 2160, 1, 1142.5, 60);
    }

    // Note Object selection
    var result = prompt("What is the name of your note object?");

    // Start searching from the root of the project
    var 
    var compositionFound = verifyExist(project.rootitem);

    // If the composition is not found anywhere in the project
    if (!compositionFound) {
        alert("Composition does not exist in any item.");
    }

    //Begin construction of note-based compositions
    processSections(timelineData);

}

main();