$(document).ready(function() {
    $('#edit_ad').on('click', function(){
        var data = {};
	data["idads"]        = $("#idads").val();
        data["description"]  = $("#description").val();
        data["title"]        = $("#title").val();
        data["posting_time"] = $("#posting_time").val();
        data["status"]       = $("#status").val();
        data["idusers"]      = $("#user-select").val();
        data["category"]     = $("#category").val();
        data["area"]         = $("#area").val();
        data["replymail"]    = $("#replymail").val();
        $.ajax({
            url: '/ad/update',
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
