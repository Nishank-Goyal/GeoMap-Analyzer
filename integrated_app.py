import os
import pandas as pd
import numpy as np
import math
import folium
from flask import Flask, render_template, request, send_file
from openpyxl import load_workbook
from datetime import datetime
import zipfile
from nbr_app.new import nbr_app
from kpi_app.safaricom import kpi_app

app = Flask(__name__)

app.route("/")
def home():
    return render_template('index.html')
app.register_blueprint(nbr_app, url_prefix='')
app.register_blueprint(kpi_app, url_prefix='')

if __name__ == '__main__':
    app.run(debug=True)