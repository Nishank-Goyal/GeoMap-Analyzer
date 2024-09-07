import os
import pandas as pd
import numpy as np
import math
import folium
from flask import Flask, render_template, request, send_file, Blueprint

app = Flask(__name__)
nbr_app = Blueprint('nbr_app', __name__, template_folder='templates')

# # Create input and output folders if they don't exist
# input_folder = "nbr_input"
# output_folder = "nbr_output"

# Create input and output folders inside the nbr_app folder if they don't exist
input_folder = os.path.join(os.path.dirname(__file__),  "nbr_input")
output_folder = os.path.join(os.path.dirname(__file__), "nbr_output")

if not os.path.exists(input_folder):
    os.makedirs(input_folder)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Global variables to store data and map
uploaded_data = None
generated_map = None
nbr_relations_df = None
uploaded_filename = None  # Store the uploaded file name

# Function to calculate sector vertices based on azimuth
def calculate_sector_vertices(lat, lon, radius, azimuth, angle):
    vertices = [(lat, lon)]
    for i in range(-angle // 2, angle // 2 + 1):
        x = lat + radius * math.cos(math.radians(azimuth + i))
        y = lon + radius * math.sin(math.radians(azimuth + i))
        vertices.append((x, y))
    return vertices

# Function to remove the file extension
def remove_extension(filename):
    base_name = os.path.splitext(filename)[0]
    return base_name

@nbr_app.route('/')
def home():
    return render_template('index.html')

@nbr_app.route('/nbr')
def nbr():
    return render_template('nbr_index.html')

@nbr_app.route('/upload', methods=['GET', 'POST'])
def upload():
    global uploaded_data, uploaded_filename
    if 'file' in request.files:
        file = request.files['file']
        if file:
            uploaded_filename = file.filename
            file.save(os.path.join(input_folder, uploaded_filename))
            uploaded_data = pd.read_excel(os.path.join(input_folder, uploaded_filename))
    return render_template('nbr_upload.html')

@nbr_app.route('/generate_map', methods=['GET', 'POST'])
def generate_map():
    global uploaded_data, generated_map, uploaded_filename
    if uploaded_data is not None:
        try:
            # Read the data from the uploaded file
            df = uploaded_data.copy()

            # Create a Folium map centered at the mean coordinates of your DataFrame
            m = folium.Map(location=[df['Lat(in decimal)'].mean(), df['Long(in decimal)'].mean()], zoom_start=13)

            # Initialize the plan DataFrame
            plan = pd.DataFrame()

            # Your map generation code here
            for index, row in df.iterrows():
                lat, lon = float(row['Lat(in decimal)']), float(row['Long(in decimal)'])
                azimuth = float(row['AZIMUTH'])
                radius = 0.01  # Adjust the radius as needed
                angle = 60  # Adjust the angle as needed

                # Categorize azimuth values into three groups based on some criteria
                if azimuth < 90:
                    color = 'red'
                elif azimuth < 240:
                    color = 'yellow'
                else:
                    color = 'blue'

                # Calculate sector vertices
                vertices = calculate_sector_vertices(lat, lon, radius, azimuth, angle)

                # Create a Folium Polygon to represent the sector with the assigned color
                folium.Polygon(
                    locations=vertices,
                    color=color,  # Color of the sector
                    fill=True,
                    fill_color=color,  # Fill color of the sector
                    fill_opacity=0.3,
                ).add_to(m)

                # Create a label with the Site ID and add it as a marker
                folium.Marker(
                    location=[lat, lon],
                    icon=folium.DivIcon(html=f"<div>{row['Site ID']}</div>"),
                    tooltip=row['Site ID']
                ).add_to(m)

            # Check if m is a Folium map before saving
            map_filename = os.path.join(output_folder, f"{remove_extension(uploaded_filename)}_map.html")
            m.save(map_filename)

            # Render the map template with the map content
            map_download_link = f"/download_map?file={remove_extension(uploaded_filename)}"
            map_content = m.get_root().render()
            return render_template('nbr_map.html', map_content=map_content, map_download_link=map_download_link)
        except Exception as e:
            return f"An error occurred: {str(e)}"
    else:
        return "Upload a file first"

@nbr_app.route('/download_map')
def download_map():
    try:
        filename = request.args.get('file')
        if filename:
            # Provide the option to download the generated map with the same name as the input file
            map_filename = os.path.join(output_folder, filename + "_map.html")
            return send_file(map_filename, as_attachment=True)
        else:
            return "File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

@nbr_app.route('/plan_nbr', methods=['GET', 'POST'])
def plan_nbr():
    global uploaded_data, nbr_relations_df, uploaded_filename
    if uploaded_data is not None:
        # Read the data from the uploaded file
        df = uploaded_data.copy()

        # Your NBR plan generation code here
        cols = df.columns.tolist()

        mmfc = df.copy()
        plan = pd.DataFrame()
        final = pd.DataFrame(columns=cols)
        result = pd.DataFrame()

        plan = pd.concat([plan, df[df['NBR Plan'] != 'Yes']])

        df3 = pd.DataFrame()

        for Cell_id, Site_id, long_a, lat_a, azi_a in zip(plan["Cell ID"], plan["Site ID"], plan["Long(in decimal)"], plan["Lat(in decimal)"], plan["AZIMUTH"]):
            Dist = []

            for long_b, lat_b in zip(mmfc["Long(in decimal)"], mmfc["Lat(in decimal)"]):
                d = 108 * (math.sqrt((long_a - long_b) ** 2 + (lat_a - lat_b) ** 2))
                Dist.append(d)

            mmfc["Distance"] = Dist
            Dist = []

            mmfc = mmfc.sort_values(by='Distance')

            StoS = []
            StoS_final = []
            StoA = []
            StoA_final = []
            StoB = []
            StoB_final = []
            Azi = []
            Grade = []

            for long_b, lat_b, azi_b in zip(mmfc["Long(in decimal)"], mmfc["Lat(in decimal)"], mmfc["AZIMUTH"]):
                n = math.degrees(math.atan2(lat_b - lat_a, long_b - long_a))
                StoS.append(n)

                m = -90 - int(n) if n <= -90 else 270 - int(n)
                StoS_final.append(m)

                p = 360 + (azi_b - m) if m > azi_b else azi_b - m
                StoA.append(p)

                q = 360 - p if p > 180 else p
                StoA_final.append(q)

                r = 360 + (azi_a - m) if m > azi_a else azi_a - m
                StoB.append(r)

                s = r - 180 if r > 180 else 180 - r
                StoB_final.append(s)

                t = 10 if (s + q) < 10 else s + q
                Azi.append(t)

                x = d * t
                Grade.append(x)

            mmfc["S to S"] = StoS
            mmfc["S to S Final"] = StoS_final
            mmfc["S to A"] = StoA
            mmfc["S to A Final"] = StoA_final
            mmfc["S to B"] = StoB
            mmfc["S to B Final"] = StoB_final
            mmfc["Azi"] = Azi
            mmfc["Grade"] = Grade

            StoS = []
            StoS_final = []
            StoA = []
            StoA_final = []
            StoB = []
            StoB_final = []
            Azi = []
            Grade = []

            mmfc = mmfc.sort_values (by ='Grade')

            df2 = pd.DataFrame()
            df2 = mmfc[['Cell ID', 'Site ID', 'Distance', 'Azi', 'Grade']].copy().iloc[:25]
            df2["Cell ID(Plan)"] = Cell_id
            df2["Site ID(Plan)"] = Site_id

            df3 = pd.concat([df3, df2])

        selected_columns = ['Cell ID(Plan)', 'Site ID(Plan)', 'Cell ID', 'Site ID', 'Distance', 'Azi', 'Grade']
        df4 = df3[selected_columns]

        # Define a list to store the NBR relations
        nbr_relations = []

        # Iterate through the DataFrame rows
        for index, row in df.iterrows():
            lat_a, lon_a = float(row['Lat(in decimal)']), float(row['Long(in decimal)'])
            azimuth_a = float(row['AZIMUTH'])

            for _, neighbor_row in df.iterrows():
                lat_b, lon_b = float(neighbor_row['Lat(in decimal)']), float(neighbor_row['Long(in decimal)'])

                # Calculate the distance between cell A and cell B
                distance = 108 * (math.sqrt((lon_a - lon_b) ** 2 + (lat_a - lat_b) ** 2))

                # Calculate the azimuth difference between cell A and cell B
                azimuth_diff = abs(azimuth_a - neighbor_row['AZIMUTH'])

                Grade = abs(distance * azimuth_diff)

                # Check if cell B is a neighbor of cell A based on your criteria
                # You can adjust the criteria as needed
                if distance < 10 and azimuth_diff < 30:
                    # Append the NBR relation as a dictionary
                    nbr_relations.append({
                        'Cell A ID': row['Cell ID'],
                        'Cell B ID': neighbor_row['Cell ID'],
                        'Distance': distance,
                        'Azimuth Difference': azimuth_diff,
                        'Grade': Grade
                    })

        # Convert the list of NBR relations to a DataFrame
        nbr_relations_df = pd.DataFrame(nbr_relations)

        # Provide the option to download the NBR relations with the same name as the input file
        nbr_filename = os.path.join(output_folder, f"{remove_extension(uploaded_filename)}_NBR_Relations.xlsx")
        nbr_relations_df.to_excel(nbr_filename, index=False)

        # Convert the NBR relations DataFrame to an HTML table
        nbr_download_link = "/download_nbr_relations"
        nbr_content = nbr_relations_df.to_html(classes='table table-striped', escape=False)

        # Render the NBR template with the NBR content
        return render_template('nbr_relations.html', nbr_content=nbr_content, nbr_download_link=f"/download_nbr_relations?file={remove_extension(uploaded_filename)}")
    else:
        return "Upload a file first"

@nbr_app.route('/download_nbr_relations')
def download_nbr_relations():
    try:
        filename = request.args.get('file')
        if filename:
            # Provide the option to download the NBR relations Excel file with the same name as the input file
            nbr_filename = os.path.join(output_folder, f"{filename}_NBR_Relations.xlsx")
            return send_file(nbr_filename, as_attachment=True)
        else:
            return "File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@nbr_app.route('/list_files')
def list_files():
    input_files = os.listdir(input_folder)
    file_info = []

    for filename in input_files:
        base_name = remove_extension(filename)
        map_exists = os.path.exists(os.path.join(output_folder, f"{base_name}_map.html"))
        nbr_exists = os.path.exists(os.path.join(output_folder, f"{base_name}_NBR_Relations.xlsx"))
        
        file_info.append({
            'filename': filename,
            'map_exists': map_exists,
            'nbr_exists': nbr_exists,
        })

    return render_template('nbr_file_list.html', files=file_info, remove_extension=remove_extension)

# if __name__ == '__main__':
#     app.run(debug=False)
