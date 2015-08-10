$(document).ready(function() {
    $('#create_ad').on('click', function(){
        var data = {};
	data["idcrag"]       = $('#idcrag').val();
	data["title"]        = $('#title').val();
	data["description"]  = $('#description').val();
	data["posting_time"] = $('#posting_time').val();
	data["status"]       = $('#status').val();
	data["idusers"]      = $('#user-select').val();
	data["category"]     = $('#category').val();
	data["area"]         = $('#area').val();
	data["replymail"]    = $('#replymail').val();
	
        $.ajax({
            url: '/ad/add',
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
