from django.shortcuts import render
from map.forms import SearchForm

import requests
import folium
import polyline
import geocoder

def get_route(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat):
    
    loc = "{},{};{},{}".format(pickup_lon, pickup_lat, dropoff_lon, dropoff_lat)
    url = "http://router.project-osrm.org/route/v1/driving/"
    r = requests.get(url + loc) 
    if r.status_code!= 200:
        return {}
  
    res = r.json()   
    routes = polyline.decode(res['routes'][0]['geometry'])
    start_point = [res['waypoints'][0]['location'][1], res['waypoints'][0]['location'][0]]
    end_point = [res['waypoints'][1]['location'][1], res['waypoints'][1]['location'][0]]
    distance = res['routes'][0]['distance']
    dur=res["routes"][0]['duration']
    out = {'route':routes,
           'start_point':start_point,
           'end_point':end_point,
           'distance':distance,
           'duration':dur
          }

    return out

def get_map(route):
    
    m = folium.Map(location=[(route['start_point'][0] + route['end_point'][0])/2, 
                             (route['start_point'][1] + route['end_point'][1])/2], 
                   zoom_start=8)

    folium.PolyLine(
        route['route'],
        weight=8,
        color='blue',
        opacity=0.6
    ).add_to(m)

    folium.Marker(
        location=route['start_point'],
        icon=folium.Icon(icon='play', color='green')
    ).add_to(m)

    folium.Marker(
        location=route['end_point'],
        icon=folium.Icon(icon='stop', color='red')
    ).add_to(m)

    return m

def get_address(a):
    g = geocoder.osm(a, method='reverse')
    c=g.json
    return c['address']

def index(request):
    form=SearchForm()
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            l1=form['city1'].value()
            l2=form['city2'].value()
            location1 = geocoder.osm(l1)
            lat1 = location1.lat
            lng1 = location1.lng
            location2 = geocoder.osm(l2)
            lat2 = location2.lat
            lng2 = location2.lng
            test_route = get_route(lng1, lat1,lng2,lat2)
            distance=test_route['distance'] * 0.000621371
            duration=(test_route['duration']/60)/60
            c=[]
            for a in test_route['route']:
                c.append(get_address(a))
            m=get_map(test_route)
            m = m._repr_html_()
            context = {
                'm': m,
                'form':form,
                'start':l1,'end':l2,
                'start_loc':location1.latlng,'end_loc':location2.latlng,
                'distance': '{0:.2f}'.format(distance),'duration':'{0:.2f}'.format(duration),
                'route':c
            }
            return render(request, 'map/index.html', context)
    else:
        form=SearchForm()
        context = {
                'form':form
            }
        return render(request, 'map/index.html', context)
