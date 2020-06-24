import dash
import dash_html_components as html
import dash_leaflet as dl
import parse,sys

NAME = sys.argv[1]

df = parse.parse(NAME)
df.to_csv('./test/converted.csv')
print(df.describe())

# markers = [dl.Marker(title=locations.count(item), position=geocoder.osm(item).latlng) for item in list(set(locations))]
# 

mid = [df.lat.median(), df.lon.median()]

what = 'PM10'

mx = df[what].max()


#print (help(dl.Circle))
'''
Keyword arguments:
 |  - children (a list of or a singular dash component, string or number; option
al): The children of this component
 |  - center (list of numbers; required): The center of the circle (lat, lon)
 |  - radius (number; required): Radius of the circle, in meters.
 |  - stroke (boolean; optional): Whether to draw stroke along the path. Set it 
to false to disable borders 
 |  on polygons or circles.
 |  - color (string; optional): Stroke color
 |  - weight (number; optional): Stroke width in pixels
 |  - opacity (number; optional): Stroke opacity
 etc... 
'''

markers = [dl.CircleMarker( dl.Tooltip(str(row)), center=[row[1].lat, row[1].lon], radius=20*row[1][what]/mx, id=str(row[0]), stroke=True,color='red',weight=1,fillColor='blue' ) for row in df.iterrows()]
# cluster = dl.MarkerClusterGroup(id="markers", children=markers, options={"polygonOptions": {"color": "red"}})
# 


app = dash.Dash()
app.layout = html.Div(
id="BornInBradford",
    children=
    dl.Map([dl.TileLayer(),dl.LayerGroup(markers,id='markers')],    
    #dl.WMSTileLayer(url="https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
                                            # layers="nexrad-n0r-900913", format="image/png", transparent=True)],
           center=mid, zoom=10,
           style={'width': '100%', 'height': '50vh', 'margin': "auto", "display": "block"})
)

if __name__ == '__main__':
    app.run_server()