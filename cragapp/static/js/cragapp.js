
var dt;
function getTime(){
    $.ajax({
	url: '/time',
	data : {},
	dataType : 'text',
	type: 'get',
	success: function (response) {
	    dt = moment(response, "YYYY-MM-DD HH:mm:ss");
	    function showTime(dt) {	    
		$('.time').html("Server time: "+dt.format("YYYY-MM-DD HH:mm:ss"));
		t = setTimeout(function () {
		    showTime(dt.add(500,'ms'))
		}, 500);};
	    showTime(dt);	    
	}
    })
};
getTime();







