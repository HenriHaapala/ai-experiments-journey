from django import forms
from .models import DocumentUpload


class DocumentUploadForm(forms.ModelForm):
    file = forms.FileField(
        required=True,
        help_text="Upload a PDF, Markdown, or text file. The file is NOT stored."
    )

    class Meta:
        model = DocumentUpload
        fields = ["title", "source_type"]  # file is NOT in the model