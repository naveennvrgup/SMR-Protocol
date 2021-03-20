import pandas as pd
import plotly.graph_objects as go
import numpy as np

df = pd.read_csv('./baltic-sea-coordinates')


fig = go.Figure(go.Scattermapbox(
    lat=df['lat'],
    lon=df['lng'],
    mode='markers',
    marker=go.scattermapbox.Marker(
        size=7
    ),
    # text=['Montreal'],
))

fig.update_layout(
    hovermode='closest',
    mapbox=dict(
        accesstoken='pk.eyJ1IjoibmF2ZWVubnZyZ3VwIiwiYSI6ImNrZ2kxYW9oeTAyODczMm40dWs4MzkwM2cifQ.wlwkYJu5zSryrA5aSIig_A',
        bearing=0,
        # center=go.layout.mapbox.Center(
        #     lat=45,
        #     lon=-73
        # ),
        # pitch=0,
        # zoom=5
    )
)

fig.show()
# fig = go.Figure(data=go.Scatter(x=df['lat'], y=df['lng'], mode='markers'))

fig.show()
