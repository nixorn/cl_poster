
$(document).ready(function() {
    $('.warning').on('click', function(e){
        e.preventDefault();
        $.get( $(this).attr('href'), function(data) {
            if (data = "Ad deleted") {
                $('.indicator').addClass('expanded').addClass('success').text('Deleted!');
                setTimeout(function(){
                    $('.indicator').removeClass('expanded').removeClass('success');
                }, 400);
                setTimeout(function(){
                    location.reload();
                }, 500);
            } else {
                console.log(data);
            }
        });
    });
    $('.action').on('click', function(e){
        e.preventDefault();
        $('.overlay').css('display','flex').hide().fadeIn();
        $.get( $(this).attr('href'), function(data) {
            $('.overlay').fadeOut();
            if (data = "Success") {
                $('.indicator').addClass('expanded').addClass('success').text('Success!');
                setTimeout(function(){
                    $('.indicator').removeClass('expanded').removeClass('success');
                }, 400);
                setTimeout(function(){
                    location.reload();
                }, 500);
            } else {
                console.log(data);
            }
        });
    });

    function filter_ads(){
	var user_param, category_param, status_param, scheduling_param,duble_param;
	if ($('#user_select').val() == 'all') {user_param='';}
	else {user_param = "idusers="+ $('#user_select').val();};
	
	if ($('#category_select').val() == 'all') {category_param='';}
	else {category_param = 'idcategory='+$('#category_select').val();};

	if ($('#status_select').val() == 'all') {status_param=''}
	else {status_param = 'status='+$('#status_select').val();};

	if ($('#scheduling_select').val() == 'all') {scheduling_param=''}
	else {scheduling_param = 'scheduled_action='+$('#scheduling_select').val();};
	
	duble_param = "is_duble=0"
	str = window.location.href
	url = str.slice(0,str.indexOf("ads")+4);

	url_param_arr = [user_param,
			 category_param,
			 status_param,
			 scheduling_param,
			 duble_param]
	url_param_arr = url_param_arr.filter(function (e){return e != '';});
	
	url = url + url_param_arr.join('&');

	window.location.replace(url);
    };

    $('#user_select').change(filter_ads);
    $('#category_select').change(filter_ads);
    $('#status_select').change(filter_ads);
    $('#scheduling_select').change(filter_ads);

});
