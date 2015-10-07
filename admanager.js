//

var page   = require('webpage').create(),
    system = require('system'),
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
    license_info;




page.settings.userAgent = "Mozilla/5.0 (Windows NT 6.1; rv:41.0) Gecko/20100101 Firefox/41.0"

CLlogin    = 'murchendaizer@gmail.com';
CLpassword = 'ltybcxtge';
area_shortcode = 'isp'; //long island
service_code = 83; //skilled trade
title = 'Haskeller';            
body = 'Good (or bad?) haskell programmer at your service';             
specific_location = 'Babylon';
postal = '11930';          
is_licensed = 'no';
license_info = 'Where I can take a haskell license, guys?';


function loadLoginForm(){
    page.open('https://accounts.craigslist.org/login');};

function fillLoginData(){
    page.evaluate(
	function(CLlogin, CLpassword){
	    document.getElementById('inputEmailHandle').value = CLlogin;
	    document.getElementById('inputPassword').value = CLpassword;
	}, CLlogin, CLpassword);
    page.render('1_login_form.png');
}

function submitLoginData(){
    page.evaluate(
	function(){
	    document.getElementsByName('login')[0].submit()});}
    
function setAreaSelect(){
    page.evaluate(
	function(area_shortcode){
	    document.getElementsByName('areaabb')[0].value = area_shortcode}, area_shortcode);
    page.render('2_area_select.png');}

function submitNewPosting(){
    page.evaluate(
	function(){
	    document.getElementsByClassName('new_posting_thing')[0].submit()});

}


function selectServices1(){
    page.evaluate(
	function (){
	    document.querySelectorAll("input[value=so]")[0].checked = true});
    page.render('3_services.png')}

function selectServices2(){
    page.evaluate(
	function (service_code){
	    document.querySelectorAll("input[value='"+service_code+"']")[0].checked = true}, service_code);
    page.render('4_services.png')}


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
    page.render('5_ad_body.png');}

function submitAdBody(){
    page.evaluate(
	function(){
	    document.getElementById('postingForm').submit()})}


function publish(){
    page.render('6_pre_publish.png');
    page.evaluate(
	function(){
	    document.getElementsByTagName('form')[0].submit()})}

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




