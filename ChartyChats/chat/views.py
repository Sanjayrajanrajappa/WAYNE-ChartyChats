from django.shortcuts import render
import pandas as pd
from .forms import FileUploadForm, ChatInputForm
from datetime import datetime
import os
import google.generativeai as geni

import pyrebase

config={
    "apiKey": "AIzaSyCTLhfCkEpanvbc_qenZjQELWD81HEpyVM",
    "authDomain": "chartychats.firebaseapp.com",
    "databaseURL": "https://chartychats-default-rtdb.firebaseio.com",
    "projectId": "chartychats",
    "storageBucket": "chartychats.firebasestorage.app",
    "messagingSenderId": "616048755184",
    "appId": "1:616048755184:web:dd789cb04c47b7bf111d35"
}
firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()


def chat(request):
    geni.configure(api_key="AIzaSyDDSxJW6cQ0VJIKNl6fHM94xktkXG0yTL0")
    model = geni.GenerativeModel("gemini-1.5-flash")
    response = None
    if request.method == 'POST':
        form_chat = ChatInputForm(request.POST)
        if form_chat.is_valid():
            response_from_user = form_chat.cleaned_data['input_text']
            response = model.generate_content(response_from_user).text
            
            form_chat = ChatInputForm()
    else:
        form_chat = ChatInputForm()

    f = FileUploadForm()
    msg = ""
    
    if request.method == 'POST' and 'file' in request.FILES:
        form = FileUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            if uploaded_file.name.endswith('.csv'):
                try:
                    data = pd.read_csv(uploaded_file)
                    for idx, row in data.iterrows():
                        row_key = "|".join(str(value) for value in row.values)
                        row_data = row.to_dict()  
                        database.child("uploaded_data").child(row_key).set(row_data)
                    msg = "File uploaded and data pushed to Firebase successfully!"
                except Exception as e:
                    msg = f"An error occurred: {e}"
            else:
                msg = "Please upload a valid CSV file."
        else:
            msg = "Form is invalid. Please try again."
    else:
        form = FileUploadForm()

    return render(request, 'chat/chat.html', {'form': f, 'msg': msg, 'form_chat':form_chat, 'response': response})
