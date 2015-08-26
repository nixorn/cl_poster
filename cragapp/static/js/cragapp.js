(function () {
    function showTime() {
	$.ajax({
            url: '/time',
	    data : {},
            dataType : 'text',
            type: 'get',
            success: function (response) {
		$('.time').html("Server time: "+response);}});
	t = setTimeout(function () {
	    showTime()
	}, 5000);}
    
    showTime();}
)();

