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
                console.log(response);
            },
            error: function(e) {
                console.log(e.message);
            }
        });
    });
});
