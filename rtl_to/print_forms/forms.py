from django.forms import ModelForm, DateInput

from print_forms.models import WaybillData, DocOriginal


class WaybillDataForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = WaybillData
        exclude = ('segment', 'ext_order', 'file_name', 'original')
        widgets = {
            'waybill_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }


class DocOriginalForm(ModelForm):
    required_css_class = 'required'

    class Meta:
        model = DocOriginal
        exclude = ('segment', 'transit', 'doc_type')
        widgets = {
            'doc_date': DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
        }
