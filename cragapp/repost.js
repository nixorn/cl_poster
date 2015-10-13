var page   = require('webpage').create(),
    system = require('system'),
    loadInProgress = false,
    crawlIndex = 0,
    CLlogin,
    CLpassword,
    idcrag;


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


if (system.args.length < 4){
    console.log("Give the CL username, password and id of ad for reposting!\n" +
	       "Call should be like\n" +
		"phantomjs repost.js username@example.com password 123456789");
    phantom.exit(1);
}

console.log(system.args)
//read config

config = JSON.parse(fs.open(system.args[1], "r").read());
imagename_array = system.args.slice(1, system.args)



CLlogin    = system.args[1];
CLpassword = system.args[2];
idcrag     = system.args[4];




function loadLoginForm(){
    page.open('https://accounts.craigslist.org/login');};

function fillLoginData(){
    
	page.evaluate(
	    function(CLlogin, CLpassword){
		document.getElementById('inputEmailHandle').value = CLlogin;
		document.getElementById('inputPassword').value = CLpassword;
	    }, CLlogin, CLpassword);

    fs.write('./logs/1_login_form.html', page.content, "w");
    

}

function submitLoginData(){
    page.evaluate(
	function(){
	    document.getElementsByName('login')[0].submit()});}


function submitRepost(){
    page.evaluate(
	function (idcrag){
	    allForms = document.getElementsByTagName("form");
	    
	    for (var i=0, i < allForms.length ){
		if (allForms[i].getAttribute("action").indexOf(idcrag) > -1
		    && allForms[i].getElementsByTagName("input")[0].value == "repost")
		{
		    allForms[i].submit();
		}
	    }
	    
	},
	idcrag
    )
}

function submitAdBody(){
    page.evaluate(
	function(){
	    document.getElementById('postingForm').submit()})}

function publish(){
    fs.write('./logs/7_pre_publish.html', page.content, 'w');

    page.evaluate(
	function(){
	    document.getElementsByTagName('form')[0].submit()})}

function post_publish(){

    fs.write('./logs/8_post_publish.html', page.content, 'w');
};


steps = [loadLoginForm,
	 fillLoginData,
	 submitLoginData,
	 submitRepost,
	 submitAdBody,
	 publish,
	 post_publish]



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
}, 5000);




