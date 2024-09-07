import os
import pandas as pd
from openpyxl import load_workbook
import numpy as np
from datetime import datetime
import zipfile
from flask import Flask, render_template, request, send_file, Blueprint

app = Flask(__name__)
kpi_app = Blueprint('kpi_app', __name__, template_folder='templates')

# # Set Pandas option to use 'openpyxl' engine for reading Excel files
# pd.set_option('io.excel.zip.reader', 'openpyxl')

today = datetime.today()
today = today.strftime("%Y-%m-%d")
# print("Today: ",today)
output_file_path = r'./kpi_app/output'

class delete_file():
    def __init__(self):
        if os.path.exists(output_file_path):
            files = os.listdir(output_file_path)
            for file in files:
                file_path = os.path.join(output_file_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                else:
                    print(f"Skipping {file_path} as it is not a file.")
        else:
            print(f"The folder '{output_file_path}' does not exist.")

def extract_zip_files(folder_path):
    
    kpifiles = os.listdir(folder_path)
    for file in kpifiles:
        if file.endswith(".zip"):
            zip_file_path = os.path.join(folder_path, file)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(folder_path)
            os.remove(zip_file_path)

@kpi_app.route('/core_kpi')
def home():
    return render_template('kpi_index.html')


@kpi_app.route('/upload_kpi', methods=['GET', 'POST'])
def upload():
    global uploaded_data, uploaded_filename
    if 'file' in request.files:
        file = request.files['file']
        if file:
            uploaded_filename = file.filename
            file.save(os.path.join('kpi_app/kpifiles', uploaded_filename))
            # uploaded_data = pd.read_excel(os.path.join('kpifiles', uploaded_filename))
    return render_template('kpi_upload.html')


def file_count():
    folder_path = r'./kpi_app/kpifiles'
    extract_zip_files(folder_path)
    # Use os.listdir() to get a list of all files in the folder
    kpifiles = os.listdir(folder_path)
    
    # Filter out only valid files after unzipping
    kpifiles = [file for file in os.listdir(folder_path) if file.endswith((".xlsx", ".txt", ".csv"))]

    print(kpifiles, "\nTotal Files in Folder: ", len(kpifiles))

    # Set a list of extensions you want to count
    extensions = [".xlsx", ".txt", ".csv"]

    # Initialize a dictionary to store counts for each extension
    extension_counts = {ext: 0 for ext in extensions}

    # Iterate through the files and count those with extensions in the list
    for file in kpifiles:
        file_name, file_extension = os.path.splitext(file)
        if file_extension in extensions:
            extension_counts[file_extension] += 1

    # Print the counts for each extension
    for extension, count in extension_counts.items():
        print(f"Number of {extension} files in the folder: {count}")
    formula_file(kpifiles, folder_path)


def formula_file(kpifiles, folder_path):
    # taking input from input(safaricom_file)
    df = pd.read_excel(r'./kpi_app/sample.xlsx')
    # finding the total kpi count
    column_name = 'KPI ID'
    total_kpi = len(df[column_name]) - 1
    print("Total_KPI:", total_kpi)
    # creating an list with kpi_ID
    kpi_ID = df['KPI ID'].dropna().tolist()
    # print(kpi_ID,"\n",len(kpi_ID))
    # df['Primary_Key3'] = df['Primary_Key3'].fillna(np.nan)
    for i in kpi_ID:
        print("KPI ID:", i)
        condition = df['KPI ID'] == i
        if condition.any():  # Check if any row meets the condition
            selected_row = df.loc[condition].iloc[0]  # Select the first row that meets the condition
            # print("Selected Row:",selected_row)
            #Selecting the Columns
            Kpi_name = selected_row['KPI Name']
            file_Identifire1 = selected_row['File Identifire']
            file_Identifire2 = selected_row['Node_Name']
            sheet_name = selected_row["Sheet_name"]
            action = selected_row["Action"]
            id = selected_row['KPI ID']
            primary_key3 = selected_row['Primary_Key3']
            unit_value = selected_row['Unit']
            if action == 'N':
                # print("In Nom Funtion")
                kpi_formula = selected_row['Nom']
                kpi_formula = kpi_formula.replace("(", "").replace(")", "").replace("SUM", "").replace(" ", "").replace(
                    "\n", "").split("+")
                # Convert all strings to uppercase using list comprehension
                uppercase_formula = [item.upper() for item in kpi_formula]
                # print("Sheet Name: ", sheet_name)
                # print(f"kpi formula: {uppercase_formula}")
                # print(f"Specific value based on condition: {file_Identifire}")
                print("File Identifier1: ", file_Identifire1, "\nFile Identifier2: ", file_Identifire2)
                for file in kpifiles:
                    # print("Files: ", file)
                    # Check if the file contains the identifier
                    if file_Identifire1 in file and file_Identifire2 in file:
                        file_path = os.path.join(folder_path, file)
                        print("File_Reading.. ", file_path)
                        Nom(file_path, sheet_name, uppercase_formula, Kpi_name,id,unit_value,primary_key3)
                # Print the updated list
                # print(uppercase_formula)
            elif action == 'D':
                # print("In Denom Function")
                kpi_formula1 = selected_row['Nom']
                kpi_formula1 = kpi_formula1.replace("(", "").replace(")", "").replace("SUM", "").replace(" ", "").replace(
                    "\n", "").split("+")
                # Convert all strings to uppercase using list comprehension
                uppercase_formula1 = [item.upper() for item in kpi_formula1]
                # print("Sheet Name: ", sheet_name)
                # print(f"kpi formula: {uppercase_formula1}")
                kpi_formula2 = selected_row['Denom']
                kpi_formula2 = kpi_formula2.replace("(", "").replace(")", "").replace("SUM", "").replace(" ",
                                                                                                        "").replace(
                    "\n", "").split("+")
                # Convert all strings to uppercase using list comprehension
                uppercase_formula2 = [item.upper() for item in kpi_formula2]
                # print("Sheet Name: ", sheet_name)
                # print(f"kpi formula: {uppercase_formula2}")
                # print(f"Specific value based on condition: {file_Identifire}")
                print("File Identifier1: ", file_Identifire1, "\nFile Identifier2: ", file_Identifire2)
                for file in kpifiles:
                    # print("Files: ", file)
                    # Check if the file contains the identifier
                    if file_Identifire1 in file and file_Identifire2 in file:
                        file_path = os.path.join(folder_path, file)
                        print("File_Reading... ", file_path)
                        Denom(file_path, sheet_name, uppercase_formula1, uppercase_formula2, Kpi_name,id,unit_value,primary_key3)
                # Print the updated list
                # print(uppercase_formula)
        else:
            print("No rows meet the condition.")


def Nom(file, sheet, formula_list, kpi_name, id, unit, key):
    df = pd.read_excel(file,sheet_name=sheet)
    # Split column names by space and extract the first part
    # Find the name of the 2nd column (column at index 1)
    # second_column_name = df.columns[1]
    df.columns = df.columns.str.split().str.get(0)
    second_column_name = df.columns[1]
    # print("Column_name: ",df.columns)
    # print("Formula_list: ",formula_list)
    set1 = set(df.columns)
    set2 = set(formula_list)
    # Find the values that are in both sets
    common_values = set1.intersection(set2)
    # Create a new list with the common values
    result_list = list(common_values)
    # print("Result:",result_list)
    # Print the updated column names
    # print(df.to_string())
    # print("Forluma_list: ", formula_list)
    file_name = kpi_name
    df[kpi_name] = 0.0
    row_to_clear = 0
    # Clear the contents in the specified row for all columns
    df.iloc[row_to_clear] = np.nan
    # Iterate through the formula list and sum matching columns
    for formula in result_list:
        try:
            df[kpi_name] += df[formula]
        except KeyError:
            print(f"Column '{formula}' not found, skipping...")
    # Convert 'Date' column to string data type
    df['Period'] = df['Period'].astype(str)
    df[['Period', 'Hour']] = df['Period'].str.split(' ', expand=True)
    ##selecting the specific columns
    df = df[['Period','Hour',second_column_name,kpi_name]]
    df['Kpi_Name'] = str(kpi_name)
    df['Kpi_Id'] = str(id)
    ##skiping 2nd row
    row_label_to_delete = 0  # This corresponds to the second row
    df = df.drop(df.index[row_label_to_delete])
    # Reset the index to maintain consecutive numbering
    df.reset_index(drop=True, inplace=True)
    df.rename(columns={'Period':'Date',second_column_name:second_column_name+"_Name"},inplace=True)
    ##setting out the column orders
    column_order = ['Date','Hour','Kpi_Name','Kpi_Id',second_column_name+"_Name",kpi_name]
    df = df[column_order]
    df.to_excel(output_file_path+"\\"+kpi_name+"_"+today+".xlsx", index=False)
    ###from here code calculating pivot table and appending
    existing_file = output_file_path+"\\"+kpi_name+"_"+today+".xlsx"
    # Create a sample DataFrame
    df = pd.read_excel(existing_file, index_col=False)
    # Define the values you want to append for specific columns

    # Calculate the sum of 'Value' based on unique values in 'Category'
    sum_by_kpi = df.groupby(second_column_name+"_Name")[kpi_name].sum().reset_index()
    sum_by_date = df.groupby('Date')[kpi_name].sum().reset_index()
    sum_by_hour = df.groupby('Hour')[kpi_name].sum().reset_index()
    # sum_by_date = sum_by_date.rename(columns={'HO Attempts': 'PLMN'})
    # print(sum_by_kpi, "\n", sum_by_date)
    df = pd.concat([df, sum_by_kpi, sum_by_date,sum_by_hour], ignore_index=True)
    # Define the columns you want to fill
    columns_to_fill = ['Date', 'Hour', 'Kpi_Name', 'Kpi_Id', second_column_name+"_Name"]
    # Define the values to fill missing values with
    fill_values = {'Date': today, 'Hour': '24:00:00', 'Kpi_Name': kpi_name, 'Kpi_Id': id, second_column_name+"_Name": 'PLMN'}
    # Use the fillna method to fill missing values in specific columns
    df[columns_to_fill] = df[columns_to_fill].fillna(fill_values)
    df.rename(columns={kpi_name:'Final'},inplace=True)
    df['Unit'] = unit
    # print("Second Column: ",df[second_column_name+'_Name'])
    # primary = pd.read_excel(r'E:\sample.xlsx')
    df['Element_Id'] = key
    df['Element_Id'] = df['Element_Id'].fillna(df[second_column_name+'_Name'])
    df.to_excel(existing_file, index=False)
    # print("Data from source files appended to the last row of the existing file.")


def Denom(file, sheet, formulalist1, formulalist2, kpi_name,id,unit,key):
    df = pd.read_excel(file, sheet_name=sheet)
    # Split column names by space and extract the first part
    df.columns = df.columns.str.split().str.get(0)
    second_column_name = df.columns[1]
    # Print the updated column names
    # print(df.columns)
    # print("Columns_list: ", df.columns)
    # print("Formula_list1: ",formulalist1)
    # print("Formula_list2: ",formulalist2)
    set1 = set(df.columns)
    set2 = set(formulalist1)
    set3 = set(formulalist2)
    # Find the values that are in both sets
    common_values1 = set1.intersection(set2)
    # Create a new list with the common values
    result_list1 = list(common_values1)
    # Find the values that are in both sets
    common_values2 = set1.intersection(set3)
    # Create a new list with the common values
    result_list2 = list(common_values2)
    # print("Result1: ",result_list1)
    # print("Result2: ",result_list2)
    # Define the row you want to clear (e.g., the second row)
    row_to_clear = 0
    # Clear the contents in the specified row for all columns
    df.iloc[row_to_clear] = np.nan
    df['Nom'] = 0.0
    df['Denom'] = 0.0
    row_to_clear = 0
    # Clear the contents in the specified row for all columns
    df.iloc[row_to_clear] = np.nan
    # Iterate through the formula list and sum matching columns
    for formula in result_list1:
        try:
            df['Nom'] += df[formula].astype(float)
        except KeyError:
            print(f"Column '{formula}' not found, skipping...")
        # if formula in df.columns:
        #     df['Nom'] = df['Nom'].astype(float) + df[formula].astype(float)
    for formula in result_list2:
        try:
            df['Denom'] += df[formula].astype(float)
        except KeyError:
            print(f"Column '{formula}' not found, skipping...")
        # if formula in df.columns:
        #     df['Denom'] = df['Denom'].astype(float) + df[formula].astype(float)
    df['Numerator'] = df['Nom']
    df['Denominator'] = df['Denom']
    df[kpi_name] = df['Nom'] / df['Denom']
    # Multiply all values by 100 and add the percentage sign
    df[kpi_name] = (df[kpi_name] * 100).apply(lambda x: f'{x:.2f}')
    # Convert 'Date' column to string data type
    df['Period'] = df['Period'].astype(str)
    df[['Period', 'Hour']] = df['Period'].str.split(' ', expand=True)
    df = df[['Period', 'Hour', second_column_name,'Numerator','Denominator', kpi_name]]
    df['Kpi_Name'] = str(kpi_name)
    df['Kpi_Id'] = str(id)
    ##skiping 2nd row
    row_label_to_delete = 0  # This corresponds to the second row
    df = df.drop(df.index[row_label_to_delete])
    # Reset the index to maintain consecutive numbering
    df.reset_index(drop=True, inplace=True)
    df.rename(columns={'Period': 'Date', second_column_name: second_column_name+'_Name'}, inplace=True)
    ##setting out the column orders
    column_order = ['Date', 'Hour', 'Kpi_Name', 'Kpi_Id', second_column_name+'_Name','Numerator','Denominator', kpi_name]
    df = df[column_order]
    df.to_excel(output_file_path + "\\" + kpi_name +"_"+today+".xlsx", index=False)
    ###from here code calculating pivot table and appending
    existing_file = output_file_path + "\\" + kpi_name +"_"+today+".xlsx"
    # Create a sample DataFrame
    df = pd.read_excel(existing_file, index_col=False)
    # Calculate the sum of 'Value' based on unique values in 'Category'
    sum_by_kpi = df.groupby(second_column_name+'_Name')[['Numerator', 'Denominator']].sum().reset_index()
    sum_by_date = df.groupby('Date')[['Numerator', 'Denominator']].sum().reset_index()
    sum_by_hour = df.groupby('Hour')[['Numerator', 'Denominator']].sum().reset_index()
    # sum_by_date = sum_by_date.rename(columns={'HO Attempts': 'PLMN'})
    # print(sum_by_kpi, "\n", sum_by_date)
    df = pd.concat([df, sum_by_kpi, sum_by_date, sum_by_hour], ignore_index=True)
    # Define the columns you want to fill
    columns_to_fill = ['Date', 'Hour', 'Kpi_Name', 'Kpi_Id', second_column_name+'_Name']
    # Define the values to fill missing values with
    fill_values = {'Date': today, 'Hour': '24:00:00', 'Kpi_Name': kpi_name, 'Kpi_Id': id, second_column_name+'_Name': 'PLMN'}
    # Use the fillna method to fill missing values in specific columns
    df[columns_to_fill] = df[columns_to_fill].fillna(fill_values)
    df.rename(columns={kpi_name:'Final'},inplace=True)
    df['Unit'] = unit
    # print("Second Column: ",df[second_column_name+'_Name'])
    # primary = pd.read_excel(r'E:\sample.xlsx')
    df['Element_Id'] = key
    df['Element_Id'] = df['Element_Id'].fillna(df[second_column_name + '_Name'])
    df.to_excel(existing_file, index=False)
    # print("Data from source files appended to the last row of the existing file.")

def combine_file():
    i = 0
    directory = r'./kpi_app/combine_file\\'
    combined_data = pd.DataFrame()
    for filename in os.listdir(output_file_path):
        if filename.endswith(".xlsx"):  # Ensure you're processing only Excel files
            file_path = os.path.join(output_file_path, filename)
            data = pd.read_excel(file_path)
            combined_data = combined_data._append(data, ignore_index=True)
            i+=1
    column_order = ['Date', 'Hour', 'Kpi_Name', 'Kpi_Id', 'MSC_Name','Element_Id','Numerator', 'Denominator', 'Final','Unit']
    combined_data = combined_data[column_order]
    combined_data.to_excel(directory+'Core_KPIs.xlsx', index=False)
    print("{} files has been combined.".format(i))
    return combined_data  # Return the combined data

@kpi_app.route('/process_files', methods=['GET', 'POST'])
def process_files():
    dl = delete_file()
    file_count()
    combined_data = combine_file()
    # Render the HTML template and pass the combined data to it
    return render_template('kpi_display_data.html', combined_data=combined_data)

@kpi_app.route('/download_combined_file')
def download_combined_file():
    combined_file_path = './kpi_app/combine_file/Core_KPIs.xlsx'  # Path to the combined data file
    return send_file(combined_file_path, as_attachment=True)

@kpi_app.route('/list_files_kpi')
def list_files():
    output_folder = './kpi_app/output'
    files = os.listdir(output_folder)
    file_list = []

    for file in files:
        file_path = os.path.join(output_folder, file)
        if os.path.isfile(file_path):
            file_list.append(file)

    return render_template('kpi_list_files.html', files=file_list)

@kpi_app.route('/download_file/<filename>')
def download_file(filename):
    output_folder = './output'
    file_path = os.path.join(output_folder, filename)

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found"

# if __name__ == '__main__':
#     dl = delete_file()
#     file_count()
#     combine_file()

# if __name__ == '__main__':
#     app.run(debug=False)