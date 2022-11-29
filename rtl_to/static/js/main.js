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

function put_id_to_select(owner_id, container=$('#modalQuickView')){
    container.find('span.cp_select').each(function(){
        $(this).attr('client_id', owner_id)
    })
    container.find('span.contract_select').each(function(){
        $(this).attr('owner_id', owner_id)
    })
}

function update_select_links(ownerID, container=$('#modalQuickView')){
    owner_id = $('#modalQuickView').find(`#${ownerID}`).val()
    put_id_to_select(owner_id, container)
}

function update_contacts_select_link(link){
    if (link.attr('contacts_type') == 'from_contacts') {
        cp_type = 'sender'
    } else if (link.attr('contacts_type') == 'to_contacts') {
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
    update_select_links('id_client')
})

function findRootObject(obj){
    obj.parents().each(function(){
        if ($(this).attr('class')) {
            if ($(this).attr('class').split('_').pop() == 'form') {
                result = $(this)
                return false
            }
        }
    })
    return result
}

function update_contracts_links() {
    $('.contract_select').each(function(el){
        ext_order_form = findRootObject($(this))
        owner_id = ext_order_form.find('.ext_order_contractor').val()
        ext_order_form.find('.contract_select').attr('owner_id', owner_id)
    })
}

$('#modalQuickView').on('change', '.ext_order_contractor', function(e){
    ext_order_form = findRootObject($(this))
    update_select_links($(this).attr('id'), ext_order_form.find('.segment_forms'))
    ext_order_form.find('.contract_select').attr('owner_id', $(this).val())
})

