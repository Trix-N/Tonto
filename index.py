#####################################################################################################
# név                            #                                                                                 
# Verzió:v1 | Utolsó módosítás: YYYY.MM.DD.| Natrix                                                 #
#####################################################################################################
#aka Project_

# -*- coding: utf-8 -*-
import os #Beolvasási útvonal címzéshez
from pathlib import Path #Fájlkezeléshez
import pandas as pd #Adatfeldolgozáshoz
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output


from app import app
from pages import diagram, home, map


db="01_Adatbázis" 
input="02_Input"
output="04_Output"

current_code_path=Path(os.path.realpath(os.path.dirname(__file__)))  #Mindig a kód helyéhez képest keressi az inputokat stb., tehát a projekt mappa szabadon másolható bárhova.
current_proj_path=current_code_path.parent

#########Adatbázisok######################

##########################################
# # # # #Beolvasás# # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # #

##########################################

#########Inputok#################

###########################################
# # # # #Beolvasás# # # # # # # # # # # #

# # # # # # # # # # # # # # # # # # # # #

##########################################

#########Output elérési útvonal###########

##########################################


nav = dbc.Navbar(
    dbc.Container([

        html.Div([

            html.A(
                html.Img(src='/assets/meteorology.png', height='40px', id='index-logo-img-id'),  
                href='/',
                className='index-logo-a-class',
                id='index-logo-a-id',
            ),

            dbc.DropdownMenu(
                
                children=[
                    dbc.DropdownMenuItem(
                        'Diagram', 
                        href='/diagram', 
                        className='index-navlink-class',
                        id='index-diagram-dropdownmenuitem-id'),
                    dbc.DropdownMenuItem(
                        'Térkép', 
                        href='/diagram/map', 
                        className='index-navlink-class',
                        id='index-map-dropdownmenuitem-id'),
                ],
                label='Időjárás előrejelzés',
                nav=True,
                in_navbar=True,
                style= {"marginLeft": "15px"},
                className='index-navlink-class',
                id='index-weatherplot-dropdownmenu-id',
            ),
        ], 
        
        className='index-weatherplot-div-class',
        id='index-weatherplot-div-id',
        
        ),

        dbc.Nav([
                dbc.NavItem(
                    dbc.NavLink(
                        'Kapcsolat', 
                        href='/contact',
                        className='index-navlink-class',
                        id='index-contact-navlink-id'
                        ), 
                    className='index-navitem-class',
                    id='index-contact-navitem-id'
                ),
            ],
            navbar=True,
            className='index-contact-nav-class',  # Jobbra tolja
            id='index-contact-nav-id'
        )

    ]),

    dark=True,
    sticky='top',
    className='index-nav-container-class',
    id='index-nav-container-id'
)



app.layout = dbc.Container([
    dcc.Location(id='index-url-location-id', refresh=False),
    nav,
    html.Div(id='index-page_content-div-id')
], 
fluid=True,
id='index-layout-container-id'
)

@app.callback(
    Output('index-page_content-div-id', 'children'),
    Input('index-url-location-id', 'pathname')
)
def display_page(pathname):
    if pathname == '/' or pathname == '/home':
        return home.layout
    elif pathname == '/diagram':
        return diagram.layout
    elif pathname == '/diagram/map':
        return map.layout
    else:
        return html.H2("404 – Nincs ilyen oldal", id='index-page_error-h2-id')

if __name__ == '__main__':
    app.run(debug=True)