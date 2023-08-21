# -*- coding: utf-8 -*-
"""
Created on Mon Aug 21 14:52:23 2023

@author: cfcpc2
"""

from collections import defaultdict
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


#%% Sankey Plot
def Plot(sheet_name, label, source, target, value):
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 30,
          thickness = 20,
          line = None, # dict(color = "black", width = 0.5),
          label = label,
          color = None # "blue"
        ),
        link = dict(
          source = source, # indices correspond to labels, eg A1, A2, A1, B1, ...
          target = target,
          value = value
      ))])

    fig.update_layout(title_text=sheet_name, font_size=10)
    fig.show()

#%%
def Data_Generate(Dict):
    
    Dict_out = {}  # Initialize the output dictionary
    for sheet_name in Dict.keys():

        df=Dict[sheet_name]


        df=df.drop([0])

        # Rename some columns 
        df.rename(columns={'Unnamed: 0': 'SECTOR','OTHER PRIMARY_x000d_\n':'OTHER PRIMARY'}, inplace=True) 
        # Remove space in column names and Sector names
        df.columns=df.columns.str.strip()
        df.SECTOR=df.SECTOR.str.strip()

        # Rename rows
        df.SECTOR.replace({'COKE PLANTS AND BLAST FURNACES_x000d_': 'COKE PLANTS AND BLAST FURNACES'}, inplace=True)

        # Reset index
        df=df.set_index('SECTOR')

        # Transpose df
        df=df.T

        # Fill NaN values
        df=df.fillna(np.nan)
        #df.fillna(0, inplace=True)

        # define the combinations
        Transformers=['REFINERIES', 'POWER PLANTS', 'SELF-PRODUCERS',
               'GAS PLANTS', 'CHARCOAL PLANTS', 'COKE PLANTS AND BLAST FURNACES',
               'DISTILLERIES', 'OTHER CENTERS']
        Primaries=['OIL','NATURAL GAS','COAL','HYDROENERGY','GEOTHERMAL','NUCLEAR','FIREWOOD','SUGARCANE AND PRODUCTS','OTHER PRIMARY']
        Secondaries=['ELECTRICITY','LPG','GASOLINE/ALCOHOL','KEROSENE/JET FUEL','DIESEL OIL','FUEL OIL','COKE','CHARCOAL','GASES','OTHER SECONDARY']
        Consumptions=['TRANSPORT','INDUSTRIAL','RESIDENTIAL','COMMERCIAL, SERVICES, PUBLIC','AGRICULTURE, FISHING AND MINING','CONSTRUCTION AND OTHERS']

        unique_combinations = []

        # here add secondary combination then type of consumption combination

        for i in Transformers:
            for j in Primaries:
                unique_combinations.append((j, i,abs(df[i][j])))

        for i in Transformers:
            for j in Secondaries:
                unique_combinations.append((i, j,abs(df[i][j])))

        #get the final consumption column     

        for i in Primaries+Secondaries:
                unique_combinations.append((i, i+'-FINAL CONSUMPTION',abs(df['FINAL CONSUMPTION'][i])))

        # the final consumption column - Usage column
        for i in Primaries+Secondaries:
            for j in Consumptions:
                unique_combinations.append((i+'-FINAL CONSUMPTION', j,abs(df['FINAL CONSUMPTION'][i])))
	        

        label=Transformers+Primaries+Secondaries+Consumptions+[i+'-FINAL CONSUMPTION' for i in Primaries+Secondaries]
        
        
        # Rename the sheet_name to contain only year. Sample: "1970 - Brazil"--> "1970"
        sheet_name_new = sheet_name.split(' - ')[0]
    
        _dict=Dict_out[sheet_name_new]={}
        _dict["source"]=[]
        _dict["target"]=[]
        _dict["value"]=[]
        _dict["label"]=label


        #Dict_out[sheet_name_new] = data  # Store the data in the dictionary
        for k in unique_combinations:
            _dict["source"].append(label.index(k[0]))
            _dict["target"].append(label.index(k[1]))
            _dict["value"].append(k[2])
           
    return Dict_out


#%% Generate

Dict=pd.read_excel("Brazil_Energy balance matrix.xlsx", sheet_name=None, skiprows=range(4), skipfooter=3)

Dict_out=Data_Generate(Dict)

#sheet_name="2021"
#label=Dict_out[sheet_name]["label"]
#source=Dict_out[sheet_name]["source"]
#target=Dict_out[sheet_name]["target"]
#value=Dict_out[sheet_name]["value"]



#Plot(sheet_name=sheet_name, label=label, source=source, target=target, value=value)



# Define a list to store the generated Plotly figures
all_figures = []

# Get the list of available years from Dict_out keys
key_options = list(Dict_out.keys())

# Create a multiselect widget to select years
selected_years = st.multiselect("Select years", options=key_options)

# Generate Plotly figures for selected years and store them in the all_figures list
for year in selected_years:
    fig = Plot(sheet_name=year, label=Dict_out[year]["label"], source=Dict_out[year]["source"], 
               target=Dict_out[year]["target"], value=Dict_out[year]["value"])
    all_figures.append(fig)

# Display all the stored figures using st.plotly_chart
for fig in all_figures:
    st.plotly_chart(fig)

