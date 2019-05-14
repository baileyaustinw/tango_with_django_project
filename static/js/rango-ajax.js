$('#likes').click(function(){
    console.log('running');
    var catid;
    catid = $(this).attr('data-catid');

    $.get('/rango/like/', {category_id: catid}, function(data){
        $('#like_count').html(data);
        $('#likes').hide();
    });
});