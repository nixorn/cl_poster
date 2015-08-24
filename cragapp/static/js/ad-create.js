$(document).ready(function() {
    $(function() {
	$('#datetimepicker1').datetimepicker();
	$('#datetimepicker1').data('DateTimePicker').date(
	    new Date());
    });
    $('#create_ad').on('click', function(){
        var data = {};
	data["idcrag"]       = $("#idcrag").val();
        data["description"]  = document.getElementById('description').value;
        data["title"]        = $("#title").val();
        data["posting_time"] = $('#datetimepicker1').data("DateTimePicker").date().format("YYYY-MM-DD HH:mm");
	data["scheduled_action"] = $('#scheduled_action').val();
	data["repost_timeout"] = $('#repost_timeout').val();
        data["idusers"]      = $("#user-select").val();
        data["category"]     = $("#category").val();
        data["area"]         = $("#area").val();
        data["contact_phone"]= $('#contact_phone').val();
        data["contact_name"] = $('#contact_name').val();
        data["postal"]       = $('#postal').val();
        data["specific_location"]= $('#specific_location').val();
        data["has_license"]  = $('#has_license').val();
        data["license"]      = $('#license').val();

        $.ajax({
            url: '/ad/add',
            data: data,
            dataType : 'text',
            type: 'post',
            success: function (response) {
                console.log('OK');
                console.log(response);
                $('#create_ad').addClass('shrinked');
                $('.indicator').addClass('success').addClass('expanded').text('OK!');
                setTimeout(function(){
                    $('.content').fadeOut(100, function(){
                        window.location = '/ad/edit/'+response;
                    });
                }, 300);
            },
            error: function(e) {
                console.log('ERROR');
                console.log(e.message);
                $('#create_ad').addClass('shrinked');
                $('.indicator').addClass('error').addClass('expanded').text(':(');
                setTimeout(function(){
                    $('#create_ad').removeClass('shrinked');
                    $('.indicator').removeClass('error').removeClass('expanded');
                }, 600);
            }
        });
    });
});
