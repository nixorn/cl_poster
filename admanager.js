//

var page   = require('webpage').create(),
    system = require('system'),
    loadInProgress = false,
    crawlIndex = 0,
    CLlogin,
    CLpassword;

page.settings.userAgent = "Mozilla/5.0 (Windows NT 6.1; rv:41.0) Gecko/20100101 Firefox/41.0"

CLlogin    = 'murchendaizer@gmail.com'
CLpassword = 'ltybcxtge'

function loadLoginForm(){
    page.open('https://accounts.craigslist.org/login');};

function fillLoginData(){
    page.evaluate(
	function(CLlogin, CLpassword){
	    document.getElementById('inputEmailHandle').value = CLlogin;
	    document.getElementById('inputPassword').value = CLpassword;
	    }, CLlogin, CLpassword);};

function submitLoginData(){
    page.evaluate(
	function(){
	    document.getElementsByName('login')[0].submit()});};


function finalize(){
    page.render('finalize.png')};



page.onLoadStarted = function() {
  loadInProgress = true;
  console.log("load started");
};

page.onLoadFinished = function() {
  loadInProgress = false;
  console.log("load finished");
};


steps = [loadLoginForm, fillLoginData,submitLoginData,finalize]

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
}, 1500);




