
$(document).ready(function() {
    $('.warning').on('click', function(e){
        e.preventDefault();
        $.get( $(this).attr('href'), function(data) {
            if (data = "Ad deleted") {
                $('.indicator').addClass('expanded').addClass('success').text('Deleted!');
                setTimeout(function(){
                    $('.indicator').removeClass('expanded').removeClass('success');
                }, 400);
                setTimeout(function(){
                    location.reload();
                }, 500);
            } else {
                console.log(data);
            }
        });
    });
    $('.action').on('click', function(e){
        e.preventDefault();
        $('.overlay').css('display','flex').hide().fadeIn();
        $.get( $(this).attr('href'), function(data) {
            $('.overlay').fadeOut();
            if (data = "Success") {
                $('.indicator').addClass('expanded').addClass('success').text('Success!');
                setTimeout(function(){
                    $('.indicator').removeClass('expanded').removeClass('success');
                }, 400);
                setTimeout(function(){
                    location.reload();
                }, 500);
            } else {
                console.log(data);
            }
        });
    });





});
