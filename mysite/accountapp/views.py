from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from accountapp.models import HelloWorld
import geokakao as gk
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

boundary = gpd.read_file('../secret_datas/grid/LARD_ADM_SECT_SGG_11.shp').to_crs('epsg:4326')
gdf = gpd.read_file('../secret_datas/no_duplicated_flood_grid.json')

# 색상 지정
custom_colorscale = [
    [0, "rgb(255, 255, 127)"],
    [1/4, "rgb(191, 255, 0)"],
    [2/4, "rgb(0, 255, 255)"],   
    [3/4, "rgb(191, 127, 255)"], 
    [1, "rgb(191, 127, 255)"]
]


fig = go.Figure()


fig.add_trace(go.Choroplethmapbox(geojson=gdf.geometry.__geo_interface__, 
                                locations=gdf.index, 
                                z=gdf['FLUD_GD'],
                                colorscale=custom_colorscale,
                                showscale=False,  #원래 범례 제거
                                marker_opacity=0.7,
                                marker_line_width=0,
                                marker_line_color='rgba(0,0,0,0)', 
                                hoverinfo='text',
                                hovertext=gdf[['FLUD_GD', 'FLUD_SHIM']].apply(lambda x: f"침수등급: {int(x['FLUD_GD'])}등급 <br>침수심: {x['FLUD_SHIM']}m", axis=1))) #hover내용

# 범례 생성
legend_colors = [item[1] for item in custom_colorscale]
legend_labels = ["1등급", "2등급", "3등급", "4등급"]

for color, label in zip(legend_colors, legend_labels):
    fig.add_trace(go.Scattermapbox(lat=[None], lon=[None],
                                marker=dict(size=10, color=color),
                                showlegend=True, name=label))

# 서울시 경계
def add_polygon_boundary_to_fig(boundary, fig):
    for _, row in boundary.iterrows():
        x, y = row['geometry'].exterior.xy
        fig.add_trace(
            go.Scattermapbox(
                mode="lines",
                lon=list(x),   
                lat=list(y),  
                marker=dict(size=0),
                line=dict(width=1, color="black"),
                showlegend=False,
                hoverinfo = 'none'
            )
        )
    return fig

def hello_world(request):
    temp = request.POST.get('hello_world_input')
    
    if temp:
        temp = pd.DataFrame([temp], columns=['Address'])
        gk.add_coordinates_to_dataframe(temp, 'Address')
        temp = temp.values[0]

        # fig.update_layout(mapbox_style="open-street-map", 
        #           mapbox_zoom=15, 
        #           mapbox_center={"lat": 37.5286, "lon": 126.9135},  #여의도 국회의사당 기준
        #           width=1200, height=750,
        #           legend_orientation="h",
        #           legend_y=0.99, 
        #           legend_x=0.01, 
        #           legend_traceorder="normal", 
        #           legend_title="침수 등급", 
        #           legend_font=dict(size=14, family="bold"))
        # fig = add_polygon_boundary_to_fig(boundary, fig)

        global fig
        
        fig.update_layout(mapbox_style="open-street-map", 
                    mapbox_zoom=15, 
                    mapbox_center={"lat": float(temp[1]), "lon": float(temp[2])},  #여의도 국회의사당 기준
                    width=1200, height=750,
                    legend_orientation="h",
                    legend_y=0.99, 
                    legend_x=0.01, 
                    legend_traceorder="normal", 
                    legend_title="침수 등급", 
                    legend_font=dict(size=14, family="bold"))
        fig = add_polygon_boundary_to_fig(boundary, fig)

        # new_hello_world = HelloWorld()	# 모델에서 테이블 인스턴스 변수 선언
        # new_hello_world.text = str(fig.to_json()).replace('False', 'false')     # text column에 temp 입력
        # # new_hello_world.text = new_hello_world.text
        # # return render(request, 'accountapp/hello_world.html', context={'hello_world_list': fig.to_json()})
        # # new_hello_world.text = fig.to_json()     # text column에 temp 입력
        # new_hello_world.save()          # 모델에 해당 record 저장

        # hello_world_list = HelloWorld.objects.all()
        return render(request, 'accountapp/hello_world.html', context={'hello_world_list': str(fig.to_json()).replace('False', 'false')})
        # return HttpResponseRedirect(reverse('accountapp:hello'))
    
    else:
        hello_world_list = HelloWorld.objects.all()
        hello_world_list = hello_world_list[len(hello_world_list)-5:]
        hello_world_list = hello_world_list[-1].text
        return render(request, 'accountapp/hello_world.html', context={'hello_world_list': hello_world_list})
