$.ajaxSetup({
    beforeSend: function (xhr)
    {
        xhr.setRequestHeader("Cache-Control", "no-cache");
        xhr.setRequestHeader("Pragma", "no-cache");
    },
});
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

function closeSubModal() {
    $('#subModalQuickView').html(null)
    $('#subModalWindow').removeAttr('style')
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

function showSubModal(url) {
    $('#subModalQuickView').html(null)

    $.ajax({
        url: url,
        type: 'GET',
        success:function(data){
            $('#subModalQuickView').html(data);
            $('#subModalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        },
        error: function(err){
            $('#subModalQuickView').html(err.responseText);
            $('#subModalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        },
    });
}

function update_select_links(){
    client_id = $('#id_client').val()
    $('body').find('span.cp_select').each(function(){
        $(this).attr('client_id', client_id)
    })
}

function update_contacts_select_link(link){
    if (link.attr('contacts_type') == 'from_contacts') {
        cp_type = 'sender'
    } else {
        cp_type = 'receiver'
    }
    cp_input_id = '#id_' + link.attr('transit_prefix') + '-' + cp_type
    cp_id = $(cp_input_id).val()
    if (cp_id) {
        link.attr('cp_id', cp_id)
        if ($('#' + link.attr('transit_prefix') + '-' + link.attr('contacts_type') + '_display').children().length > 0) {
            link.html('Изменить')
        }
    }
}

function update_contacts_select_links(){
    $('body').find('span.contacts_select').each(function(){
        update_contacts_select_link($(this))
    })
}

$('#modalQuickView').on('change', '#id_client', function(e) {
    update_select_links()
})

$('#subModalQuickView').on('keyup', '#search_input', function(){
    search_area = $('#subModalQuickView div.searchable')
    filter = $(this).val().toUpperCase()
    search_area.children().each(function(){
        if ($(this).find('label').html().toUpperCase().indexOf(filter) > -1) {
            $(this).removeAttr('style')
        } else {
            $(this).css('display', 'none')
        }
    })
})

function delay(time) {
  return new Promise(resolve => setTimeout(resolve, time));
}

var clicked_sub_link

$('#modalQuickView').on('click', 'span.cp_select', function(e){
    cp_type = $(this).attr('cp_type')
    transit_prefix = $(this).attr('transit_prefix')
    client_id = $(this).attr('client_id')
    clicked_sub_link = $(this)
    if (!client_id) {
        $('#modalQuickView').animate({
            scrollTop: $('#id_client').offset().top
        }, 1000)
        delay(500).then(() => $('#id_client').css('border-color', 'red'))
        delay(1500).then(() => $('#id_client').removeAttr('style'))
    } else {
        selectCP(client_id, transit_prefix, cp_type)
    }
})

function selectCP(client_id, prefix, cp_type) {
    $('#subModalQuickView').html(null)
    url = '/profile/clients/' + client_id + '/cp_select'

    $.ajax({
        url: url,
        type: 'GET',
        success:function(data){
            content = $(data)
            content.find('#transit_prefix').val(prefix)
            content.find('#cp_type').val(cp_type)
            $('#subModalQuickView').append(content);
            $('#subModalQuickView').find('a#cp_add').attr('href', '/profile/clients/' + client_id + '/cp_add')
            $('#subModalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        },
        error: function(err){
            $('#subModalQuickView').html(err.responseText);
            $('#subModalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        },
    });
}

$('#modalQuickView').on('click', 'span.contacts_select', function(e){
    contacts_type = $(this).attr('contacts_type')
    transit_prefix = $(this).attr('transit_prefix')
    cp_id = $(this).attr('cp_id')
    clicked_sub_link = $(this)
    if (!cp_id) {
        cp_select = $(this).parent().parent().parent().find('span.cp_select').last().parent().parent()
        cp_select.parent().parent().css('border-collapse','collapse')
        cp_select.css('border', '2px solid red')
        delay(1000).then(() => cp_select.removeAttr('style'))
        delay(1000).then(() => cp_select.parent().parent().removeAttr('style'))
    } else {
        selectContact(cp_id, transit_prefix, contacts_type)
    }
})

function selectContact(cp_id, transit_prefix, contacts_type) {
    $('#subModalQuickView').html(null)
    url = '/profile/counterparties/' + cp_id + '/contacts_select'

    $.ajax({
        url: url,
        type: 'GET',
        success:function(data){
            content = $(data)
            content.find('#transit_prefix').val(transit_prefix)
            content.find('#contacts_type').val(contacts_type)
            $('#subModalQuickView').append(content);
            $('#subModalQuickView').find('a#contact_add').attr('href', '/profile/counterparties/' + cp_id + '/contacts_add')
            $('#subModalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        },
        error: function(err){
            $('#subModalQuickView').html(err.responseText);
            $('#subModalWindow').css('display', 'flex');
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

$('#subModalQuickView').on('click', 'a', function(e){
    if (typeof($(this).attr('download')) === 'undefined') {
        e.preventDefault();
        showSubModal($(this).attr('href'));
        return false;
    } else {
        return;
    }
})

$('#modalQuickView').on('click', 'a', function(e){
    if (typeof($(this).attr('download')) === 'undefined') {
        e.preventDefault();
        showModal($(this).attr('href'));
        return false;
    } else {
        return;
    }
})

$('table.list_view_table.modal tbody').on('click', 'tr', function(e){
    showModal($(this).attr('href'))
}).on('click', 'a', function(e){
    e.preventDefault();
    showModal($(this).attr('href'))
    return false;
})

$('table.list_view_table.no_modal tbody').on('click', 'tr', function(e){
    document.location = $(this).attr('href')
}).on('click', 'a', function(e){
    e.preventDefault();
    document.location = $(this).attr('href')
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

$('body').on('click', '.btn_add_transit', function(e){
    e.preventDefault()
    table = $('#transit_forms')
    formNum = $('.transit_form').length
    totalTransits = $("#id_transits-TOTAL_FORMS").val()
    newTransit = $(newTransitGlobal.replace(/__tprefix__/g, formNum))
    table.append(newTransit)
    totalTransits++
    $("#id_transits-TOTAL_FORMS").val(totalTransits)
    if (newTransit.find('.cargo_form').length == 0) {
        newTransit.find('.btn_add_cargo').last().click()
    }
    update_select_links()
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
    update_select_links()
})