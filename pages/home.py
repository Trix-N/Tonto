#####################################################################################################
# név                            #                                                                                 
# Verzió:v1 | Utolsó módosítás: YYYY.MM.DD.| Natrix                                                 #
#####################################################################################################
#aka Project_

# -*- coding: utf-8 -*-
import os #Beolvasási útvonal címzéshez
from pathlib import Path #Fájlkezeléshez
import pandas as pd #Adatfeldolgozáshoz
from dash import html

db="01_Adatbázis" 
input="02_Input"
output="04_Output"

current_code_path=Path(os.path.realpath(os.path.dirname(__file__)))  #Mindig a kód helyéhez képest keressi az inputokat stb., tehát a projekt mappa szabadon másolható bárhova.
current_proj_path=current_code_path.parent.parent

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


layout = html.Div([
    html.Div(
        id='home-content-div-id',
        className='home-content-div-class',
        children=[
            html.H1("Üdvözöllek az időjárás előrejelzést mutató weboldalamom"),

        ],

    )
])