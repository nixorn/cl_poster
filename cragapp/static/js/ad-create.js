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
                if (response == 'Ad created') {
                    $('#create_ad').addClass('shrinked');
                    $('.indicator').addClass('success').addClass('expanded').text('OK!');
                    setTimeout(function(){
                        $('.content').fadeOut(100, function(){
                            window.location = '/ads';
                        });
                    }, 300);
                } else {
                    console.log(response);
                }
            },
            error: function(e) {
                console.log(e.message);
                $('#create_ad').addClass('shrinked');
                $('.indicator').addClass('error').addClass('expanded').text(':(');
                setTimeout(function(){
                    $('#create_ad').removeClass('shrinked');
                    $('.indicator').removeClass('error').removeClass('expanded');
                }, 600);
            }
        });
    });
});
