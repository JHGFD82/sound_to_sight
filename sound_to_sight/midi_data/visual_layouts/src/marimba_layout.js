function getCenterPointsOfGroupObjects() {
    var doc = app.activeDocument;

    // Check if there is an active document
    if (!doc) {
        alert('No active document found!');
        return;
    }

    // Check for selection
    if (doc.selection.length === 0 || doc.selection[0].typename != "GroupItem") {
        alert('Please select a group.');
        return;
    }

    var group = doc.selection[0];
    var centers = "{";

    for (var i = 0; i < group.pageItems.length; i++) {
        var item = group.pageItems[i];
        var center = getCenterPoint(item);
        centers += "\"" + (i + 48) + "\": [{\"x\": " + center[0] + ", \"y\": " + center[1] + "}]";
        if (i < group.pageItems.length - 1) {
            centers += ", ";
        }
    }

    centers += "}";

    return centers;
}

function getCenterPoint(item) {
    var x = item.position[0] + item.width / 2;
    var y = -(item.position[1] - item.height / 2);
    return [x, y];
}

// Run the function and output the result
var centerPoints = getCenterPointsOfGroupObjects();
$.writeln(centerPoints);