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

function delCargo(elem) {
    id_id = elem.find('.cargo_hidden_field').first().find('input').first().attr('id')
    parsed_id = id_id.split('-')
    transitNum = parsed_id[1]
    cargoNum = parsed_id[3]
    var deleteItem = false
    if (elem.parent().find('.cargo_form:not([style])').length > 1) {
        deleteItem = true
    } else {
        if (confirm('Вы уверены, что хотите удалить последний груз?\nПри сохранении это приведет к удалению всей перевозки!')) {
            deleteItem = true
        }
    }
    if (deleteItem) {
        id_value = NaN
        $(elem).find('input[type=hidden]').each(function(){
            if ($(this).attr("id").endsWith("id")) {
                id_value = $(this).val()
            }
        })
        if (id_value) {
            elem.css('display', 'none')
            $('#id_transits-' + transitNum + '-cargos-' + cargoNum + '-DELETE').prop('checked', true);
        } else {
            totalCargos = $('#id_transits-' + transitNum + '-cargos-TOTAL_FORMS').val()
            totalCargos--
            $('#id_transits-' + transitNum + '-cargos-TOTAL_FORMS').val(totalCargos)
            parent = $(elem).parent()
            elem.remove()
            ind = 0
            parent.find('div.cargo_form').each(function(){
                e = $(this)
                e_id_id = e.find('.cargo_hidden_field').first().find('input').first().attr('id')
                e_parsed_id = id_id.split('-')
                e_transitNum = parsed_id[1]
                e_cargoNum = parsed_id[3]
                e.find('label').each(function(){
                    attr_for = $(this).attr('for')
                    if (attr_for) {
                        $(this).attr('for', attr_for.replace(/transits-\d-cargos-\d/g, 'transits-' + e_transitNum + '-cargos-' + ind))
                    }
                })
                e.find('input').each(function(){
                    attr_name = $(this).attr('name')
                    attr_id = $(this).attr('id')
                    if (attr_name) {
                        $(this).attr('name', attr_name.replace(/transits-\d-cargos-\d/g, 'transits-' + e_transitNum + '-cargos-' + ind))
                    }
                    if (attr_id) {
                        $(this).attr('id', attr_id.replace(/transits-\d-cargos-\d/g, 'transits-' + e_transitNum + '-cargos-' + ind))
                    }
                })
                e.find('select').each(function(){
                    attr_name = $(this).attr('name')
                    attr_id = $(this).attr('id')
                    if (attr_name) {
                        $(this).attr('name', attr_name.replace(/transits-\d-cargos-\d/g, 'transits-' + e_transitNum + '-cargos-' + ind))
                    }
                    if (attr_id) {
                        $(this).attr('id', attr_id.replace(/transits-\d-cargos-\d/g, 'transits-' + e_transitNum + '-cargos-' + ind))
                    }
                })
                ind++
            })
        }
    }
}

function delTransit(elem) {
    id_id = elem.find('input[type=hidden]').first().attr('id')
    transitNum = id_id.split('-')[1]
    if (elem.parent().find('.transit_form:not([style])').length > 1) {
        deleteItem = true
    } else {
        if (confirm('Вы уверены, что хотите удалить последнюю перевозку?\nПри сохранении это приведет к удалению всего поручения!')) {
            deleteItem = true
        }
    }
    if (deleteItem) {
        id_value = NaN
        $(elem).find('input[type=hidden]').each(function(){
            if ($(this).attr("id").endsWith("id")) {
                id_value = $(this).val()
            }
        })
        if (id_value) {
            elem.css('display', 'none')
            $('#id_transits-' + transitNum + '-DELETE').prop('checked', true);
        } else {
            totalTransits = $('#id_transits-TOTAL_FORMS').val()
            totalTransits--
            $('#id_transits-TOTAL_FORMS').val(totalTransits)
            parent = $(elem).parent()
            elem.remove()
            ind = 0
            parent.find('div.transit_form').each(function(){
                e = $(this)
                e.find('label').each(function(){
                    attr_for = $(this).attr('for')
                    if (attr_for) {
                        $(this).attr('for', attr_for.replace(/transits-\d/g, 'transits-' + ind))
                    }
                })
                e.find('input').each(function(){
                    attr_name = $(this).attr('name')
                    attr_id = $(this).attr('id')
                    if (attr_name) {
                        $(this).attr('name', attr_name.replace(/transits-\d/g, 'transits-' + ind))
                    }
                    if (attr_id) {
                        $(this).attr('id', attr_id.replace(/transits-\d/g, 'transits-' + ind))
                    }
                })
                e.find('select').each(function(){
                    attr_name = $(this).attr('name')
                    attr_id = $(this).attr('id')
                    if (attr_name) {
                        $(this).attr('name', attr_name.replace(/transits-\d/g, 'transits-' + ind))
                    }
                    if (attr_id) {
                        $(this).attr('id', attr_id.replace(/transits-\d/g, 'transits-' + ind))
                    }
                })
                ind++
            })
        }
    }
}
$("body").on('click', '.btn_delete_cargo', function (e) {
    e.preventDefault()
    delCargo($(this).parents(".cargo_form"))
})

