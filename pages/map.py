#####################################################################################################
# név                            #                                                                                 
# Verzió:v1 | Utolsó módosítás: YYYY.MM.DD.| Natrix                                                 #
#####################################################################################################
#aka Project_

# -*- coding: utf-8 -*-
import os #Beolvasási útvonal címzéshez
from pathlib import Path #Fájlkezeléshez
import pandas as pd #Adatfeldolgozáshoz
import json
import dash_leaflet as dl
from dash import html, Output, Input, callback
import dash_bootstrap_components as dbc
from shapely.geometry import LineString
from shapely.ops import linemerge, unary_union, polygonize
import numpy as np
from dash_svg import Svg, Polygon

from _modules import data_downloader_MEANDER as ddMEANDER

db="01_Adatbázis" 
input="02_Input"
output="04_Output"
temp="05_Temp"

current_code_path=Path(os.path.realpath(os.path.dirname(__file__)))  #Mindig a kód helyéhez képest keressi az inputokat stb., tehát a projekt mappa szabadon másolható bárhova.
current_proj_path=current_code_path.parent.parent

#########Adatbázisok######################
db01_path=os.path.join(current_proj_path,db,"DB.json")
##########################################
# # # # #Beolvasás# # # # # # # # # # # #
with open(db01_path, "r", encoding="utf-8") as f:
    db01_json = json.load(f)
# # # # # # # # # # # # # # # # # # # # #

##########################################

#########Inputok#################

###########################################
# # # # #Beolvasás# # # # # # # # # # # # 

# # # # # # # # # # # # # # # # # # # # #

##########################################

#########Output elérési útvonal###########

##########################################

#########Temp elérési útvonal#############
tmp01_path=os.path.join(current_proj_path,temp,"02_MEANDER_nc_files")
##########################################

def df_load(data, df):

    weather = data['weather']
    weather_types = weather['weather_types']
    presWeather_types = weather['presWeather_types']
    color_scale = data['color_scale']

    emoji_map = {float(k): v[1] for k, v in weather_types.items()}
    weather_types_map={float(k): v[0] for k, v in weather_types.items()}
    presWeather_types_map={float(k): v for k, v in presWeather_types.items()}

    df["simpleWeather"] = df["simpleWeather"].astype(float)
    df["presWeather"] = df["presWeather"].astype(float)
    df["U10"] = df["U10"].astype(float)
    df["V10"] = df["V10"].astype(float)


    df["emoji"] = df["simpleWeather"].map(emoji_map)
    df["weather_types_text"]=df["simpleWeather"].map(weather_types_map)
    df["presWeather_types_text"]=df["presWeather"].map(presWeather_types_map)



    df['wind_len'] = np.sqrt(df['U10']**2 + df['V10']**2)+100
    angle_rad = np.arctan2(df['V10'], df['U10'])
    df['angle_deg'] = np.degrees(angle_rad)
    df["color"] = df["T2"].apply(lambda x: color_scale[value_to_color_index(x)])

    return df

def value_to_color_index(val):
    vmin = 231
    vmax = 321
    n_colors = 25

    if val <= vmin:
        return 0
    if val >= vmax:
        return n_colors - 1
    norm = (val - vmin) / (vmax - vmin)
    idx = int(norm * n_colors)
    if idx == n_colors:
        idx = n_colors - 1
    return idx

def load_polygons_from_json(data, df):
    polygons, colors=[], []
    for town, town_data in data["towns_areas"].items():
                elements = town_data.get("elements", [])
                node_coords = {el['id']: (el['lat'], el['lon'])
                            for el in elements if el['type'] == 'node'}

                line_strings = []
                for el in elements:
                    if el['type'] == 'way':
                        coords = [node_coords[n] for n in el['nodes'] if n in node_coords]
                        if len(coords) >= 2:
                            line_strings.append(LineString(coords))

                if not line_strings:
                    return []  # Ha nincs érvényes vonal, hagyjuk ki

                merged = linemerge(line_strings)
                if isinstance(merged, LineString):
                    merged = [merged]

                mls = unary_union(merged)


                polys = list(polygonize(mls))
                polygons.extend(polys)
                colors.extend([df.loc[town, 'color']] * len(polys))

    if len(polygons) != len(colors):
        raise ValueError("Poligonok és színek száma nem egyezik meg.")

    return [
        dl.Polygon(
            positions=[[(lat, lon) for lat, lon in poly.exterior.coords]],
            color=colors[i],
            fillColor=colors[i],
            fillOpacity=0.3,
            opacity=0.3
        )
        for i, poly in enumerate(polygons)
    ]

