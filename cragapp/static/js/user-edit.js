$(document).ready(function() {
    $('#edit_user').on('click', function(){
        var data = {};
    	data["idusers"] = $('#idusers').val();
    	data["idvpss"] = $('#vps-select').val();
    	data["username"] = $('#username').val();
    	data["password"] = $('#password').val();
    	data["mail_pass"] = $('#mail_pass').val();
	
        $.ajax({
            url: '/user/update',
            data: data,
            dataType : 'text',
            type: 'post',
            success: function (response) {
                if (response == 'UPDATED') {
                    $('#edit_user').addClass('shrinked');
                    $('.indicator').addClass('success').addClass('expanded');
                    setTimeout(function(){
                        $('.content').fadeOut(200, function(){
                            window.location = '/users';
                        });
                    }, 400);
                } else {
                    console.log(response);
                }
            },
            error: function(e) {
                console.log(e.message);
            }
        });
    });
});