$('#subModalQuickView').on('keyup', '#search_input', function(){
    search_area = $('#subModalQuickView div.searchable tbody')
    filter = $(this).val().toUpperCase()
    search_area.children().each(function(){
        if ($(this).find('td').text().toUpperCase().indexOf(filter) > -1) {
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
    owner_type = $(this).attr('owner_type')
    clicked_sub_link = $(this)
    if (!client_id) {
        parent_form = findRootObject(findRootObject($(this)))
        parent_prefix = findPrefix(parent_form)
        field_names = ['client', 'contractor']
        for (const field_name of field_names) {
            if (parent_prefix == '') {
                target_id = `#id_${field_name}`
            } else {
                target_id = `#id_${parent_prefix}-${field_name}`
            }
            target = parent_form.find(target_id)
            if (target.length > 0) {
                break
            }
        }
        $('#modalQuickView').animate({
            scrollTop: $('#modalQuickView').scrollTop() + target.offset().top - 150
        }, 1000)
        delay(500).then(() => target.css('border-color', 'red'))
        delay(1500).then(() => target.removeAttr('style'))
    } else {
        selectCP(client_id, transit_prefix, cp_type, owner_type)
    }
})

$('#modalQuickView').on('click', 'span.segment_docs', function(e){
    $('#subModalQuickView').html(null)
    segment_pk = $(this).attr('segment_pk')
    lk_type = $(this).attr('lk_type')
    clicked_sub_link = $(this)
    $.ajax({
        url: `/${lk_type}/print_forms/${segment_pk}/docs/`,
        type: 'get',
        success: function(data){
            content = $(data)
            $('#subModalQuickView').append(content);
            $('#subModalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        },
    })
})

function update_segments_select_links(){
    $('.segment_form').each(function(){
        container = $(this)
        owner_id = 'id_' + findPrefix($(this)) + '-contractor'
        update_select_links(owner_id, container)
    })
}

function selectCP(client_id, prefix, cp_type, owner_type='clients') {
    $('#subModalQuickView').html(null)

    if (owner_type == 'admin') {
        url = '/profile/admin/cp_select'
    } else {
        url = `/profile/${owner_type}/${client_id}/cp_select`
    }

    $.ajax({
        url: url,
        type: 'GET',
        success:function(data){
            content = $(data)
            content.find('#transit_prefix').val(prefix)
            content.find('#cp_type').val(cp_type)
            $('#subModalQuickView').append(content);
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
    if (typeof($(this).attr('download')) === 'undefined' && $(this).attr('target') != '_blank') {

        e.preventDefault();
        showSubModal($(this).attr('href'));
        return false;
    } else {
        return;
    }
})

$('#modalQuickView').on('click', 'a', function(e){
    if (typeof($(this).attr('download')) === 'undefined' && $(this).attr('target') != '_blank') {
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
        } else {
            deleteItem = false
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
    update_select_links('id_client')
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
    update_select_links('id_client')
})

function findPrefix (elem, full = true) {

    id_id = elem.find('input').first().attr('name')
    if (full) {
        slice = id_id.split('-').slice(0, -1)
    } else {
        slice = id_id.split('-').slice(0, -2)
    }

    return slice.join('-')
}

function addForm(label, template, prefix) {
    target = $('#' + prefix + '-' + label + '_forms')
    formNum = target.find('.' + label + '_form').length
    raw_prefix = findPrefix($(template))
    tags = raw_prefix.match(/__\w+__/g)
    matches = prefix.match(/\d+/g)
    if (!matches) {
        matches = new Array()
    }
    matches.push(formNum.toString())
    newForm = template
    for (let i = 0; i < tags.length; i++) {
        regex = new RegExp(tags[i], 'g')
        newForm = newForm.replace(regex, matches[i])
    }
    target.append(newForm)
    total = $("#id_" + prefix + "-TOTAL_FORMS").val()
    total++
    $("#id_" + prefix + "-TOTAL_FORMS").val(total)
    return $(target.children().eq(-1))
}

function update_ordering() {
    segments = $('.segment_form').filter(function() {
        return typeof $(this).attr('style') == 'undefined'
    })
    var i = 0
    segments.each(function(){
        i++
        prefix = findPrefix($(this))
        $('#id_' + prefix + '-ordering_num').val(i)
    })
}

function makeID(obj, form_prefix, field_prefix) {
    return `#id_${form_prefix}-${field_prefix}_${obj.attr('name').split('-').at(-1).split('_').slice(1).join('_')}`
}

function cross_exchange(input_obj, root_container = null){
    parent = findRootObject(input_obj)

    if (!root_container) {
        container = $('.' + parent.attr('class')).filter(function(){
            return input_obj.css('display') != 'none'
        })
    } else {
        container = root_container.find('.' + parent.attr('class')).filter(function(){
            return input_obj.css('display') != 'none'
        })
    }
    if (getSubFormType(input_obj) == 'departure_data') {
        target_form_index = container.index(parent) - 1
        target_input_prefix = 'to'
    } else if (getSubFormType(input_obj) == 'receive_data') {
        target_form_index = container.index(parent) + 1
        target_input_prefix = 'from'
    }
    target_form = container.eq(target_form_index)
    if (target_form.length > 0 && target_form_index >= 0) {
        target_input_id = makeID(input_obj, findPrefix(target_form), target_input_prefix)
        $(target_input_id).val(input_obj.val())
        if ($(target_input_id).attr('class').includes('ext_order_from_addr')) {
            seg_target = $(target_input_id).parents('.ext_order_form').find('.segment_form').first()
            if (seg_target.length > 0) {
                copy_departure_data($(target_input_id).parents('.ext_order_form'), seg_target)
            }
        } else if ($(target_input_id).attr('class').includes('ext_order_to_addr')) {
            seg_target = $(target_input_id).parents('.ext_order_form').find('.segment_form').last()
            if (seg_target.length > 0) {
                copy_receive_data($(target_input_id).parents('.ext_order_form'), seg_target)
            }
        }

        if (input_obj.attr('value') === undefined) {
            $(target_input_id).attr('value', null)
        } else {
            $(target_input_id).attr('value', input_obj.attr('value'))
        }
    }
}

function compare_receive_data(source, target) {
    source_arr = source.find('.receive_data').first().find('input').toArray()
    target_arr = target.find('.receive_data').first().find('input').toArray()
    let result = true
    source_arr.forEach((e, i) => {
    if ($(source_arr[i]).val() != $(target_arr[i]).val())
        result = false
    })
    return result
}

function flush_cp_data(form) {
    form.find('input').each(function(){
        $(this).val('')
        $(this).attr('value', null)
    })
    form.find('select').each(function(){
        $(this).val('')
        $(this).html(null)
    })
    form.find('.cp_display').html(null)
    form.find('.cp_select').html('Выбрать')
    form.find('.contacts_display').html(null)
    form.find('.contacts_select').html('Выбрать')
    form.find('.contacts_select').removeAttr('cp_id')
}

function segment_cp_exchange(source, target){
    source.find('.segment_cross_exchange').each(function(){
        $(this).trigger('change')
    })
    target.find('.cp_display').html(source.find('.cp_display').html())
    target.find('.cp_select').html(source.find('.cp_select').html())
}

function ext_order_cp_exchange(source, target){
    source.find('.ext_order_cross_exchange').each(function(){
        $(this).trigger('change')
    })
    target.find('.cp_display').html(source.find('.cp_display').html())
    target.find('.cp_select').html(source.find('.cp_select').html())
    target.find('.contacts_display').html(source.find('.contacts_display').html())
    target.find('.contacts_select').html(source.find('.contacts_select').html())
}

$('body').on('change', '.segment_cross_exchange', function(){
    root_container = findRootObject(findRootObject($(this)))
    cross_exchange($(this), root_container)
})

$('body').on('change', '.ext_order_cross_exchange', function(){
    cross_exchange($(this))
})

function make_departure_inactive(parent_form, type) {
    form = parent_form.find('.departure_data').first()
    form.find('.' + type + '_from_addr').attr('disabled', true)
    form.find('.cp_select').css('display', 'none')
    form.find('.contacts_select').css('display', 'none')
}

function make_departure_active(parent_form, type) {
    form = parent_form.find('.departure_data').first()
    form.find('.' + type + '_from_addr').removeAttr('disabled')
    form.find('.cp_select').removeAttr('style')
    form.find('.contacts_select').removeAttr('style')
}

function make_receive_inactive(parent_form, type) {
    form = parent_form.find('.receive_data').first()
    form.find('.' + type + '_to_addr').attr('disabled', true)
    form.find('.cp_select').css('display', 'none')
    form.find('.contacts_select').css('display', 'none')
}

function make_receive_active(parent_form, type) {
    form = parent_form.find('.receive_data').first()
    form.find('.' + type + '_to_addr').removeAttr('disabled')
    form.find('.cp_select').removeAttr('style')
    form.find('.contacts_select').removeAttr('style')
}

function indexInQuery(elem, queryLiteral) {
    query = $(queryLiteral).filter(function() {
        return $(this).css('display') != 'none'
    })
    return query.index(elem) + 1
}

$('body').on('click', '#btn_add_ext_order', function(e){
    e.preventDefault()
    last_existing_form = $('.ext_order_form').filter(function() {
        return $(this).css('display') != 'none'
    }).last()
    newForm = addForm('ext_order', newExtOrderGlobal, $(this).attr('prefix'))
    formIndex = indexInQuery(newForm, `.${newForm.attr('class')}`)
    newForm.find('.ext_order_number').val(`${fullTransitNum}${extOrderNumDelimiter}${formIndex}`)
    if (last_existing_form.length > 0) {
        last_existing_form_receive_data = last_existing_form.find('.receive_data').first()
        new_form_departure_data = newForm.find('.departure_data').last()
        if (last_existing_form.find('input.to_addr').val() == newForm.find('input.to_addr').val()) {
            flush_cp_data(last_existing_form_receive_data)
            flush_cp_data(new_form_departure_data)
        }
        ext_order_cp_exchange(last_existing_form_receive_data, new_form_departure_data)
    }

    update_contacts_select_links()
    if ($('.ext_order_form').length == 1) {
        make_departure_inactive($('.ext_order_form').first(), 'ext_order')
    }
    $('.ext_order_form').each(function(){
        make_receive_active($(this), 'ext_order')
    })
    make_receive_inactive($('.ext_order_form').last(), 'ext_order')
    newForm.find('.btn_add_segment').click()
})

function copy_departure_data(source, target, with_contacts = false){
    source_dep_data = source.find('.departure_data').first()
    target_dep_data = target.find('.departure_data').first()
    source_prefix = findPrefix(source)
    target_prefix = findPrefix(target)
    target_dep_data.find('.cp_display').html(source_dep_data.find('.cp_display').html())
    target_dep_data.find('.cp_select').html(source_dep_data.find('.cp_select').html())
    $(`#id_${target_prefix}-from_addr`).val($(`#id_${source_prefix}-from_addr`).val())
    $(`#id_${target_prefix}-sender`).val($(`#id_${source_prefix}-sender`).val())
    if (with_contacts) {
        $(`#id_${target_prefix}-from_contacts`).html($(`#id_${source_prefix}-from_contacts`).html())
        target_dep_data.find('.contacts_display').html(source_dep_data.find('.contacts_display').html())
        target_dep_data.find('.contacts_select').html(source_dep_data.find('.contacts_select').html())
    }
    $(`#id_${target_prefix}-from_addr`).change()
}

$('body').on('change', '.ext_order_form>.horizontal_tables_list>.departure_data', function(){
    source = $(this).parents('.ext_order_form')
    target = source.find('.segment_form').first()
    if (target.length > 0) {
        copy_departure_data(source, target)
    }
})

function copy_receive_data(source, target, with_contacts=false) {
    source_rec_data = source.find('.receive_data').first()
    target_rec_data = target.find('.receive_data').first()
    source_prefix = findPrefix(source)
    target_prefix = findPrefix(target)
    target_rec_data.find('.cp_display').html(source_rec_data.find('.cp_display').html())
    target_rec_data.find('.cp_select').html(source_rec_data.find('.cp_select').html())
    $(`#id_${target_prefix}-to_addr`).val($(`#id_${source_prefix}-to_addr`).val())
    $(`#id_${target_prefix}-receiver`).val($(`#id_${source_prefix}-receiver`).val())
    if (with_contacts) {
        $(`#id_${target_prefix}-to_contacts`).html($(`#id_${source_prefix}-to_contacts`).html())
        target_rec_data.find('.contacts_display').html(source_rec_data.find('.contacts_display').html())
        target_rec_data.find('.contacts_select').html(source_rec_data.find('.contacts_select').html())
    }
    $(`#id_${target_prefix}-to_addr`).change()
}

$('body').on('change', '.ext_order_form>.horizontal_tables_list>.receive_data', function(){
    source = $(this).parents('.ext_order_form')
    target = source.find('.segment_form').last()
    if (target.length > 0) {
        copy_receive_data(source, target)
    }
})

$('body').on('click', '.btn_add_segment', function(e){
    e.preventDefault()
    ext_order = $(this).parents('.ext_order_form')
    last_existing_form = ext_order.find('.segment_form').filter(function() {
        return $(this).css('display') != 'none'
    }).last()
    newForm = addForm('segment', newSegmentGlobal, $(this).attr('prefix'))
    owner_id = 'id_' + findPrefix(ext_order) + '-contractor'
    update_select_links(owner_id, ext_order.find('.segment_forms'))
    update_ordering()
    copy_receive_data(ext_order, newForm)
    if (last_existing_form.length > 0) {
        last_existing_form_receive_data = last_existing_form.find('.receive_data').last()
        new_form_departure_data = newForm.find('.departure_data').last()
        new_form_index = $('.segment_form').index(newForm)
        if (last_existing_form.find('.segment_to_addr').val() == newForm.find('.segment_to_addr').val()) {
            flush_cp_data(last_existing_form_receive_data)
        }
        segment_cp_exchange(last_existing_form_receive_data, new_form_departure_data)
    } else {
        copy_departure_data(ext_order, newForm)
    }
    if (ext_order.find('.segment_form').length == 1) {
        make_departure_inactive(ext_order.find('.segment_form').first(), 'segment')
    } else {
        ext_order.find('.segment_form').each(function(){
            make_receive_active($(this), 'segment')
        })
    }
    make_receive_inactive(newForm, 'segment')
})

function updateStrAttrs(form, jquery_select, attr_names, regex, replacement) {
    form.find(jquery_select).each(function(){
        obj = $(this)
        attr_names.forEach(function(attr_name){
            attr_val = obj.attr(attr_name)
            if (attr_val) {
                obj.attr(attr_name, attr_val.replace(regex, replacement))
            }
        })
    })
}

function formsRefresh(form_class, root_container=null){
    query = $(`.${form_class}_form`)
    query.each(function(){
        input = $(this).find('.receive_data').first().find(`.${form_class}_to_addr`)
        input.trigger('change')
    })
}

function delForm(elem) {
    prefix = findPrefix(elem, false)
    prefix_full = findPrefix(elem)
    elem.css('display', 'none')
    id_value = $('#id_' + prefix_full + '-id').val()

    if (elem.hasClass('ext_order_form')) {
        el_query = $('.ext_order_form')
        elem_index = el_query.index(elem)
        last_elem_index = el_query.length - 1
        if (elem_index == 0) {
            next_elem = el_query.eq(1)
            if (next_elem.length > 0) {
                copy_departure_data(elem, next_elem, true)
            }
        } else if (elem_index == last_elem_index) {
            next_elem = el_query.eq(last_elem_index - 1)
            if (next_elem.length > 0) {
                copy_receive_data(elem, next_elem, true)
            }
        }
    } else if (elem.hasClass('segment_form')) {
        el_query = elem.parents('.ext_order_form').find('.segment_form')
        elem_index = el_query.index(elem)
        last_elem_index = el_query.length - 1

        if (elem_index == 0) {
            next_elem = el_query.eq(1)
            if (next_elem.length > 0) {
                copy_departure_data(elem, next_elem)
            }
        } else if (elem_index == last_elem_index) {
            next_elem = el_query    .eq(last_elem_index - 1)
            if (next_elem.length > 0) {
                copy_receive_data(elem, next_elem)
            }
        }
    }

    if (id_value) {
        elem.css('display', 'none')
        $('#id_' + prefix_full + '-DELETE').val(true)
    } else {
        total = $('#id_' + prefix + '-TOTAL_FORMS').val()
        total--
        $('#id_' + prefix + '-TOTAL_FORMS').val(total)
        parent = $(elem).parent()
        elem.remove()
        ind = 0
        search_regex = new RegExp(prefix + '-\\d', 'g')
        parent.find('div.' + label + '_form').each(function(){
            e = $(this)
            updateStrAttrs(e, 'label', ['for'], search_regex, prefix + '-' + ind)
            updateStrAttrs(e, 'input', ['name', 'id'], search_regex, prefix + '-' + ind)
            updateStrAttrs(e, 'select', ['name', 'id'], search_regex, prefix + '-' + ind)
            ind++
        })
    }
    if (elem.hasClass('ext_order_form')) {
        formsRefresh('ext_order')
        if (elem_index == 0) {
            first_remaining = $('.ext_order_form').eq(1)
        } else {
            first_remaining = $('.ext_order_form').first()
        }
        make_departure_inactive(first_remaining, 'ext_order')
        make_receive_inactive($('.ext_order_form').last(), 'ext_order')
    } else if (elem.hasClass('segment_form')) {
        formsRefresh('segment', elem.parents('.ext_order_form'))
        make_departure_inactive(elem.parents('.ext_order_form').find('.segment_form').first(), 'segment')
        make_receive_inactive(elem.parents('.ext_order_form').find('.segment_form').last(), 'segment')
    }
}

$("body").on('click', '.btn_delete_status', function (e) {
    e.preventDefault()
    label = $(this).find('span').attr('label')
    delForm($(this).parents("." + label + "_form"))
})

function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
    return false;
};

$('body').on('click', '#contact_select_form tr', function(){
    input = $(this).find('input[type=checkbox]')
    if (input.attr('checked')) {
        $(this).removeAttr('class')
        input.attr('checked', false)
    } else {
        $(this).addClass('checked')
        input.attr('checked', true)
    }
})

$('body').on('click', '#contract_select_form tr', function(){
    input = $(this).find('input[type=radio]')
    if (input.attr('checked')) {
        $(this).removeAttr('class')
        input.attr('checked', false)
    } else {
        $('#contract_select_form tr').removeAttr('class')
        $('#contract_select_form input[type=radio]').attr('checked', false)
        $(this).addClass('checked')
        input.attr('checked', true)
    }
})

$('body').on('click', '#cp_select_form tr', function(){
    input = $(this).find('input[type=radio]')
    if (input.attr('checked')) {
        $(this).removeAttr('class')
        input.attr('checked', false)
    } else {
        $('#cp_select_form tr').removeAttr('class')
        $('#cp_select_form input[type=radio]').attr('checked', false)
        $(this).addClass('checked')
        input.attr('checked', true)
    }
})

$('body').on('click', '.show_ext_orders_hidden span.link_styled_span', function(){
    parent_form = $(this).parents('.ext_order_detail')
    hidden_element = parent_form.find('.ext_orders_hidden')
    label = parent_form.find('.span_label')
    if (hidden_element.css('display') == 'block') {
        hidden_element.removeAttr('style')
        label.html('Показать')
    } else {
        hidden_element.css('display', 'block')
        label.html('Скрыть')
    }
})

function toggleClass(elem, cls) {
    if (elem.hasClass(cls)) {
        elem.removeClass(cls)
    } else {
        elem.addClass(cls)
    }
}

function toggleHidden(elem){
    toggleClass(elem, 'hidden')
}

$('body').on('focus', '#cargos_paste_area', function() {
    $(this).find('div').each(function(){toggleHidden($(this))})
    toggleHidden($('#sh_warning'))
})

$('body').on('focusout', '#cargos_paste_area', function() {
    $(this).find('div').each(function(){toggleHidden($(this))})
    toggleHidden($('#sh_warning'))
})

$('body').on('change', '#id_size_dimensions', function(){
    var sizeDimensions = $(this).val()
    if (sizeDimensions == 1) {
        sizeDimensions = 0.1
    }
    data = hot.getSourceData()
    data.forEach(function (elem){
        elem.length = (elem.length / sizeDimensions).toFixed(1)
        elem.width = (elem.width / sizeDimensions).toFixed(1)
        elem.height = (elem.height / sizeDimensions).toFixed(1)
    })
    hot.updateData(data)
})

function sizeSplit (sizeRow) {
    knownDelimiters = ['x', 'х', '*']
    result = new Array()
    var i = 0
    curr_size = ''
    while (i < sizeRow.length) {
        char = sizeRow[i]
        if (knownDelimiters.includes(char)) {
            result.push(curr_size)
            curr_size = ''
        } else {
            curr_size += char
        }
        i++
    }
    result.push(curr_size.replace(',', '.'))
    return result
}

$('body').on('paste', '#cargos_paste_area', function(event) {
    $(container).html(null)
    var input_id = $(this).attr("id");
    var sizeDimensions = $('#id_size_dimensions').val()
    var sizeIsJoined = document.getElementById('id_size_joined').checked
    var value;
    if (event.originalEvent.clipboardData) {
        value = event.originalEvent.clipboardData.getData('text/plain');
    } else if (window.clipboardData) {
        value = window.clipboardData.getData("Text")
    } else {
        return
    }
    parsed_clipboard = new Array()
    value.split('\r\n').forEach((row) => {
        if (row !== ''){
            row_arr = row.split('\t')
            if (sizeIsJoined) {
                size = sizeSplit(row_arr[3])
                weight = parseFloat(row_arr[4].replace(' ', '').replace(',', '.'))
            } else {
                size = [row_arr[3].replace(',', '.'), row_arr[4].replace(',', '.'), row_arr[5].replace(',', '.')]
                weight = parseFloat(row_arr[6].replace(' ', '').replace(',', '.'))
            }
            parsed_clipboard.push({
                package: row_arr[0],
                quantity: row_arr[1],
                mark: row_arr[2],
                length: (size[0] / sizeDimensions).toFixed(1),
                width: (size[1] / sizeDimensions).toFixed(1),
                height: (size[2] / sizeDimensions).toFixed(1),
                weight: weight
            })
        }
    })

    hot = Handsontable(container, {
        data: parsed_clipboard,
        rowHeaders: false,
        colHeaders: ['Тип упаковки', 'Кол-во мест', 'Маркировка', 'Длина, см', 'Ширина, см', 'Высота, см', 'Вес, кг'],
        columnSorting: true,
        sortIndicator: true,
        height: 'auto',
        width: 'auto',
        licenseKey: 'non-commercial-and-evaluation'
    })
    toggleHidden($('#cargos_paste_area'))
    toggleClass($('#sh_wrapper'), 'thin')
    toggleHidden($('button'))
    tableWidth = $('#spreadsheet-area .wtHider').first().width()
    $('#allowed_packages').css('width', tableWidth)
    event.preventDefault();
})

$('#modalQuickView').on('click', 'span.cargos_spreadsheet', function(e){
    prefix = $(this).attr('tprefix')
    $.ajax({
        url: 'cargos_spreadsheet',
        type: 'GET',
        success: function(data){
            content = $(data)
            $('#subModalQuickView').append(content);
            $('#subModalQuickView').find('#transit_prefix').val(prefix)
            $('#subModalWindow').css('display', 'flex');
            $('html, body').css({
                overflow: 'hidden',
                height: '100%'
            });
        }
    })
})

$('body').on('click', '#spreadsheed_submit', function(e){
    e.preventDefault()
    rows = $('#spreadsheet-area').find('table.htCore>tbody>tr')

    allowed_packages = $('#allowed_packages p').last().html()

    correct = true
    rows.each(function(){
        pack_td = $(this).find('td').first()
        if (!allowed_packages.includes(pack_td.html())) {
            pack_td.css('border', '1px solid red')
            correct = false
        }
    })
    if (correct) {
        prefix = $('#transit_prefix').val()
        transit_form = $(`#id_${prefix}-id`).parents('.transit_form')
        button = transit_form.find('.btn_add_cargo')
        data = hot.getData()
        while (transit_form.find('.cargo_form').length < data.length) {
            button.click()
        }

        forms = transit_form.find('.cargo_form')
        data.forEach((el, ind) => {
            form = forms.eq(ind)

            form.find('.cargo_mark').val(el[2]) // cargo_mark
            form.find('.cargo_length').val(el[3])
            form.find('.cargo_width').val(el[4])
            form.find('.cargo_height').val(el[5])
            form.find('.cargo_weight').val(el[6])
            form.find('.cargo_quantity').val(el[1])

            form.find('.cargo_package_type').find('option').each(function(){
                if ($(this).html() == el[0]) {
                    $(this).prop('selected', true)
                }
            })
        })
        $('#subModalCloseButton').click()
    }
})

$('.order_filter').on('change', function(){
    window.location.href = $(this).val()
})

function selectContract(owner_id, owner_type, form_prefix) {
    $('#subModalQuickView').html(null)

    url = `/profile/${owner_type}/${owner_id}/contract_select`

    $.ajax({
        url: url,
        type: 'GET',
        success:function(data){
            content = $(data)
            content.find('#owner_type').val(owner_type)
            content.find('#form_prefix').val(form_prefix)
            $('#subModalQuickView').append(content);
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

$('#modalQuickView').on('click', 'span.contract_select', function(e){
    owner_id = $(this).attr('owner_id')
    owner_type = $(this).attr('owner_type')
    form_prefix = $(this).attr('form_prefix')
    clicked_sub_link = $(this)
    if (!owner_id) {
        parent_form = findRootObject(findRootObject($(this)))
        parent_prefix = findPrefix(parent_form)
        field_names = ['client', 'contractor']
        for (const field_name of field_names) {
            if (parent_prefix == '') {
                target_id = `#id_${field_name}`
            } else {
                target_id = `#id_${parent_prefix}-${field_name}`
            }
            target = parent_form.find(target_id)
            if (target.length > 0) {
                break
            }
        }
        $('#modalQuickView').animate({
            scrollTop: $('#modalQuickView').scrollTop() + target.offset().top - 150
        }, 1000)
        delay(500).then(() => target.css('border-color', 'red'))
        delay(1500).then(() => target.removeAttr('style'))
    } else {
        selectContract(owner_id, owner_type, form_prefix)
    }
})
