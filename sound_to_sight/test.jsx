// Global variables
var project = app.project;
var patternData, playerData, patternFPS, projectLength, patternLength, noteCeiling, fps, videoResolution, noteObject, noteResolution, noteDuration, totalDuration, patternFolder;

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
    return noteHitComp;
}

// Assemble patterns with supplied note information
function patternBuilder(patternComp, note, instrumentDiagramSize) {

    // NoteLayer properties for use with multiple objects per note
    var noteLayerX = note[4][0] + (patternComp.width / 2) - (instrumentDiagramSize[0] / 2);
    var noteLayerY = note[4][1] + (patternComp.height / 2) - (instrumentDiagramSize[1] / 2);
    var objPosition = [noteLayerX, noteLayerY];
    var objStartTime = note[0] / patternFPS;

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

function instrumentLayoutMatte(instrumentDiagramLayer, note) {
    var mask = instrumentDiagramLayer.property("Masks").addProperty("Mask");
    var maskShape = new Shape();
    var vertices = [];
    var numPoints = 18; // Number of points to define the circle
    var angleStep = Math.PI * 2 / numPoints;
    for (var i = 0; i < numPoints; i++) {
        var angle = angleStep * i;
        var x = note[4][0] + Math.cos(angle) * (345 / 2);
        var y = note[4][1] + Math.sin(angle) * (345 / 2);
        vertices.push([x, y]);
    }
    maskShape.vertices = vertices;
    maskShape.closed = true;
    mask.property("ADBE Mask Shape").setValue(maskShape);
    mask.property("ADBE Mask Feather").setValue([345 / 2, 345 / 2]);
    var maskOpacity = mask.property("ADBE Mask Opacity");
    maskOpacity.setValueAtTime((note[0] - 1) / patternFPS, 0);
    maskOpacity.setValueAtTime(note[0] / patternFPS, 75);
    maskOpacity.setValueAtTime((note[0] + 15) / patternFPS, 0);
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
                    instrumentLayoutMatte(instrumentDiagramLayer, notesArray[i]);
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

// Creation of pattern loop compositions for player-based timeline
function patternLoopConstructor(patternRepetitions, patternKey) {
    // Check first if the pattern exists, throw an error if not
    var patternComp = verifyExist(patternKey);
    if (!patternComp) {
        throw new Error("Pattern " + patternKey + " does not exist in the project. Check that all patterns listed in the timeline.JSON file are listed in the patterns.JSON file to ensure all patterns are created.");
    }

    // Check for the existence of the needed pattern repetition comp before creating one
    if (patternRepetitions > noteCeiling) {
        var patternLoopName = patternKey + "-loop";
        var loopNumber = noteCeiling;
    } else {
        var patternLoopName = patternKey + "-" + patternRepetitions;
        var loopNumber = patternRepetitions;
    }
    var patternLoopExists = verifyExist(patternLoopName);
    if (patternLoopExists) {return patternLoopExists};

    // Create the loop composition if none exist
    var patternLoopDuration = patternLength * (noteCeiling - 1) + noteDuration;
    var patternLoopContainer = project.items.addComp(patternLoopName, noteResolution[0], noteResolution[1], 1, patternLoopDuration, patternFPS);
    patternLoopContainer.parentFolder = patternFolder;

    for (var i = 0; i < loopNumber; i++) {
        var loopObject = patternLoopContainer.layers.add(patternComp);
        loopObject.collapseTransformation = true;
        loopObject.startTime = patternLength * i;
    }
    return patternLoopContainer;
}

// Recursive function to process patterns
function processPatterns(measureKey, playerKey, player) {
    // Check for existence of player composition, create one if none
    var playerComp = verifyExist("P" + playerKey + " comp");
    if (!playerComp) {
        throw new Error("P" + playerKey + " comp does not exist in this project. Check the processPlayers function for any processing issues.")
    }

    // Assemble patterns in player composition
    for (var patternKey in player) {
        if (player.hasOwnProperty(patternKey)) {
            var patternRepetitions = player[patternKey];
            var patternLoopContainer = patternLoopConstructor(patternRepetitions, patternKey);
            var patternLoopLayer = playerComp.layers.add(patternLoopContainer);
            patternLoopLayer.collapseTransformation = true;
            var videoMeasureTime = measureKey - 1;
            patternLoopLayer.startTime = videoMeasureTime * patternLength;

            // If this is a looped pattern, set up the looping structure
            if (patternRepetitions > noteCeiling) {
                var inPointValue = (videoMeasureTime + noteCeiling - 1) * patternLength;
                var outPointValue = (videoMeasureTime + patternRepetitions) * patternLength;
                patternLoopLayer.outPoint = videoMeasureTime * patternLength + (noteCeiling - 1) * patternLength;
                var patternLoopLayerEnd = patternLoopLayer.duplicate();
                patternLoopLayerEnd.startTime = outPointValue - (noteCeiling * patternLength);
                patternLoopLayerEnd.inPoint = outPointValue;
                patternLoopLayerEnd.outPoint = patternLoopLayerEnd.startTime + patternLoopLayerEnd.source.duration;
                var loopingLayer = patternLoopLayer.duplicate();
                loopingLayer.timeRemapEnabled = true;
                var loopingLayerRemap = loopingLayer.property("ADBE Time Remapping");
                var loopExpr = "loopOut(\"cycle\")";
                loopingLayerRemap.expression = loopExpr;
                loopingLayerRemap.removeKey(1);
                loopingLayerRemap.setValueAtTime(inPointValue, (noteCeiling - 1) * patternLength);
                loopingLayerRemap.setValueAtTime(inPointValue + patternLength, (noteCeiling - 1) * patternLength + patternLength);
                loopingLayerRemap.removeKey(3);
                loopingLayer.inPoint = inPointValue;
                loopingLayer.outPoint = outPointValue;
            }
        }
    }
}

// Recursive function to process players
function processPlayers(measureKey, measure) {
    for (var playerKey in measure) {
        if (measure.hasOwnProperty(playerKey)) {
            var player = measure[playerKey];
            
            // Check if the folder and pattern assembly composition for the player already exists, create one if not
            var playerFolder = verifyExist("P" + playerKey) || project.items.addFolder("P" + playerKey);
            var playerComp = verifyExist("P" + playerKey + " comp") || project.items.addComp("P" + playerKey + " comp", noteResolution[0], noteResolution[1], 1, totalDuration, patternFPS);
            playerComp.parentFolder = playerFolder;

            // Process patterns for this player
            processPatterns(measureKey, playerKey, player);
        }
    }
}

// Recursive function to process measures
function processMeasures(section) {
    for (var measureKey in section) {
        if (section.hasOwnProperty(measureKey)) {
            var measure = section[measureKey];
            
            // Perform actions on measures here (if needed)

            // Process players for this measure
            processPlayers(measureKey, measure);
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
            processMeasures(section);
        }
    }
}

function assembleMainComp() {
    for (playerKey in playerData) {
        var playerComp = verifyExist("P" + playerKey + " comp");
        mainCompPlayer = mainComp.layers.add(playerComp)
        mainCompPlayer.collapseTransformation = true;
    }
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
    var itemNameToCheck = "Base Ring";
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
    noteHitComp = verifyExist("Note Hit") || createNoteHit();

    // // Check for main comp first, create it if it doesn't exist
    mainComp = verifyExist("Main Comp") || project.items.addComp("Main Comp", videoResolution[0], videoResolution[1], 1, totalDuration, fps);

    // // Create pattern folder and compositions
    patternFolder = verifyExist("Patterns") || project.items.addFolder("Patterns");
    patternDirectoryCreator();

    //Begin construction of note-based compositions
    processSections(timelineData);

    assembleMainComp();

    app.endUndoGroup();

}

main();