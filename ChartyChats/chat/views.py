from django.shortcuts import render
import pandas as pd
from .forms import FileUploadForm, ChatInputForm
import google.generativeai as geni
import io
import json
import re
from .grapher import graphGenerator

def chat(request):
    #GEMINI API 
    geni.configure(api_key="AIzaSyDDSxJW6cQ0VJIKNl6fHM94xktkXG0yTL0")
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = geni.GenerativeModel(
        model_name="gemini-1.5-flash-8b",
        generation_config=generation_config,
        #INSTRUCTION PASSED TO THE LLM
        system_instruction = (
            "I am Charty, an AI assistant designed to assist you with analyzing and interpreting datasets. If you greet, I will greet you back and ask how I can help. If you upload a CSV file, I will silently acknowledge it without mentioning the upload status unless you explicitly ask."
            "When you ask about the upload status like 'can you read the uploaded data?' I will reply by saying yes or no and what to do with the data. I won't be generating anything other than this."
            "I can help you in various ways:Reading the Data:I can provide insights into the data, such as summarizing its content, reading specific rows, or explaining its structure. You can request actions like listing columns, showing the first few rows, or summarizing key statistics."
            "Example: 'Please show me the first 10 rows of the dataset.'"
            "If you ask whether I can read the uploaded data, I will confirm once and only once, then proceed to ask what you would like to do with it."
            "If you ask questions like 'sum up the average incomes' I will give only the sum of average incomes and not generate any visuals."
            "I would be able to generate new data through aggregate functions and give them as data to be used to produce visuals and explain those visuals to you."
            "Answering Queries: You can ask specific questions about your dataset. I will analyze it to provide answers based on the data, such as finding trends, performing calculations, or summarizing it in meaningful ways. Example: 'How has revenue changed over the past five years?'"
            "Generating Visualizations: For questions involving trends or performance, I will suggest the best type of graphs based on the query, you can select the one that you see would fit good and I will generate a structured JSON format to create the plot. I will not assume visualization is required unless you explicitly ask or the question logically warrants it. Example: 'What are the sales figures for each product in Q4?'"
            '''
                {
                    "data": [
                        {
                            "x": ["giraffes", "orangutans", "monkeys"],  // Categories for x-axis
                            "y": [20, 14, 23],  // Values for y-axis
                            "type": "bar"  // Type of graph
                        }
                    ],
                    "title": "Zoo Animal Counts",
                    "xaxis_title": "Animals",
                    "yaxis_title": "Count"
                }
                {
                    "data": [
                        {
                            "x": [1, 2, 3, 4, 5],  // x-axis values (time, or any continuous variable)
                            "y": [10, 11, 12, 13, 14],  // y-axis values (numeric values corresponding to x)
                            "type": "line"  // Type of graph
                        }
                    ],
                    "title": "Sales Over Time",
                    "xaxis_title": "Time",
                    "yaxis_title": "Sales"
                }
                {
                    "data": [
                        {
                            "labels": ["A", "B", "C"],  // Categories
                            "values": [10, 20, 30],  // Values for each category
                            "type": "pie"  // Type of graph
                        }
                    ],
                    "title": "Category Distribution"
                }
                {
                    "data": [
                        {
                            "x": [1, 2, 2, 3, 3, 3, 4, 4, 4, 4],  // Data points
                            "type": "histogram"  // Type of graph
                        }
                    ],
                    "title": "Data Distribution",
                    "xaxis_title": "Values",
                    "yaxis_title": "Frequency"
                }
                {
                    "data": [
                        {
                            "y": [10, 11, 12, 13, 14, 15, 16],
                            "type": "box"  // Type of graph
                        }
                    ],
                    "title": "Data Spread",
                    "yaxis_title": "Values"
                }

            '''
            "The json data should be in the above format. And the necessary things like labels, points should also be given for various visualizations"
            "The 0-index would be the json file data and the 1-index would be the explanation for the graph always."
            "Dont do 'Explanation:....' just give it in a casual manner like 'This graph says that ......'"
            "4. **End-to-End Output**: For queries involving visualizations, I give the required json data for generating the respective visualization."
            "and explain the graph that is plotted using the given json data nothing more no other impoortant notes and such sentences be straight forward."
        )
    )
    #CHAT: SESSION START
    chat_session = model.start_chat(
        history=[
            {"role": "user", "parts": ["Hi, what is your name?\n"]},
            {"role": "model", "parts": ["My name is Charty.\n"]},
        ]
    )

    response = None #RESPONSE OF BOT
    json_data = None #JSON DATA OF VISUALS GIVEN BY CHARTY
    form_chat = ChatInputForm() #INPUT FROM THE USER
    f = FileUploadForm() #CSV FILE UPLOAD
    msg = ""
    uploaded_data = None
    uploaded_data_preview = None
    visualization_data = None
    graph_type = None

    #CHAT: RESET HANDLER
    if request.method == 'POST' and 'reset_chat' in request.POST:
        request.session['chat_history'] = []
        request.session['uploaded_data'] = None
        response = None
        form_chat = ChatInputForm()

    #CHAT: MESSAGE HANDLER
    elif request.method == 'POST' and 'input_text' in request.POST:
        form_chat = ChatInputForm(request.POST)
        if form_chat.is_valid():
            response_from_user = form_chat.cleaned_data['input_text']
            uploaded_data = request.session.get('uploaded_data', None)
            if uploaded_data:
                uploaded_data_df = pd.DataFrame(uploaded_data)
                raw_data = uploaded_data_df.to_string(index=False)
                response_prompt = (
                    f"{response_from_user}\n\nHere is the raw dataset you provided:\n{raw_data}\n"
                    "Based on this dataset, can you help me with a visualization or analysis?"
                )
            else:
                response_prompt = response_from_user
            bot_response = chat_session.send_message(response_prompt) #CHARTY TAKING INPUT FROM THE USER
            response = bot_response.text #CHARTY'S RESPONSE TO THE INPUT GIVEN BY THE USER
            r = ""
            for i in response.split("```"):
                if "json" in i:
                    try:
                        #CLEANING THE DATA TO TEST FOR AVAILABILITY OF JSON
                        cleaned_data = i.replace("json", "", 1).strip()
                        json_data = json.loads(cleaned_data) #CHECKS FOR JSON
                        graphGenerator(json_data)
                        print("The json data is: ")
                        print(json_data)
                    except Exception as e:
                        print("Error processing JSON:", e)
                        print(i)
                else:
                    r += i.strip() #NON JSON PART (REST OF THE CHAT)
            response = r

            #CHAT: UPDATE ON MEMORY
            chat_history = request.session.get('chat_history', [])
            chat_history.append({'user': response_from_user, 'bot': response})
            request.session['chat_history'] = chat_history

    #FILE UPLOAD HANDLER
    elif request.method == 'POST' and 'file' in request.FILES:
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            if uploaded_file.name.endswith('.csv'):
                try:
                    uploaded_data = pd.read_csv(uploaded_file)
                    request.session['uploaded_data'] = uploaded_data.to_dict()
                    uploaded_data_preview = uploaded_data.head().to_html()
                    msg = "File uploaded and data successfully read into a DataFrame!"
                except Exception as e:
                    msg = f"An error occurred while reading the file: {e}"
            else:
                msg = "Please upload a valid CSV file."
        else:
            msg = "Form is invalid. Please try again."

    #RENDERING THE DATA ON THE TEMPLATE
    return render(request, 'chat/chat.html', {
        'form': f,
        'msg': msg,
        'form_chat': form_chat,
        'response': response,
        'chat_history': request.session.get('chat_history', []),
        'uploaded_data_preview': uploaded_data_preview,
        'visualization_data': visualization_data,
        'graph_type': graph_type,
    })