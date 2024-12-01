from django import forms

#FILE UPLOAD FORM
class FileUploadForm(forms.Form):
    file = forms.FileField(required=False)

#CHAT INPUT FORM
class ChatInputForm(forms.Form):
    input_text = forms.CharField(max_length=255, 
    label='',
    widget=forms.TextInput(attrs={
        'class': 'chat_input',
        'placeholder': 'Prompt...'
    },
    ))