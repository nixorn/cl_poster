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
                console.log(response);
            },
            error: function(e) {
                console.log(e.message);
            }
        });
    });
});
