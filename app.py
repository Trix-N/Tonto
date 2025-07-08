#####################################################################################################
# név                            #                                                                                 
# Verzió:v1 | Utolsó módosítás: YYYY.MM.DD.| Natrix                                                 #
#####################################################################################################
#aka Project_

# -*- coding: utf-8 -*-

from dash import Dash
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)
server = app.server 

