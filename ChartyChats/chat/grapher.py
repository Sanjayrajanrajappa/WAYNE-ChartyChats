import plotly.graph_objects as go
from plotly.offline import plot

def graphGenerator(data):
    #INITIALIZE THE FIGURE
    fig = go.Figure()
    
    #FINDING THE GRAPH TYPE FROM THE JSON PASSED
    for graph in data['data']:
        graph_type = graph.get('type', 'scatter') #DEFAULT SET TO SCATTER

        #CHECK FOR THE GRAPH TYPE PRESENT IN THE JSON

        if graph_type == 'bar':
            fig.add_trace(go.Bar(x=graph['x'], y=graph['y'], name=graph.get('name', '')))
        elif graph_type == 'line':
            fig.add_trace(go.Scatter(x=graph['x'], y=graph['y'], mode='lines', name=graph.get('name', '')))
        elif graph_type == 'scatter':
            mode = graph.get('mode', 'markers')  
            fig.add_trace(go.Scatter(x=graph['x'], y=graph['y'], mode=mode, name=graph.get('name', '')))
        elif graph_type == 'pie':
            fig.add_trace(go.Pie(labels=graph['labels'], values=graph['values'], name=graph.get('name', '')))
        elif graph_type == 'histogram':
            fig.add_trace(go.Histogram(x=graph['x'], name=graph.get('name', '')))
        elif graph_type == 'box':
            fig.add_trace(go.Box(y=graph['y'], name=graph.get('name', '')))
        else:
            raise ValueError(f"Unsupported graph type: {graph_type}")

    #LAYOUT TO BE SET DYANAMICALLY BASED ON THE GRAPH TYPE
    layout = {}

    #LABELS ON THE GRAPH
    layout.update({
        'title': data.get("title", ""),
        'xaxis_title': data.get("xaxis_title", ""),
        'yaxis_title': data.get("yaxis_title", ""),
    })
    
    #LABELING OR LAYOUT BASED ON THE GRAPH
    for graph in data['data']:
        graph_type = graph.get('type', 'scatter')

        if graph_type == 'pie':
            layout.update({
                'showlegend': True,
                'title': graph.get('name', data.get('title', '')),
            })
        elif graph_type == 'scatter' or graph_type == 'line':
            layout.update({
                'xaxis': {'title': data.get('xaxis_title', '')},
                'yaxis': {'title': data.get('yaxis_title', '')},
                'showlegend': True
            })
        elif graph_type == 'bar':
            layout.update({
                'xaxis': {'title': data.get('xaxis_title', '')},
                'yaxis': {'title': data.get('yaxis_title', '')},
                'showlegend': True
            })
        elif graph_type == 'histogram':
            layout.update({
                'xaxis': {'title': data.get('xaxis_title', '')},
                'yaxis': {'title': data.get('yaxis_title', '')},
                'showlegend': True
            })
        elif graph_type == 'box':
            layout.update({
                'yaxis': {'title': data.get('yaxis_title', '')},
                'showlegend': True
            })
    
    #SELECTING THE FINAL LAYOUT THAT HAS MATCHED WITH THE INPUT
    fig.update_layout(layout)

    #PLOTTING
    graph_html = plot(fig, output_type='div', include_plotlyjs='cdn')
    return graph_html
