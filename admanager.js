//

var page   = require('webpage').create(),
    system = require('system'),
    address,
    qry;

address = system.args[1];
qry = system.args[2];



page.onLoadFinished = function(){
    page.render('1.png');
    //console.log(page.content);

    page.evaluate( function(qry){document.getElementById('query').value = qry}, qry);

    page.render('2.png');

    page.evaluate(
	function(){document.getElementById('search').submit();});

    page.render('3.png');
    phantom.exit();
}

if (system.args.length < 3){
    console.log('you should give link and the query')
    phantom.exit()
} else {
    console.log(address);
    console.log(qry);
    page.open(address);
}




