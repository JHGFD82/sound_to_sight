// Global variables
var project = app.project;
var patternData, playerData, patternFPS, projectLength, patternLength, noteCeiling, fps, videoResolution, noteObject, noteResolution, noteDuration, totalDuration, noteTrackMatteComp, noteHitComp, patternFolder;

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
function loadJSONData(fileName) {
    var filePath = new File($.fileName).parent.fullName + '/' + fileName;
    var content = readFile(filePath);
    return parseJSON(content);
}

// Create track matte for instrument layout underneath note for each note object
function createNoteObjects() {
    noteTrackMatteComp = project.items.addComp("Note Track Matte", 345, 345, 1, 20 / patternFPS, patternFPS);
    var trackMatte = noteTrackMatteComp.layers.addShape();
    trackMatte.name = "Note Track Matte";
    var trackMatteOpacity = trackMatte.opacity;
    trackMatteOpacity.setValueAtTime(0, 100);
    trackMatteOpacity.setValueAtTime(20 / patternFPS, 0);
    var contents = trackMatte.property("ADBE Root Vectors Group");
    var trackMatte = contents.addProperty("ADBE Vector Shape - Ellipse");
    trackMatte.property("ADBE Vector Ellipse Size").setValue([345, 345]);
    var shapeFill = contents.addProperty("ADBE Vector Graphic - G-Fill");
    shapeFill.property("ADBE Vector Grad Type").setValue(2);
    shapeFill.property("ADBE Vector Grad Start Pt").setValue([0.0, 0.0]);
    shapeFill.property("ADBE Vector Grad End Pt").setValue([0.0, noteTrackMatteComp.height / 2]);
}

// Create white note hit symbol
function createNoteHit() {
    noteHitComp = project.items.addComp("Note Hit", 100, 100, 1, 10 / patternFPS, patternFPS);
    var noteHit = noteHitComp.layers.addShape();
    noteHit.name = "Note Hit";
    var noteHitOpacity = noteHit.opacity;
    noteHitOpacity.setValueAtTime(0, 100);
    noteHitOpacity.setValueAtTime(6 / patternFPS, 0);
    var contents = noteHit.property("ADBE Root Vectors Group");
    var noteHit = contents.addProperty("ADBE Vector Shape - Ellipse");
    noteHit.property("ADBE Vector Ellipse Size").setValue([100, 100]);
    var shapeFill = contents.addProperty("ADBE Vector Graphic - Fill");
    shapeFill.property("ADBE Vector Fill Color").setValue([1, 1, 1, 1]);
}

// Assemble patterns with supplied note information
function patternBuilder(patternComp, note, instrumentDiagramSize, instrumentDiagramLayer) {

    // NoteLayer properties for use with multiple objects per note
    var noteLayerX = note[4][0] + (patternComp.width / 2) - (instrumentDiagramSize[0] / 2);
    var noteLayerY = note[4][1] + (patternComp.height / 2) - (instrumentDiagramSize[1] / 2);
    var objPosition = [noteLayerX, noteLayerY];
    var objStartTime = note[0] / patternFPS;

    // Placement of the track matte comp behind note
    var noteTrackMatte = patternComp.layers.add(noteTrackMatteComp);
    noteTrackMatte.startTime = objStartTime;
    noteTrackMatte.position.setValue(objPosition);
    noteTrackMatte.setTrackMatte(instrumentDiagramLayer, TrackMatteType.ALPHA);
    noteTrackMatte.collapseTransformation = true;

    // Creation of the note object
    var noteLayer = patternComp.layers.add(noteObject);
    noteLayer.startTime = objStartTime;
    noteLayer.opacity.setValue(note[2] / 6);
    noteLayer.position.setValue(objPosition);
    noteLayer.collapseTransformation = true;

    // Placement of the note hit comp above the note
    var noteHit = patternComp.layers.add(noteHitComp);
    noteHit.startTime = objStartTime;
    noteHit.position.setValue(objPosition);
    noteHit.collapseTransformation = true;
}

