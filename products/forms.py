from django import forms

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return initial
        if isinstance(data, (list, tuple)):
            return [super().clean(file, initial) for file in data]
        return [super().clean(data, initial)]

class ProductCreateForm(forms.Form):
    name = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea, required=False)
    price = forms.DecimalField()
    category = forms.IntegerField()  # Assuming category is a PK
    quantity = forms.IntegerField(required=False)
    upload_images = MultipleFileField(required=False)