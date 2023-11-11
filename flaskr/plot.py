import plotly.express as px

def create_plot():
    # Your plot creation logic here
    fig = px.scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13], labels={'x': 'X-axis', 'y': 'Y-axis'})
    return fig