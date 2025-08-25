from django.forms import ModelForm
from django import forms
from django.db.models import Case, When, Value, IntegerField
from custom.models import *
from .models import Shop, ShopImage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, Row, Column, HTML, Field

class ShopImageForm(ModelForm):
    class Meta:
        model = ShopImage
        fields = ['image','image_type']

        labels = {
            'image': 'Image',
            'image_type': 'Image Type',
        }

    def __init__(self, *args, **kwargs):
        super(ShopImageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(""" <div class="row"> """),
            Column(Field('image_type', css_class='form-control'), css_class="col"),
            Column(Field('image', css_class='form-control'), css_class="col"),
            HTML(""" </div> """),
        )

class ShopImageForm1(ModelForm):
    class Meta:
        model = ShopImage
        fields = ['image']

        labels = {
            'image': 'Image',
        }

    def __init__(self, *args, **kwargs):
        super(ShopImageForm1, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(""" <div class="row"> """),
            Column(Field('image', css_class='form-control'), css_class="col"),
            HTML(""" </div> """),
        )

class ShopImageForm2(ModelForm):
    class Meta:
        model = ShopImage
        fields = ['shop', 'image','image_type']

        labels = {
            'shop': 'Name of Shop',
            'image': 'Image',
            'image_type': 'Image Type',
        }

    def __init__(self, *args, **kwargs):
        super(ShopImageForm2, self).__init__(*args, **kwargs)

        self.fields['shop'].queryset = Shop.objects.filter(delete_time__isnull=True)

        # Optional: use a lambda or function for display
        self.fields['shop'].label_from_instance = lambda obj: f"{obj.center} - {obj.name}"

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(""" <div class="row"> """),
            Column(Field('shop', css_class='form-control', id='shop-select'), css_class="col"),
            Column(Field('image_type', css_class='form-control'), css_class="col"),
            Column(Field('image', css_class='form-control'), css_class="col"),
            HTML(""" </div> """),
        )

class ShopForm(ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'owner', 'contact']

    def __init__(self, *args, **kwargs):
        super(ShopForm, self).__init__(*args, **kwargs)
        self.fields['municipality'].queryset = Municipality.objects.all()
        self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        self.fields['village'].queryset = Village.objects.none()
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(""" <div class="row mt-2"> """),
            Column(Field('name', css_class='form-control'), css_class="col"),
            Column(Field('owner', css_class='form-control'), css_class="col"),
            Column(Field('contact', css_class='form-control'), css_class="col"),
            HTML(""" </div> """),           
        )

