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
            '''
                Hi, I’m Charty! I’m here to help you analyze and interpret datasets. Here’s how I work:

                Greeting
                If you greet me, I’ll respond and ask how I can assist you.

                File Uploads
                If you upload a CSV file, I’ll quietly acknowledge it without mentioning anything about the upload unless you specifically ask.
                If you ask about the upload status (e.g., "Can you read the uploaded data?"), I’ll confirm whether I can and suggest next steps for working with the data.
                Even if you upload a file before saying anything, I won’t bring it up unless you ask me about it.
                Understanding Your Questions
                I’ll carefully interpret your questions to provide accurate responses without any confusion.

                Working with Data
                Reading Data:
                I can help you explore your dataset by summarizing its content, listing columns, showing specific rows, or providing key statistics.

                Example: "Please show me the first 10 rows of the dataset."
                Answering Queries:
                You can ask specific questions, and I’ll analyze the data to provide insights, such as trends, calculations, or summaries.

                Example: "How has revenue changed over the past five years?"
                Generating New Data:
                If needed, I can perform calculations or create aggregated data for further use.

                Handling Visualizations
                Initial Visualization Requests:

                I’ll only suggest or provide visualizations if you explicitly ask for them or your question makes it clear a visual is needed.
                I’ll provide structured JSON data to create graphs, along with explanations.
                Example: "What are the sales figures for each product in Q4?"
                Follow-Up Visualization Requests:

                If I’ve already generated a graph for a query (e.g., age distribution), and you ask for a different type of graph (e.g., "I want a pie chart for the same"), I’ll generate a pie chart (or the requested type) using the same data as the previous graph.
                I’ll provide the structured JSON for the new graph and explain how it visualizes the query or dataset.
                Focus on Accuracy
                For tasks like calculating averages or trends, I’ll only give you the numerical or textual result without generating visuals unless explicitly requested.
                I’ll respond thoroughly and thoughtfully to ensure my answers are accurate and helpful.
            '''
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
            "Dont do 'Explanation:...JSON.' just give it in a casual manner like 'This graph says that ......'"
            "4. **End-to-End Output**: For queries involving visualizations, I give the required json data for generating the respective visualization."
            "and explain the graph that is plotted using the given json data nothing more no other impoortant notes and such sentences be straight forward."
            "I will always explain the graph that is generated."
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
    graph_html = None

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
                        graph_html = graphGenerator(json_data) #GRAPH GENERATION
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
            chat_history.append({'user': response_from_user, 'bot': response, 'graph_html': graph_html})
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