// Create pattern compositions
function patternLayout(patternFolder, layoutKey, instrumentDiagram) {
    var layoutFolder = verifyExist(layoutKey) || project.items.addFolder(layoutKey);
    layoutFolder.parentFolder = patternFolder;
    instrumentDiagram.parentFolder = layoutFolder;
    var instrumentDiagramSize = [instrumentDiagram.width, instrumentDiagram.height];

    for (var patternKey in patternData[layoutKey]) {
        if (patternData[layoutKey].hasOwnProperty(patternKey)) {
            var patternComp = project.items.addComp(patternKey, noteResolution[0], noteResolution[1], 1, noteDuration, patternFPS);
            patternComp.parentFolder = layoutFolder;
            var instrumentDiagramLayer = patternComp.layers.add(instrumentDiagram);
            instrumentDiagramLayer.collapseTransformation = true;

            var notesArray = patternData[layoutKey][patternKey];
            if (notesArray instanceof Array) {
                for (var i = 0; i < notesArray.length; i++) {
                    patternBuilder(patternComp, notesArray[i], instrumentDiagramSize, instrumentDiagramLayer);
                }
            } else {
                $.writeln('Error: patternData for ' + layoutKey + ' - ' + patternKey + ' is not an array.');
            }
        }
    }
}

// Pattern folder and composition creation process
function patternDirectoryCreator() {
    for (var layoutKey in patternData) {
        var footageFile = new File($.fileName).parent.fullName + "/midi_data/visual_layouts/graphics/" + layoutKey + "_layout.ai";
        var instrumentDiagram = verifyExist(footageFile) || project.importFile(new ImportOptions(new File(footageFile)));
        patternLayout(patternFolder, layoutKey, instrumentDiagram);
    }
}

// Recursive function to process patterns
function processPatterns(sectionKey, measureKey, playerKey, player, playerLayout) {
    for (var patternKey in player) {
        if (player.hasOwnProperty(patternKey)) {
            var patternValue = player[patternKey];
            if (patternValue )
            
            // Perform actions on the pattern here
            var pattern = patternData[playerLayout][patternKey]
            // alert("Section: " + sectionKey + ", Measure: " + measureKey + ", Player: " + playerKey + ", Pattern: " + patternKey + ", Value: " + patternValue);
        }
    }
}

// Recursive function to process players
function processPlayers(sectionKey, measureKey, measure) {
    for (var playerKey in measure) {
        if (measure.hasOwnProperty(playerKey)) {
            var player = measure[playerKey];
            
            // Check if the folder for the player already exists, create one if not
            var playerFolder = verifyExist("P" + playerKey) || project.items.addFolder("P" + playerKey);

            // Process patterns for this player
            processPatterns(sectionKey, measureKey, playerKey, player, playerFolder);
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

function assembleMainComp() {
    pass
}

// Main function
function main() {

    // Call functions to load data from reference JSONs
    patternData = loadJSONData('patterns.json');
    playerData = loadJSONData('players.json');
    instrument_info = loadJSONData('midi_data/supported_instruments.json')

    // Import project detail JSON
    var detailData = loadJSONData('project_detail.json');

    // Save project details to variables
    patternFPS = detailData['pattern_fps'];
    projectLength = detailData['project_length'];
    patternLength = detailData['pattern_length'];
    fps = detailData['fps'];
    videoResolution = detailData['video_resolution'];

    // Import timeline JSON
    var timelineData = loadJSONData('timeline.json');

    // Note Object searching from the root of the project
    // var itemNameToCheck = prompt("What is the name of your note object?", "");
    var itemNameToCheck = 'Base Ring';
    noteObject = verifyExist(itemNameToCheck);

    // If the note object does not exist, throw an error
    if (!noteObject || !(noteObject instanceof CompItem)) {
        throw new Error("The note object " + itemNameToCheck + " was not found or is not a composition.");
    }
    
    // Grab the duration of the note object
    noteResolution = [noteObject.width, noteObject.height];
    noteDuration = noteObject.duration + patternLength;
    totalDuration = projectLength + noteDuration;
    noteCeiling = Math.ceil(noteDuration / patternLength);

    // Start Undo Group of everything until construction is finished
    app.beginUndoGroup("Process");

    // Create additional objects per note
    // createNoteObjects();
    // createNoteHit();

    // // Check for main comp first, create it if it doesn't exist
    mainComp = verifyExist("Main Comp") || project.items.addComp(itemNameToCheck, videoResolution[0], videoResolution[1], 1, totalDuration, fps);


    // // Create pattern folder and compositions
    patternFolder = verifyExist("Patterns") || project.items.addFolder("Patterns");
    // patternDirectoryCreator();

    //Begin construction of note-based compositions
    processSections(timelineData);

    assembleMainComp();

    app.endUndoGroup();

}

main();