class ShopCoordinateForm(ModelForm):
    class Meta:
        model = Shop
        fields = ['municipality', 'administrativepost', 'village', 'aldeia', 'latitude', 'longitude']
    def __init__(self, *args, **kwargs):
        super(ShopCoordinateForm, self).__init__(*args, **kwargs)
        self.fields['municipality'].queryset = Municipality.objects.all()
        self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        self.fields['village'].queryset = Village.objects.none()
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(""" <div class="row mt-2"> """),
            Column(Field('municipality', css_class='form-control'), css_class="col"),
            Column(Field('administrativepost', css_class='form-control'), css_class="col"),
            HTML(""" <div class="row mt-2"> """),
            HTML(""" </div> """),
            Column(Field('village', css_class='form-control'), css_class="col"),
            Column(Field('aldeia', css_class='form-control'), css_class="col"),
            HTML(""" </div> """),
            HTML(""" <div class="row mt-2"> """),
            Column(Field('latitude', css_class='form-control'), css_class="col"),
            HTML(""" </div> """),
            HTML(""" <div class="row mt-2"> """),
            Column(Field('longitude', css_class='form-control'), css_class="col"),
            HTML(""" </div> """),
        )

        if 'municipality' in self.data:
            try:
                municipality_id = int(self.data.get('municipality'))
                self.fields['administrativepost'].queryset = AdministrativePost.objects.filter(municipality_id=municipality_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        elif self.instance.pk and self.instance.municipality:
            self.fields['administrativepost'].queryset = AdministrativePost.objects.filter(municipality=self.instance.municipality).order_by('name')

        if 'administrativepost' in self.data:
            try:
                ap_id = int(self.data.get('administrativepost'))
                self.fields['village'].queryset = Village.objects.filter(administrativepost_id=ap_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['village'].queryset = Village.objects.none()
        elif self.instance.pk and self.instance.administrativepost:
            self.fields['village'].queryset = Village.objects.filter(administrativepost=self.instance.administrativepost).order_by('name')

        if 'village' in self.data:
            try:
                village_id = int(self.data.get('village'))
                self.fields['aldeia'].queryset = Aldeia.objects.filter(village_id=village_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['aldeia'].queryset = Aldeia.objects.none()
        elif self.instance.pk and self.instance.village:
            self.fields['aldeia'].queryset = Aldeia.objects.filter(village=self.instance.village).order_by('name')

class ShopAddForm(ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'owner', 'contact','municipality', 'administrativepost', 'village', 'aldeia', 'kind_of_channel','latitude', 'longitude','kind_of_banner','dimension']
        widgets = {
            'kind_of_channel': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'administrativepost': 'Administrative Post',
        }
    def __init__(self, *args, **kwargs):
        super(ShopAddForm, self).__init__(*args, **kwargs)
        self.fields['municipality'].queryset = Municipality.objects.all()
        self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        self.fields['village'].queryset = Village.objects.none()
        self.fields['aldeia'].queryset = Aldeia.objects.none()
        self.fields['kind_of_channel'].queryset = Channel.objects.annotate(
            is_other=Case(
                When(name='Other', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('is_other', 'name')
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(""" <div class="row mt-2"> """),
            Column(Field('name', css_class='form-control'), css_class="col-lg-4 col-md-4 mt-2"),
            Column(Field('owner', css_class='form-control'), css_class="col-lg-4 col-md-4 mt-2"),
            Column(Field('contact', css_class='form-control'), css_class="col-lg-4 col-md-4 mt-2"),
            # Column(Field('center', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            HTML(""" </div> """),
            HTML(""" <div class="row mt-2"> """),
            Column(Field('municipality', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            Column(Field('administrativepost', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            # HTML(""" <div class="row mt-2"> """),
            # HTML(""" </div> """),
            Column(Field('village', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            Column(Field('aldeia', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            HTML(""" </div> """),
            HTML(""" <div class="row mt-2"> """),
            Column(Field('kind_of_banner', css_class='form-control'), css_class="col-lg-6 col-md-6 mt-2"),
            Column(Field('dimension', css_class='form-control'), css_class="col-lg-6 col-md-6 mt-2"),
            HTML(""" </div> """),
            HTML(""" <div class="row mt-2"> """),
            Column(Field('kind_of_channel', css_class='form-check-input'), css_class="col"),
            HTML(""" </div> """),
            HTML(""" <div class="row mt-2"> """),
            Column(Field('latitude', css_class='form-control'), css_class="col-lg-6 col-md-6 mt-2"),
            Column(Field('longitude', css_class='form-control'), css_class="col-lg-6 col-md-6 mt-2"),
            HTML(""" </div> """),
        )

        if 'municipality' in self.data:
            try:
                municipality_id = int(self.data.get('municipality'))
                self.fields['administrativepost'].queryset = AdministrativePost.objects.filter(municipality_id=municipality_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        elif self.instance.pk and self.instance.municipality:
            self.fields['administrativepost'].queryset = AdministrativePost.objects.filter(municipality=self.instance.municipality).order_by('name')

        if 'administrativepost' in self.data:
            try:
                ap_id = int(self.data.get('administrativepost'))
                self.fields['village'].queryset = Village.objects.filter(administrativepost_id=ap_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['village'].queryset = Village.objects.none()
        elif self.instance.pk and self.instance.administrativepost:
            self.fields['village'].queryset = Village.objects.filter(administrativepost=self.instance.administrativepost).order_by('name')

        if 'village' in self.data:
            try:
                village_id = int(self.data.get('village'))
                self.fields['aldeia'].queryset = Aldeia.objects.filter(village_id=village_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['aldeia'].queryset = Aldeia.objects.none()
        elif self.instance.pk and self.instance.village:
            self.fields['aldeia'].queryset = Aldeia.objects.filter(village=self.instance.village).order_by('name')


class ShopInfoForm(ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'owner', 'contact','municipality', 'administrativepost', 'village', 'aldeia', 'kind_of_channel', 'dimension','kind_of_banner']
        widgets = {
            'kind_of_channel': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'administrativepost': 'Administrative Post',
        }
    def __init__(self, *args, **kwargs):
        super(ShopInfoForm, self).__init__(*args, **kwargs)
        self.fields['kind_of_channel'].queryset = Channel.objects.annotate(
            is_other=Case(
                When(name='Other', then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by('is_other', 'name')

        self.fields['municipality'].queryset = Municipality.objects.all()
        self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        self.fields['village'].queryset = Village.objects.none()
        self.fields['aldeia'].queryset = Aldeia.objects.none()
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(""" <div class="row mt-2"> """),
            Column(Field('name', css_class='form-control'), css_class="col-lg-4 col-md-4 mt-2"),
            Column(Field('owner', css_class='form-control'), css_class="col-lg-4 col-md-4 mt-2"),
            Column(Field('contact', css_class='form-control'), css_class="col-lg-4 col-md-4 mt-2"),
            # Column(Field('center', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            HTML(""" </div> """),
            HTML(""" <div class="row mt-2"> """),
            Column(Field('municipality', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            Column(Field('administrativepost', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            # HTML(""" <div class="row mt-2"> """),
            # HTML(""" </div> """),
            Column(Field('village', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            Column(Field('aldeia', css_class='form-control'), css_class="col-lg-3 col-md-3 mt-2"),
            HTML(""" </div> """),
            HTML(""" <div class="row mt-2"> """),
            Column(Field('kind_of_banner', css_class='form-control'), css_class="col-lg-6 col-md-6 mt-2"),
            Column(Field('dimension', css_class='form-control'), css_class="col-lg-6 col-md-6 mt-2"),
            HTML(""" </div> """),
            HTML(""" <div class="row mt-2"> """),
            Column(Field('kind_of_channel', css_class='form-check-input'), css_class="col"),
            HTML(""" </div> """),
        )

        if 'municipality' in self.data:
            try:
                municipality_id = int(self.data.get('municipality'))
                self.fields['administrativepost'].queryset = AdministrativePost.objects.filter(municipality_id=municipality_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        elif self.instance.pk and self.instance.municipality:
            self.fields['administrativepost'].queryset = AdministrativePost.objects.filter(municipality=self.instance.municipality).order_by('name')

        if 'administrativepost' in self.data:
            try:
                ap_id = int(self.data.get('administrativepost'))
                self.fields['village'].queryset = Village.objects.filter(administrativepost_id=ap_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['village'].queryset = Village.objects.none()
        elif self.instance.pk and self.instance.administrativepost:
            self.fields['village'].queryset = Village.objects.filter(administrativepost=self.instance.administrativepost).order_by('name')

        if 'village' in self.data:
            try:
                village_id = int(self.data.get('village'))
                self.fields['aldeia'].queryset = Aldeia.objects.filter(village_id=village_id).order_by('name')
            except (ValueError, TypeError):
                self.fields['aldeia'].queryset = Aldeia.objects.none()
        elif self.instance.pk and self.instance.village:
            self.fields['aldeia'].queryset = Aldeia.objects.filter(village=self.instance.village).order_by('name')

class ShopMapLocationForm(ModelForm):
    class Meta:
        model = Shop
        fields = ['latitude', 'longitude']
    
    def __init__(self, *args, **kwargs):
        super(ShopMapLocationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML(""" <div class="row mt-2"> """),
            Column(Field('latitude', css_class='form-control'), css_class="col-lg-6 col-md-6"),
            Column(Field('longitude', css_class='form-control'), css_class="col-lg-6 col-md-6"),
            HTML(""" </div> """),
        )


class ShopImportForm(forms.Form):
    file = forms.FileField(label="Upload CSV", widget=forms.ClearableFileInput(attrs={'class': 'form-control my-2'}))
