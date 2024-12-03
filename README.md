![ChartyChats](https://github.com/user-attachments/assets/04df2bc3-5563-445c-b7ef-a0b34a6afe18)

# Charty Chats

## Project Description
Charty Chats is a web application designed to generate graphs and visualizations based on CSV data and user-provided natural language input. Users can describe the type of analysis or visualization they require, and the application dynamically generates the corresponding charts.

### Key Highlights
1. Users can specify the desired graph or analysis through a natural language input field.
2. The application employs an LLM backend to interpret user input and generate appropriate visualizations.
3. Charts and graphs are displayed dynamically based on user queries.
4. Users can upload CSV files directly through the web app for data visualization.
5. A chat-like interface ensures a seamless user experience.
6. Provides data insights and summaries based on visualized data.

---

## Features
- **Input Field**: Describe the required graph or analysis in plain language.
- **LLM Integration**: Backend LLM interprets user input and generates visualizations.
- **Dynamic Visualization**: Charts and graphs are created dynamically based on queries.
- **CSV File Upload**: Users can upload CSV data for visualization.
- **Chat-like UI**: Interactive and user-friendly interface for queries and results.
- **Data Insights**: Provides summaries or insights based on visualized data.

---

## Technologies Used
### Programming and Scripting Languages
- Python
- HTML
- CSS
- JavaScript

### Frameworks
- **Django**: Backend framework used for:
  - LLM integration.
  - Handling user input.
  - Displaying input and LLM responses.
  - Rendering output templates.
- **Plotly**: Generates visualizations like bar charts, line graphs, scatter plots, etc.

### LLM
- **Gemini – 1.5 - Flash – 8b**: Used for interpreting user queries and generating responses.

---

## Installation
To set up and run Charty Chats locally, follow these steps:

1. **Activate the Virtual Environment**:
   ```bash
   source <your_virtual_environment>/bin/activate
   ```
2. **Install Dependenceis**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Change Directory: Navigate to the project directory**:
   ```bash
   cd ChartyChats
   ```
4. **Configure the API Key**:
   *Add your Gemini API key in ChartyChats/chat/views.py.*
5. **Run the Development Server**:
   ```bash
    python manage.py runserver
   ```
## Usage

1. Open your browser and navigate to the URL provided by the development server (e.g., `http://127.0.0.1:8000`).
2. Upload a CSV file via the web app.
3. Use the input field to describe the type of graph or analysis you need (e.g., "Show a bar chart of weekly sales").
4. View dynamically generated charts and summaries based on your input.

## Video Demo

https://youtu.be/H59gFs3ldXU  <- Subscribe to my channel  😄👍

