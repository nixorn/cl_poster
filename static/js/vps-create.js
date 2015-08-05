$(document).ready(function() {
    $('#create').on('click', function(){
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
                console.log(response);
            },
            error: function(e) {
                console.log(e.message);
            }
        });
    });
});
