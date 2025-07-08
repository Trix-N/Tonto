
#####################################################################################################
# név                            #                                                                                 
# Verzió:v1 | Utolsó módosítás: YYYY.MM.DD.| Natrix                                                 #
#####################################################################################################
#aka Project_

# -*- coding: utf-8 -*-

import os #Beolvasási útvonal címzéshez
from pathlib import Path #Fájlkezeléshez
import pandas as pd #Adatfeldolgozáshoz
from dash import html, dcc, Input, Output, callback
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta
import pytz
import json
import requests
from _modules import data_downloader_FOCUS as ddFOCUS

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
output_abspath=os.path.join(current_proj_path,output)  
##########################################

#########Temp elérési útvonal#############
tmp01_path=os.path.join(current_proj_path,temp,"01_FOCUS_nc_files")
##########################################

def town_options():
    data=db01_json
    towns= data["towns"]
    town_options = [
        {"label": town, "value": town}
        for town in towns.keys()
    ]
    return town_options

def df_load(data, df):
    now = datetime.now(pytz.timezone("Europe/Budapest"))
    weather = data['weather']
    weather_types = weather['weather_types']
    precipitation_types = weather['precipitation_types']
    cover_types = weather['cover_types']



    emoji_map = {float(k): v[1] for k, v in weather_types.items()}
    weather_types_map={float(k): v[0] for k, v in weather_types.items()}
    precipitation_types_map={float(k): v for k, v in precipitation_types.items()}
    cover_types_map={float(k): v for k, v in cover_types.items()}

    df["weather24h"] = df["weather24h"].astype(float)
    df["newPtypeWT24h"] = df["newPtypeWT24h"].astype(float)
    df["newCloudyWT24h"] = df["newCloudyWT24h"].astype(float)

    df["emoji"] = df["weather24h"].map(emoji_map)
    df["precipitation_types_text"]=df["newPtypeWT24h"].map(precipitation_types_map)
    df["cover_types_text"]=df["newCloudyWT24h"].map(cover_types_map)
    df["weather_types_text"]=df["weather24h"].map(weather_types_map)


    napnevek, date_list, day_list = ['Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap'], [], []
    for i in range(7):
        nap = now + timedelta(days=i)
        nap_date=nap.strftime('%m.%d.')
        nap_nev = napnevek[nap.weekday()]
        day_list.append(nap_nev)
        date_list.append(nap_date)

    df["day_name"]=day_list
    df["dates"]=date_list
    return df

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

def other_column(town_coords):
    # Koordináták Budapesthez
    lat, lon = town_coords

    # Időzóna beállítása
    budapest = pytz.timezone("Europe/Budapest")
    now = datetime.now(budapest)
    now_str = now.strftime('%Y-%m-%dT%H:00')

    # API hívás - Budapest időzónával
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m&timezone=Europe%2FBudapest"
    response = requests.get(url)
    data = response.json()

    times = data['hourly']['time']
    temps = data['hourly']['temperature_2m']

    # Kezdő index meghatározása
    start_index = times.index(now_str)

    # Következő 24 órányi adat
    selected_times = times[start_index:start_index+24]
    selected_temps = temps[start_index:start_index+24]

    # DataFrame pontos időbélyegekkel (nem csak órákkal)
    df = pd.DataFrame({
        'time': pd.to_datetime(selected_times),  # datetime objektum!
        'value': selected_temps
    })

    # Vonalas + emoji nélküli grafikon
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['value'],
        mode='lines+markers',
        line=dict(width=3, color='teal'),
        hovertemplate='<b>Idő:</b> %{x|%H:%M}<br><b>Hőmérséklet:</b> %{y:.2f} °C<extra></extra>'
    ))

    fig.update_layout(
        title={
        'text': "Óránkénti hőmérséklet előrejelzés<br>a következő 24 órára",
        'x': 0.5,  # 0 = balra, 1 = jobbra, 0.5 = középre
        'xanchor': 'center'
        },
        yaxis_title="Hőmérséklet (°C)",
        xaxis_title="Idő (óra)",
        xaxis=dict(
            tickformat="%H:%M",
            tickangle=0
        ),
        yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='gray'),
        template='plotly_white',
        margin=dict(
        l=150,  
        )
    )

    return html.Div([
        dcc.Graph(figure=fig, id='diagram-time_series-graph-id')
    ])

def number_icon(number, color):
    return html.Div(

        id='diagram-number_icon-div-id',
        className='diagram-number_icon-div-class',
        style={
            "backgroundColor":color,  # kék szín (Bootstrap kék)
        },
        children=str(number)
    )

