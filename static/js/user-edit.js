$(document).ready(function() {
    $('#edit_user').on('click', function(){
        var data = {};
	data["idusers"] = $('#idusers').val(); 
	data["idvpss"] = $('#vps-select').val(); 
	data["username"] = $('#username').val();
	data["password"] = $('#password').val();
	data["accountID"] = $('#accountID').val();
        $.ajax({
            url: '/user/update',
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
