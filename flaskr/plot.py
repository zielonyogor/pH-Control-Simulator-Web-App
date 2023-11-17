import plotly.express as px

def create_plot(name):
    # Your plot creation logic here
    fig = px.scatter(x=[1, 2, 3, 4], y=[10, 11, 12, 13], labels={'x': name, 'y': 'Y-axis'})
    return fig