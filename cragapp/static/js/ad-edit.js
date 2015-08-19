$(document).ready(function() {
    $('#edit_ad').on('click', function(){
        var data = {};
    	data["idads"]        = $("#idads").val();
    	data["idcrag"]       = $("#idcrag").val();
        data["description"]  = document.getElementById('description').value;
        data["title"]        = $("#title").val();
        data["posting_time"] = $("#posting_time").val();
        data["status"]       = $("#status").val();
        data["idusers"]      = $("#user-select").val();
        data["category"]     = $("#category").val();
        data["area"]         = $("#area").val();
        data["replymail"]    = $("#replymail").val();
        data["contact_phone"]= $('#contact_phone').val();
        data["contact_name"] = $('#contact_name').val();
        data["postal"]       = $('#postal').val();
        data["specific_location"]= $('#specific_location').val();
        data["has_license"]  = $('#has_license').val();
        data["license"]      = $('#license').val();

        $.ajax({
            url: '/ad/update',
            data: data,
            dataType : 'text',
            type: 'post',
            success: function (response) {
                if (response == 'UPDATED') {
                    $('#edit_ad').addClass('shrinked');
                    $('.indicator').addClass('success').addClass('expanded').text('OK!');
                    setTimeout(function(){
                        $('#edit_ad').removeClass('shrinked');
                        $('.indicator').removeClass('success').removeClass('expanded');
                    }, 400);
                } else {
                    console.log(response);
                }
            },
            error: function(e) {
                $('#edit_ad').addClass('shrinked');
                $('.indicator').addClass('error').addClass('expanded').text(':(');
                setTimeout(function(){
                    $('#edit_ad').removeClass('shrinked');
                    $('.indicator').removeClass('error').removeClass('expanded');
                }, 400);
                console.log(e.message);
            }
        });
    });
    var form = document.getElementById('images_upload');
    var fileSelect = document.getElementById('image_to_upload');
    var uploadButton = document.getElementById('image_upload_submit');
    form.onsubmit = function(event) {
	event.preventDefault();

	// Update button text.
	uploadButton.innerHTML = 'Uploading...';

	// Get the selected files from the input.
	var files = fileSelect.files;

	// Create a new FormData object.
	var formData = new FormData();
	for (var i = 0; i < files.length; i++) {
	    var file = files[i];

	    // Check the file type.
	    if (!file.type.match('image.*')) {
		continue;
	    };

	    // Add the file to the request.
	    formData.append('images[]', file, file.name);
	};
	var xhr = new XMLHttpRequest();
	xhr.open('POST', '/upload_images', true);
	xhr.onload = function () {
	    if (xhr.status === 200) {
		// File(s) uploaded.
		uploadButton.innerHTML = 'Upload';
	    } else {
		alert('An error occurred!');
	    };
	};
	formData.append('idads',$("#idads").val());
	xhr.send(formData);
    };
});