$("body").on('click', '.btn_delete_transit', function (e) {
    e.preventDefault()
    delTransit($(this).parents(".transit_form"))
})

$('body').on('click', '.btn_add_cargo', function(e){
    e.preventDefault()
    table = $(this).parent().parent().find('.cargo_table')
    transitNum = table.find('input[type=hidden]').attr('name').split('-')[1]
    formNum = table.find('.cargo_form').length
    newCargo = newCargoGlobal.replace(/__tprefix__/g, transitNum).replace(/__prefix__/g, formNum)
    table.append(newCargo)
    totalCargos = $("#id_transits-" + transitNum + "-cargos-TOTAL_FORMS").val()
    totalCargos++
    $("#id_transits-" + transitNum + "-cargos-TOTAL_FORMS").val(totalCargos)
})

$('.btn_add_transit').on('click', function(e){
    e.preventDefault()
    table = $('#transit_forms')
    formNum = $('.transit_form').length
    totalTransits = $("#id_transits-TOTAL_FORMS").val()
    newTransit = newTransitGlobal.replace(/__tprefix__/g, formNum)
    table.append(newTransit)
    totalTransits++
    $("#id_transits-TOTAL_FORMS").val(totalTransits)
    $(this).parent().parent().find('.btn_add_cargo').last().click()
})

$('body').on('click', '.swap_forms', function(){
    sender_inputs = $(this).prev().find('input')
    receiver_inputs = $(this).next().find('input')
    for (let i = 0; i < sender_inputs.length; i++) {
        sender_val = sender_inputs[i].value
        receiver_val = receiver_inputs[i].value
        $(sender_inputs[i]).val(receiver_val)
        $(receiver_inputs[i]).val(sender_val)
    }
})

$('body').on('click', '.copy_transit', function(){
    clonedFormInputs = $(this).parent().find('input')
    clonedFormSelects = $(this).parent().find('select')
    table = $('#transit_forms')
    formNum = $('.transit_form').length
    totalTransits = $("#id_transits-TOTAL_FORMS").val()
    newTransit = $($.parseHTML(newTransitGlobal.replace(/__tprefix__/g, formNum)))
    table.append(newTransit)
    cargos_num = $(this).parent().find('.cargo_form').length
    while (newTransit.find('.cargo_form').length < cargos_num) {
        newTransit.find('.btn_add_cargo').last().click()
    }

    newFormInputs = newTransit.find('input')
    for (let i = 0; i < clonedFormInputs.length; i++) {
        cloned_item = $(clonedFormInputs[i])
        new_item = $(newFormInputs[i])
        if (
            !cloned_item.attr('id').endsWith('-id') &&
            !cloned_item.attr('id').endsWith('DELETE') &&
            !cloned_item.attr('id').endsWith('INITIAL_FORMS') &&
            !cloned_item.attr('id').endsWith('sub_number')
        ) {
            new_item.val(cloned_item.val())
        }
    }
    newFormSelects = newTransit.find('select')
    for (let i = 0; i < clonedFormSelects.length; i++) {
        $(newFormSelects[i]).val($(clonedFormSelects[i]).val())
    }
    totalTransits++
    $("#id_transits-TOTAL_FORMS").val(totalTransits)
})