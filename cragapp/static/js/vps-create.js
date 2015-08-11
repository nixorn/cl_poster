$(document).ready(function() {
    $('#create_vps').on('click', function(e){
        e.preventDefault();
        var data = {};
        data["ip"] = $('#ip').val();
        data["port"] = $('#port').val();
        data["user"] = $('#user').val();
        data["password"] = $('#password').val();
        $.ajax({
            url: '/vps/add',
            data: data,
            dataType : 'text',
            type: 'post',
            success: function (response) {
                if (response == 'VPS created') {
                    $('#create_vps').addClass('shrinked');
                    $('.indicator').addClass('success').addClass('expanded').text('OK!');
                    setTimeout(function(){
                        $('.content').fadeOut(100, function(){
                            window.location = '/vps';
                        });
                    }, 300);
                }
            },
            error: function(e) {
                console.log(e.message);
                $('#create_vps').addClass('shrinked');
                $('.indicator').addClass('error').addClass('expanded').text(':(');
                setTimeout(function(){
                    $('#create_vps').removeClass('shrinked');
                    $('.indicator').removeClass('error').removeClass('expanded');
                }, 600);
            }
        });
    });
});
