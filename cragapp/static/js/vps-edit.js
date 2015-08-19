$(document).ready(function() {
    $('#edit_vps').on('click', function(){
        var data = {};
        data["idvpss"]   = $('#idvpss').val();
        data["ip"]       = $('#ip').val();
        data["port"]     = $('#port').val();
        data["user"]     = $('#user').val();
        data["password"] = $('#password').val();
        $.ajax({
            url: '/vps/update',
            data: data,
            dataType : 'text',
            type: 'post',
            success: function (response) {
                if (response == 'UPDATED') {
                    $('#edit_vps').addClass('shrinked');
                    $('.indicator').addClass('success').addClass('expanded');
                    setTimeout(function(){
                        $('.content').fadeOut(200, function(){
                            window.location = '/vps';
                        });
                    }, 400);
                }
            },
            error: function(e) {
                console.log(e.message);
            }
        });
    });
});