def column(df):
    children=[]
    for idx, row in df.iterrows():

        children.append(
            html.Div(
                id='diagram-container-div-id',
                className='diagram-container-div-class',
                children=[

                    html.Div(
                        id='diagram-bars-div-id',
                        className='diagram-bars-div-class',
                        children=[

                            html.Div(
                                id=f'diagram-{idx}_day-div-id',
                                className='diagram-idx_day-div-id',
                                children=[

                                    html.Span(
                                        id=f'diagram-{idx}_emoji-span-id',
                                        className='diagram-idx_emoji-span-class',
                                        children=row['emoji'],
                                    ),

                                    html.Div(
                                        id='diagram-TMin-div-id',
                                        className='diagram-temp-div-class',
                                        style={'top': f'{40+(int(row['TMin2'])-50)*65/-60}%'},
                                        children=[number_icon(int(row['TMin2']),  '#007BFF')]
                                    ),
                                    
                                    html.Div(
                                        id='diagram-TMax-div-id',
                                        className='diagram-temp-div-class',
                                        style={'top': f'{25+(int(row['TMax2'])-50)*65/-60}%'},
                                        children=[number_icon(int(row['TMax2']),  '#FF1100')]
                                    ),
                                ]
                            ),
                                        # Piros rész
                            html.Div(
                                id=f'diagram-{idx}_rain-div-id',
                                className='diagram-idx_rain-div-class',
                                children=f'{round(float(row['Prec24h']), 1)} mm',
                            ),
                            html.Div(
                                id='diagram-dates-div-id',
                                className='diagram-dates-div-class',
                                children =f"{row['dates']}",
                            )
                        ],
                    ),
                    html.Div(
                        id='diagram-day_name-div-id',
                        className='diagram-day_name-div-class',
                        children=row['day_name']
                    ),

                    dbc.Tooltip(
                        id='diagram-wind_tooltip-tooltip-id',
                        className='diagram-wind_tooltip-tooltip-class',
                        target=f'diagram-{idx}_day-div-id',
                        placement="right",
                        delay={"show": 300, "hide": 100},
                        autohide=True,
                        children=
                            html.Div(
                                children=[
                                        html.B("Szél"),
                                        html.Br(),
                                        f"Szélsebesség: {round(float(row['WSpeed24h']),1)} m/s",
                                        html.Br(),
                                        f"Szélirány: {get_direction(row['WDir24h'])}",
                                    ]
                            ),

                    ),

                    dbc.Tooltip(
                        id='diagram-weather_type_text_tooltip-tooltip-id',
                        className='diagram-weather_type_text_tooltip-tooltip-class',
                        target=f'diagram-{idx}_emoji-span-id',
                        placement="right",
                        delay={"show": 300, "hide": 100},
                        autohide=True,
                        children=
                            html.Div(
                                children=[
                                    html.B("Időkép: "), f"{row["weather_types_text"].capitalize()}"
                                ]
                            ),

                    ),

                    dbc.Tooltip(
                        id='diagram-rain_tooltip-tooltip-id',
                        className='diagram-rain_tooltip-tooltip-class',
                        target=f'diagram-{idx}_rain-div-id',
                        placement="right",
                        delay={"show": 300, "hide": 100},
                        autohide=True,
                        children=
                            html.Div(
                                children=[
                                    html.B("Felhőkép: "), f"{row["cover_types_text"].capitalize()}\n",
                                    html.B("Csapadék: "), f"{row["precipitation_types_text"].capitalize()}",
                                ]
                            ),
                    ),
                     
                ],
            
            )   
        )
    return children


layout=html.Div(
    id='diagram-layout-div-id',
    className='diagram-layout-div-class',
    children=[
        html.Div(
            id='diagram-dropdown_container-div-id',
            className='diagram-dropdown_container-div-class',
            children=[
                dcc.Dropdown(
                    id='diagram-town_dropdown-dropdown-id',
                    className='diagram-dropdown-class',
                    options=town_options(),
                    value=list(db01_json["towns"].keys())[0],
                    clearable=False,
                ),
                dcc.Dropdown(
                    id='diagram-timeseries_prediction_dropdown-dropdown-id',
                    className='diagram-dropdown-class',
                    options=[
                        {"label": "Heti előrejelzés", "value": "m1"},
                        {"label": "Napi előrejelzés", "value": "m2"},
                    ],
                    value="m1",
                    clearable=False,
                ),
        ]
),

        html.Div(
            id='diagram-timeseries_prediction-div-id',
            className='diagram-timeseries_prediction-div-class',
            children=[
                html.Div(
                    id='diagram-dynamic_timeseries_prediction-div-id',
                    className='diagram-dynamic_timeseries_prediction-div-class',
                    children=column(pd.DataFrame()),
                )]),


    ]
)

@callback(
    Output('diagram-dynamic_timeseries_prediction-div-id', 'children'),
    Input('diagram-town_dropdown-dropdown-id', 'value'),
    Input('diagram-timeseries_prediction_dropdown-dropdown-id', 'value')
)
def update_column(town, value):

    data=db01_json
    town_coords=data["towns"][town]
    if value == 'm1': 
        ddFOCUS.nc_downloader_FOCUS(tmp01_path)
        df=ddFOCUS.town_coords_downloader(town_coords, tmp01_path)
        df=df_load(data, df)
        return column(df)
    else:
        return other_column(town_coords)  