def load_border_polyline(border_color, data):

    # Csak a node típusú elemek pozícióit gyűjtjük
    hungary_border=data['hungary_border']
    node_coords = {
        el["id"]: (el["lat"], el["lon"])
        for el in hungary_border["elements"] if el["type"] == "node"
    }

    # Vonalak (way) összegyűjtése
    line_strings = []
    for el in hungary_border["elements"]:
        if el["type"] == "way":
            coords = [node_coords.get(n) for n in el["nodes"] if n in node_coords]
            if len(coords) >= 2:
                line_strings.append(LineString(coords))

    # Egyesítjük a vonalakat
    if not line_strings:
        return []

    merged = linemerge(line_strings)
    if isinstance(merged, LineString):
        merged = [merged]
    unioned = unary_union(merged)

    # Vonalak létrehozása `dl.Polyline`-ként
    polylines = []
    for line in unioned.geoms if hasattr(unioned, "geoms") else [unioned]:
        coords = [(lat, lon) for lat, lon in line.coords]
        polyline = dl.Polyline(positions=coords, color=border_color, weight=1.5)
        polylines.append(polyline)

    return polylines

def create_emoji_with_number_icon(emoji, number):
    return dict(
        html=f"""
        <div style="position: relative; width: 40px; height: 40px; font-size: 1.5em; text-align: center;">
            <span>{emoji}</span>
            <div style="
                position: absolute;
                top: -6px;
                right: -2px;
                background: red;
                color: white;
                border-radius: 50%;
                width: 18px;
                height: 18px;
                font-size: 10px;    /* kisebb betűméret */
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid white;
                box-shadow: 0 0 2px rgba(0,0,0,0.5);
                line-height: normal;
            ">
                {number}
            </div>
        </div>
        """,
        className="",
        iconSize=[40, 40]
    )


def get_emoji_markers(df):
    markers = []
    for idx, row in df.iterrows():
        emoji = row["emoji"]
        number = int(row["T2"]-271)  # cseréld le a megfelelő oszlopnévre
        lat = row["lat"]
        lon = row["lon"]
        name=idx
        temp=int(row['T2']-273.15)
        weather_type=row["weather_types_text"]
        presWeather_type=row["presWeather_types_text"]
        icon = create_emoji_with_number_icon(emoji, number)

        marker = dl.DivMarker(
            id=f'map-{idx}_emoji-divmarker-id',
            position=[lat, lon],
            iconOptions=icon,
            children=[
                dl.Tooltip(f"{name}"),
                dl.Popup(html.Div([
                    html.H4(f"{name}"),
                    html.P(f"Hőmérséklet: {temp} °C"),
                    html.P(f"Az időjárás {weather_type}"),
                    html.P(f"{presWeather_type.capitalize()}"),
                ]))
            ]
        )
        markers.append(marker)
    return markers

def create_svg_arrow_icon(angle_degrees, color="pink", length=100):
    height = length + 20
    return dict(
        html=f"""
            <svg width="40" height="{height}" viewBox="0 0 100 {height}"
                 style="transform: rotate({angle_degrees}deg);">
                <polygon points="50,10 60,30 55,30 55,{length} 45,{length} 45,30 40,30"
                         fill="{color}" stroke="black" stroke-width="2"/>
            </svg>
        """,
        className="",
        iconSize=[40, height]
    )

