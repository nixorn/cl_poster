
$(document).ready(function() {
    $('.warning').on('click', function(e){
        e.preventDefault();
        $.get( $(this).attr('href'), function(data) {
            if (data = "VPS deleted") {
                $('.indicator').addClass('expanded').addClass('success').text('Deleted!');
                setTimeout(function(){
                    $('.indicator').removeClass('expanded').removeClass('success');
                }, 400);
                setTimeout(function(){
                    location.reload();
                }, 500);
            }
        });
    });
});
