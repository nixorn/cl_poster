var page   = require('webpage').create(),
    system = require('system'),
    fs = require('fs'),
    loadInProgress = false,
    crawlIndex = 0,
    CLlogin,
    CLpassword,
    area_shortcode,
    service_code,
    title,            
    body,             
    specific_location,
    postal,           
    is_licensed,      
    license_info,
    config;


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
    console.log("Give at least name of the config file!\n" +
	       "Call should be like\n" +
		"phantomjs add_ad.js config.json");
    phantom.exit(1);
}


//read config

config = JSON.parse(fs.open(system.args[1], "r").read());




CLlogin    = config["username"];
CLpassword = config["password"];
area_shortcode = config["area"]; //long island for example
service = config["service"];
service_code = config["category"]; //skilled trade
title = config["title"];            
body = config["body"];
specific_location = config["specific_location"];
postal = config["postal"];          
is_licensed = config["no"];
license_info = config["license_info"];



function loadLoginForm(){
    page.open('https://accounts.craigslist.org/login');};

function fillLoginData(){
    page.evaluate(
	function(CLlogin, CLpassword){
	    document.getElementById('inputEmailHandle').value = CLlogin;
	    document.getElementById('inputPassword').value = CLpassword;
	}, CLlogin, CLpassword);
    page.render('./logs/1_login_form.png');
    fs.write('./logs/1_login_form.html', page.content, "w");
}

function submitLoginData(){
    page.evaluate(
	function(){
	    document.getElementsByName('login')[0].submit()});}

function setAreaSelect(){
    page.evaluate(
	function(area_shortcode){
	    document.getElementsByName('areaabb')[0].value = area_shortcode}, area_shortcode);
    page.render('./logs/2_area_select.png');
    fs.write('./logs/2_area_select.html', page.content, 'w');}

function submitNewPosting(){
    page.evaluate(
	function(){
	    document.getElementsByClassName('new_posting_thing')[0].submit()});

}


function selectServices1(){
    page.evaluate(
	function (service){
	    document.querySelectorAll("input[value="+service+"]")[0].checked = true}, service);
    page.render('./logs/3_services.png')
    fs.write('./logs/3_services.html', page.content, 'w');
}

function selectServices2(){
    page.evaluate(
	function (service_code){
	    document.querySelectorAll("input[value='"+service_code+"']")[0].checked = true}, service_code);
    page.render('./logs/4_services.png');
    fs.write('./logs/4_services.html', page.content, 'w');}


function submitServices(){
    page.evaluate(
	function(){
	    document.querySelectorAll('form[class="catpick picker"]')[0].submit()})}

function fillAdBody(){
    page.evaluate(
	function(title, body, specific_location, postal, is_licensed, license_info){
	    
	    document.getElementById('PostingTitle').value = title;
	    document.getElementById('PostingBody').value = body;
	    document.getElementById('GeographicArea').value = specific_location;
	    document.getElementById('postal_code').value = postal;

	    if (is_licensed == 'yes') {
		document.getElementById('lic').checked = true;
		document.getElementById('license_info').value = license_info;
		
	    } else{document.getElementById('nolic').checked = true;}
	    
	},title,body,specific_location,	postal,is_licensed,license_info);
    page.render('./logs/5_ad_body.png');
    fs.write('./logs/5_body.html', page.content, 'w');}

function submitAdBody(){
    page.evaluate(
	function(){
	    document.getElementById('postingForm').submit()})}

function handleImages(){
    fs.write('./logs/6_pre_image.html', page.content, 'w');

    page.evaluate(
	function(){
	    document.getElementsByTagName('form')[1].submit();   })}

function publish(){
    fs.write('./logs/7_pre_publish.html', page.content, 'w');

    page.evaluate(
	function(){
	    document.getElementsByTagName('form')[0].submit()})}

function finalize(){
    page.render('./logs/finalize.png');
    fs.write('./logs/finalize.html', page.content, 'w');
};



page.onLoadStarted = function() {
    loadInProgress = true;
    console.log("load started");
};

page.onLoadFinished = function() {
    loadInProgress = false;
    console.log("load finished");
};


steps = [loadLoginForm,
	 fillLoginData,
	 submitLoginData,
	 setAreaSelect,
	 submitNewPosting,
	 selectServices1,
	 submitServices,
	 selectServices2,
	 submitServices,
	 fillAdBody,
	 submitAdBody,
	 handleImages,
	 publish,
	 finalize]

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



