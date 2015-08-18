
$(document).ready(function() {
    $('.warning').on('click', function(e){
        e.preventDefault();
        $.get( $(this).attr('href'), function(data) {
            if (data = "User deleted") {
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

    $('.sync').on('click', function(e){
        e.preventDefault();
        $('.overlay').css('display','flex').hide().fadeIn();
        $.get( $(this).attr('href'), function(data) {
            $('.overlay').fadeOut();
            if (data = "Ad scraped") {
                $('.indicator').addClass('expanded').addClass('success').text('Scraped!');
                setTimeout(function(){
                    $('.indicator').removeClass('expanded').removeClass('success');
                }, 600);
                setTimeout(function(){
                    window.location = '/ads';
                }, 700);
            }
        });
    });

});
