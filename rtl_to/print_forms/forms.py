from django.forms import ModelForm, DateInput

from print_forms.models import TransDocsData, DocOriginal


class WaybillDataForm(ModelForm):
    required_css_class = 'required'

    def as_my_style(self):
        context = super().get_context()
        context['fields'] = {f_e[0].name: f_e[0] for f_e in context['fields']}
        context['hidden_fields'] = {f_e.name: f_e for f_e in context['hidden_fields']}
        return self.render(template_name='print_forms/pages/base/waybill_as_my_style.html', context=context)

    class Meta:
        model = TransDocsData
        exclude = ('segment', 'ext_order', 'file_name', 'doc_original')
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
