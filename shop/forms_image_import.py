from django import forms

class ImageImportForm(forms.Form):
    FILE_TYPE_CHOICES = [
        ('csv', 'CSV File'),
        ('excel', 'Excel File (.xlsx, .xls)'),
    ]
    
    file_type = forms.ChoiceField(
        choices=FILE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control my-2'}),
        label="Data File Type"
    )
    data_file = forms.FileField(
        label="Data File (CSV/Excel)", 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control my-2'})
    )
    sheet_name = forms.CharField(
        required=False,
        label="Sheet Name (for Excel)",
        widget=forms.TextInput(attrs={'class': 'form-control my-2', 'placeholder': 'Leave empty for first sheet'})
    )
    
    def clean_data_file(self):
        file = self.cleaned_data.get('data_file')
        file_type = self.data.get('file_type')
        
        if file and file_type:
            file_name = file.name.lower()
            
            if file_type == 'csv':
                if not file_name.endswith('.csv'):
                    raise forms.ValidationError(
                        'Please upload a CSV file with .csv extension. '
                        'Current file type is not supported for CSV format.'
                    )
            elif file_type == 'excel':
                if not (file_name.endswith('.xlsx') or file_name.endswith('.xls')):
                    raise forms.ValidationError(
                        'Please upload an Excel file with .xlsx or .xls extension. '
                        'Current file type is not supported for Excel format.'
                    )
        
        return file

class ImageImportFolderForm(ImageImportForm):
    images = forms.FileField(
        label="Image Files",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control my-2',
            'multiple': True,
            'accept': '.png,.jpg,.jpeg,.gif'
        })
    )
    
    def clean_images(self):
        files = self.files.getlist('images')
        if not files:
            raise forms.ValidationError('Please select at least one image file.')
        
        for file in files:
            if not file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                raise forms.ValidationError(f'File {file.name} is not a valid image format. Only PNG, JPG, JPEG, GIF are allowed.')
        
        return files

class ImageImportZipForm(ImageImportForm):
    zip_file = forms.FileField(
        label="ZIP File containing images",
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control my-2',
            'accept': '.zip'
        })
    )
    
    def clean_zip_file(self):
        file = self.cleaned_data.get('zip_file')
        if file and not file.name.lower().endswith('.zip'):
            raise forms.ValidationError('Please upload a ZIP file.')
        return file