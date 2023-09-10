from django import forms
from django.forms import ModelForm, DateInput, ClearableFileInput

from print_forms.models import TransDocsData, DocOriginal, ShippingReceiptOriginal, RandomDocScan


class WaybillDataForm(ModelForm):
    """
    Форма заполнения данных по автомобильной перевозке
    """
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='print_forms/pages/base/waybill_as_my_style.html', context=context)

    class Meta:
        model = TransDocsData
        exclude = ('segment', 'ext_order', 'file_name', 'doc_original', 'race_number')
        widgets = {
            'doc_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'doc_date_trans': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'driver_passport_issued_at': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }


class TransDocDataForm(ModelForm):
    """
    Форма заполнения данных по не-автомобильной перевозке
    """
    required_css_class = 'required'
    race_number = forms.CharField(required=True, label='Номер рейса')

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='print_forms/pages/base/trans_doc_as_my_style.html', context=context)

    class Meta:
        model = TransDocsData
        exclude = (
            'segment', 'ext_order', 'file_name', 'doc_original', 'driver_last_name', 'driver_first_name',
            'driver_second_name', 'driver_entity', 'driver_license', 'auto_model', 'auto_number', 'auto_ownership',
            'auto_tonnage'
        )
        widgets = {
            'doc_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'doc_date_trans': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }


class FileInputWithBlankLink(ClearableFileInput):
    template_name = 'print_forms/pages/base/clearable_file_input.html'


class DocOriginalForm(ModelForm):
    """
    Форма занесения скана транспортного документа
    """
    required_css_class = 'required'

    class Meta:
        model = DocOriginal
        exclude = ('segment', 'transit')
        widgets = {
            'doc_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'load_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'td_file': FileInputWithBlankLink()
        }


class RandomDocScanForm(ModelForm):
    """
    Форма занесения скана иного документа
    """
    required_css_class = 'required'

    class Meta:
        model = RandomDocScan
        exclude = ('segment', 'transit')
        widgets = {
            'doc_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'rd_file': FileInputWithBlankLink()
        }


class ShippingReceiptOriginalForm(ModelForm):
    """
    Форма занесения скана ЭР
    """
    required_css_class = 'required'

    class Meta:
        model = ShippingReceiptOriginal
        exclude = ('segment', 'transit')
        widgets = {
            'doc_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'load_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'sr_file': FileInputWithBlankLink()
        }