def get_direction(degree):
    directions = [
        "Észak",          # 0°
        "Északkelet",     # 45°
        "Kelet",          # 90°
        "Délkelet",       # 135°
        "Dél",            # 180°
        "Délnyugat",      # 225°
        "Nyugat",         # 270°
        "Északnyugat",    # 315°
        "Észak"           # 360°, ugyanaz mint 0°
    ]
    
    # Biztonság kedvéért normalizáljuk [0, 360) tartományba
    degree = degree % 360

    # Minden irány 45°-os szeletet fed le
    index = int((degree + 22.5) // 45)
    return directions[index]

def get_arrow_marker(df):
    markers=[]
    for idx, row in df.iterrows():
        lat = row["lat"]
        lon = row["lon"]
        angle=row['angle_deg']
        length=row['wind_len']
        name = idx
        wind_gust=row["WGUST"]
        surface_Pa=row["PSFC"]
        wind_dir=get_direction(angle)
        icon = create_svg_arrow_icon(angle, 'green', length)

        marker = dl.DivMarker(
            id=f'map-{idx}_wind-divmarker-id',
            position=[lat, lon],
            iconOptions=icon,
            children=[
                dl.Tooltip(f"{name}"),
                 dl.Popup(html.Div([
                    html.H4(f"{name}"),
                    html.P(f"Szélsebesség: {round(float(length),2)} m/s"),
                    html.P(f"Szélirány: {wind_dir}"),
                    html.P(f"Széllökés: {round(float(wind_gust),2)} m/s"),
                    html.P(f"Felszíni légnyomás: {round(float(surface_Pa/1000),2)} kPa"),
                ]))
            ]
        )
        markers.append(marker)
    return markers

def get_precipitation_bubbles(df):
    bubbles = []

    for idx, row in df.iterrows():
        lat = row["lat"]
        lon = row["lon"]
        precip=row["sumRadPrec"]
        sumprecip_01=row["sumPrec_01hour"]
        visibility=row["Visibility"]
        cloudines=row["cloudines"]
        radius = 10+precip/5 

        color_intensity = int(255 - (precip / 50) * 200) 
        fill_color = f"rgba(0, 0, {color_intensity}, 0.6)"
        
        font_size = radius * 0.8  
        html_icon = f"""
        <svg width="{radius*2}" height="{radius*2}" viewBox="0 0 {radius*2} {radius*2}">
            <circle cx="{radius}" cy="{radius}" r="{radius-2}" fill="{fill_color}" stroke="black" stroke-width="1" />
            <text x="{radius}" y="{radius}" font-size="{font_size}" fill="white" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{int(precip)}</text>
        </svg>
        """
        icon = dict(html=html_icon,  className="", iconSize=[radius*2, radius*2])
        
        bubbles.append(
            dl.DivMarker(
                id=f'map-{idx}_precip-divmarker-id',
                position=[lat, lon],
                iconOptions=icon,
                children=[dl.Tooltip(f"{idx}: {int(precip)} mm"),
                dl.Popup(html.Div([
                    html.H4(f"{idx}"),
                    html.P(f"Előrejelzett csapadék: {int(precip)} mm"),
                    html.P(f"Az elmúlt 1 órában lehullott csapadék: {int(sumprecip_01)} mm"),
                    html.P(f"Borultság: {round(float(cloudines),2)} okta"),
                    html.P(f"Látástávolság: {round(float(visibility)/1000,2)} km"),
                ])
                )]
            )
        )
    return bubbles


layout = dbc.Container(
    id='map-layout-container-id',
    className='map-layout-container-class',
    fluid=True,
    children=
        dbc.Row(
            id='map-layout-row-id',
            className='map-layout-row-class',
            children=[
            dbc.Col(
                id='map-tilelayer_col-col-id',
                className='map-tilelayer_col-col-class',
                children=
                dl.Map(
                    id='map-tilelayer_map-map-id',
                    className='map-tilelayer_map-map-class',
                    center=[47.1, 19.5],
                    zoom=7,
                    children=[
                        dl.TileLayer(),
                    ],
                ),

            ),

            dbc.Col(
                id='map-radioitems_col-col-id',
                className='map-radioitems_col-col-class',
                children=
                    html.Div(
                        id='map-radioitems_container-div-id',
                        className='map-radioitems_container-div-class',
                        children=[
                            html.H5("Válassz térképet:"),
                            dbc.RadioItems(
                                id='map-radio-radioitems-id',
                                options=[
                                    {"label": "Időjárástérkép", "value": 1},
                                    {"label": "Széltérkép", "value": 2},
                                    {"label": "Csapadéktérkép", "value": 3},
                                ],
                                value=1,
                                inline=False,
                            ),

                            html.Div(
                                id='map-space-div-id',
                                className='map-space-div-class',
                            ),

                            html.H5("Térkép módok:"),

                            dbc.RadioItems(
                                id='map-mode-radioitems-class',
                                options=[
                                    {"label": "OpenStreetMap", "value": 1},
                                    {"label": "Dark", "value": 2},
                                    {"label": "White", "value": 3},
                                ],
                                value=1,
                                inline=False,
                            )
                        ],
                    ),
            )
            ]
        ),
)

@callback(
    Output('map-tilelayer_map-map-id', 'children'),
    Input('map-radio-radioitems-id', 'value'),
    Input('map-mode-radioitems-class', 'value')  # <- új bemenet a térkép módhoz
)
def update_map_layers(selected_option, map_mode):

    tile_layers = {
    1: dl.TileLayer(url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"),  # Alap OSM
    2: dl.TileLayer(url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"),  # Sötét
    3: dl.TileLayer(url="https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png")  # Fehér/stílusos
    }


    
    ddMEANDER.nc_downloader_MEANDER(tmp01_path)
    df=ddMEANDER.town_coords_downloader(db01_json, tmp01_path)

    df=df_load(db01_json, df)


    layers = [tile_layers.get(map_mode, tile_layers[1])]  # Default: OSM

    border_color = "white" if map_mode==2 else "grey"

    layers += load_border_polyline(border_color, db01_json)
    
    if selected_option == 1:
        layers += get_emoji_markers(df)
        layers += load_polygons_from_json(db01_json, df)

    elif selected_option == 2:
        layers += get_arrow_marker(df)

    elif selected_option == 3:
        layers += get_precipitation_bubbles(df)

    return layers