$(document).ready(function() {
    $('#create_user').on('click', function(){
        var data = {};
    	data["idvpss"] = $('#vps-select').val();
    	data["username"] = $('#username').val();
    	data["password"] = $('#password').val();
    	data["accountID"] = $('#accountID').val();
        $.ajax({
            url: '/user/add',
            data: data,
            dataType : 'text',
            type: 'post',
            success: function (response) {
                if (response == 'User created') {
                    $('#create_user').addClass('shrinked');
                    $('.indicator').addClass('success').addClass('expanded').text('OK!');
                    setTimeout(function(){
                        $('.content').fadeOut(100, function(){
                            window.location = '/users';
                        });
                    }, 300);
                } else {
                    console.log(response);
                }
            },
            error: function(e) {
                console.log(e.message);
                $('#create_user').addClass('shrinked');
                $('.indicator').addClass('error').addClass('expanded').text(':(');
                setTimeout(function(){
                    $('#create_user').removeClass('shrinked');
                    $('.indicator').removeClass('error').removeClass('expanded');
                }, 600);
            }
        });
    });
});
