var page   = require('webpage').create(),
    system = require('system'),
    fs = require('fs'),
    loadInProgress = false,
    crawlIndex = 0,
    url_to_confirm;


page.settings.userAgent = "Mozilla/5.0 (Windows NT 6.1; rv:41.0) Gecko/20100101 Firefox/41.0"

phantom.onError = function(msg, trace) {
  var msgStack = ['PHANTOM ERROR: ' + msg];
  if (trace && trace.length) {
    msgStack.push('TRACE:');
    trace.forEach(function(t) {
      msgStack.push(' -> ' + (t.file || t.sourceURL) + ': ' + t.line + (t.function ? ' (in function ' + t.function +')' : ''));
    });
  }
  console.error(msgStack.join('\n'));
  phantom.exit(1);
};


if (system.args.length < 2){
    console.log("Give the confirmation url!\n" +
	       "Call should be like\n" +
		"phantomjs confirm.js http://craigslist.org/confirmation/url");
    phantom.exit(1);
}

url_to_confirm = system.args[1];


function loadConfirnPage(){
    page.open(url_to_confirm);};

function sumbitTOU(){
    page.evaluate(
	function(){
	    if (document.findElementsByTagName("form").length > 0 ){
		document.findElementsByTagName("form")[0].submit()
	    }
	}
    )
}


function finalizeConfirm(){
        fs.write('./logs/confirm.html', page.content, 'w');};


page.onLoadStarted = function() {
    loadInProgress = true;
    console.log("load started");
};

page.onLoadFinished = function() {
    loadInProgress = false;
    console.log("load finished");
};


steps = [loadConfirnPage,finalizeConfirm]

interval = setInterval(function() {
    if (!loadInProgress && typeof steps[crawlIndex] == "function") {
	console.log("step " + (crawlIndex + 1));
	steps[crawlIndex]();
	crawlIndex++;
    }
    if (typeof steps[crawlIndex] != "function") {
	console.log("test complete!");
	phantom.exit();
    }
}, 3000);
