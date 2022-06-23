$('body').on('click', '.short', function(){
    if (!$(this).next().attr('style')){
        $(this).next().css('display', 'table-row')
    }else{
        $(this).next().removeAttr('style')
    }
})
$('body').on('click', '.tab_label', function(e){
    e.preventDefault()
    target_id = '#' + $(this).attr('id').split('_')[0]
    $(this).parent().find('.tab_label').removeClass('active')
    $(this).addClass('active')
    $(this).parent().parent().find('.transit_info_block').removeAttr('style')
    $(target_id).css('display', 'block')
})
$('body').on('click', '.trigger', function (e) {
    console.log('.trigger clicked')
    itemsBlock = $(this).parent().next()
    if (itemsBlock.attr('style')) {
        itemsBlock.removeAttr('style')
    } else {
        itemsBlock.css({
            "padding": "25px",
            "width": "calc(100% - 56px)",
            "height": "auto",
        })
    }
})
function closeModal() {
    location.reload()
}

function showModal(url) {
    $('#modalQuickView').html(null)

    $.ajax({
        url: url,
        type: 'GET',
        success:function(data){
            $('#modalQuickView').html(data);
            $('#modalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        },
        error: function(err){
            $('#modalQuickView').html(err.responseText);
            $('#modalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        },
    });
}
$('a.refresh').click(function(e){
    e.stopImmediatePropagation();
    e.preventDefault();
    $.ajax({
        url: $(this).attr('href'),
        type: 'GET',
        success: function(data){
            document.location.reload(true);
        },
        error: function(error){
            $('#modalQuickView').html(error);
            $('#modalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        },
    })
    return false;
})

$('#modalQuickView').on('click', 'a', function(e){
    e.preventDefault();
    showModal($(this).attr('href'))
    return false;
})

$('table.list_view_table tbody').on('click', 'tr', function(e){
    showModal($(this).attr('href'))
}).on('click', 'a', function(e){
    e.preventDefault();
    showModal($(this).attr('href'))
    return false;
})