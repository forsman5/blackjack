// file containing methods for button presses on the game page

function hit() {
  var jqxhr = $.post(window.location.href + "/hit/", function (response) {
    alert(response);
    // TODO: display new game state returned
  });
}

function stand() {
  var jqxhr = $.post(window.location.href + "/stand/", function (response) {
    // TODO: display new game state returned
  });
}

function insure() {
  var jqxhr = $.post(window.location.href + "/insure/", function (response) {
    // TODO: display new game state returned
  });
}

function double() {
  var jqxhr = $.post(window.location.href + "/double/", function (response) {
    // TODO: display new game state returned
  });
}

function split() {
  var jqxhr = $.post(window.location.href + "/split/", function (response) {
    // TODO: display new game state returned
  });
}

// if the game ends, disable all buttons
function disableButtons() {
  // TODO: implement
}
