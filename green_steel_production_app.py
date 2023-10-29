import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
import plotly.express as px
import pandas as pd

# Define the function for steel production cost calculation
def calculate_steel_production_costs(
    base_other_costs, 
    base_hydrogen_units, 
    base_electricity_units, 
    base_carbon_units, 
    base_labour_units,
    hydrogen_prices,
    electricity_prices,
    carbon_prices,
    labour_prices, 
    fixed_production, 
    years, 
    raw_material_utilisation, 
    operational_labour_efficiency, 
    target_efficiency_hydrogen, 
    target_efficiency_electricity, 
    target_efficiency_carbon, 
    target_efficiency_labour, 
    traditional_price,
    target_tipping_year,
    ):
    
    # calculate base costs
    base_hydrogen_costs = base_hydrogen_units * hydrogen_prices[0]
    base_electricity_costs = base_electricity_units * electricity_prices[0]
    base_carbon_costs = base_carbon_units * carbon_prices[0]
    base_labour_costs = base_labour_units * labour_prices[0]
    
    # Initialize empty lists for projection
    other_costs_projection = [base_other_costs]
    hydrogen_costs_projection = [base_hydrogen_costs]
    electricity_costs_projection = [base_electricity_costs]
    carbon_costs_projection = [base_carbon_costs]
    labour_costs_projection = [base_labour_costs]

    # Initialize empty lists for aggregated projections
    total_costs = []
    cumulative_production = []
    costs_per_ton = []

    base_wasted_hydrogen_units = base_hydrogen_units * (1 - raw_material_utilisation)
    base_wasted_electricity_units = base_electricity_units * (1 - raw_material_utilisation)
    base_wasted_carbon_units = base_carbon_units * (1 - raw_material_utilisation)
    base_wasted_labour_units = base_labour_units * (1 - operational_labour_efficiency)

    # Initialize intersection year to None
    intersection_year = None

    for i in range(years):
        if i == 0:
            total_costs_calculated = (
                other_costs_projection[i]
                + hydrogen_costs_projection[i]
                + electricity_costs_projection[i]
                + carbon_costs_projection[i]
                + labour_costs_projection[i]
            )
            costs_per_ton_calculated = total_costs_calculated / fixed_production

            total_costs.append(total_costs_calculated)
            cumulative_production.append(fixed_production)
            costs_per_ton.append(costs_per_ton_calculated)

        else:
            wasted_hydrogen_units = base_wasted_hydrogen_units * (1 - target_efficiency_hydrogen) ** i
            hydrogen_savings_units = base_wasted_hydrogen_units - wasted_hydrogen_units
            hydrogen_units_calculated = base_hydrogen_units - hydrogen_savings_units
            hydrogen_costs_calculated = hydrogen_units_calculated * hydrogen_prices[i]
            hydrogen_costs_projection.append(hydrogen_costs_calculated)

            wasted_electricity_units = base_wasted_electricity_units * (1 - target_efficiency_electricity) ** i
            electricity_savings_units = base_wasted_electricity_units - wasted_electricity_units
            electricity_units_calculated = base_electricity_units - electricity_savings_units
            electricity_costs_calculated = electricity_units_calculated * electricity_prices[i]
            electricity_costs_projection.append(electricity_costs_calculated)

            wasted_carbon_units = base_wasted_carbon_units * (1 - target_efficiency_carbon) ** i
            carbon_savings_units = base_wasted_carbon_units - wasted_carbon_units
            carbon_units_calculated = base_carbon_units - carbon_savings_units
            carbon_costs_calculated = carbon_units_calculated * carbon_prices[i]
            carbon_costs_projection.append(carbon_costs_calculated)

            wasted_labour_units = base_wasted_labour_units * (1 - target_efficiency_labour) ** i
            labour_savings_units = base_wasted_labour_units - wasted_labour_units
            labour_units_calculated = base_labour_units - labour_savings_units
            labour_costs_calculated = labour_units_calculated * labour_prices[i]
            labour_costs_projection.append(labour_costs_calculated)

            total_costs_calculated = (
                base_other_costs
                + hydrogen_costs_projection[i]
                + electricity_costs_projection[i]
                + carbon_costs_projection[i]
                + labour_costs_projection[i]
            )
            costs_per_ton_calculated = total_costs_calculated / fixed_production

            total_costs.append(total_costs_calculated)
            cumulative_production.append(fixed_production)
            costs_per_ton.append(costs_per_ton_calculated)
            
            # Check for intersection with international price
            if costs_per_ton_calculated <= traditional_price and intersection_year is None:
                intersection_year = i - 1

    subsidy = costs_per_ton[target_tipping_year] - traditional_price
    


    #####
    # Matplotlib Code
    #####
    # Set the background color to black
    # Create a black background figure
    fig = plt.figure(facecolor='black')
    
    # Set the text color to white
    plt.rcParams['text.color'] = 'white'
    
    # Change the font to Garamond
    font = FontProperties(family='Garamond')
    
    plt.plot(range(years), [traditional_price] * years, linestyle='--', label='Traditional Price')
    plt.plot(range(years), costs_per_ton, label='Cost per Ton')
    plt.ylim(0, 1)  # Set the y-axis minimum to 0
    plt.xlabel('Years', fontproperties=font)
    plt.ylabel('Costs per Ton', fontproperties=font)
    plt.title(f'Cost per Ton of Steel Production Over Time (with target tipping point in year {target_tipping_year} and required subsidy)', fontproperties=font)
    
    # Set arrow color to white for all annotations
    arrow_props = dict(arrowstyle='->', color='white')
    
    plt.annotate(f'Required Subsidy: £{round(subsidy, 4)}/ton', xy=(target_tipping_year, costs_per_ton[target_tipping_year]), xytext=(target_tipping_year + 1, costs_per_ton[target_tipping_year] * 1.5), arrowprops=arrow_props)
    # only one line may be specified; ymin & ymax specified as a percentage of y-range
    plt.axvline(x=target_tipping_year, ymin=traditional_price, ymax=costs_per_ton[target_tipping_year], color='green', ls='--', label='subsidy')
    
    if intersection_year is not None:
        plt.annotate(f'Tipping Calendar Year: {intersection_year}', xy=(intersection_year, traditional_price), xytext=(intersection_year + 1, traditional_price * 1.5), arrowprops=arrow_props)
    
    plt.legend()
    
    # Set the background color of the plot to black
    fig.patch.set_facecolor('black')
    
    plt.show()  # Show the plot


# Streamlit UI
st.title("Steel Production Cost Calculator")

st.sidebar.header("Input Parameters")

base_other_costs = st.sidebar.number_input("Base Other Costs (£)", value=100)
base_hydrogen_units = st.sidebar.number_input("Base Hydrogen Units (kg)", value=20)
base_electricity_units = st.sidebar.number_input("Base Electricity Units (kWh)", value=10)
base_carbon_units = st.sidebar.number_input("Base Carbon Units (kg)", value=10)
base_labour_units = st.sidebar.number_input("Base Labour Units (hours)", value=5)
hydrogen_prices = st.sidebar.text_area("Hydrogen Prices (£/kg) separated by comma", "10,9,9,8,8,8,8,8,8,8")
hydrogen_prices = [float(price) for price in hydrogen_prices.split(",")]
electricity_prices = st.sidebar.text_area("Electricity Prices (£/kWh) separated by comma", "15,15,13,13,14,14,13,13,13,13")
electricity_prices = [float(price) for price in electricity_prices.split(",")]
carbon_prices = st.sidebar.text_area("Carbon Prices (£/kg) separated by comma", "7,8,8,8,9,9,9,9,9,9")
carbon_prices = [float(price) for price in carbon_prices.split(",")]
labour_prices = st.sidebar.text_area("Labour Prices (£/hour) separated by comma", "16,17,18,18,18,20,20,20,20,22")
labour_prices = [float(price) for price in labour_prices.split(",")]
fixed_production = st.sidebar.number_input("Fixed Production (tons)", value=1000)
years = st.sidebar.number_input("Number of Years", value=10)
raw_material_utilisation = st.sidebar.slider("Raw Material Utilisation (%)", 0.0, 1.0, 0.2)
operational_labour_efficiency = st.sidebar.slider("Operational Labour Efficiency (%)", 0.0, 1.0, 0.3)
target_efficiency_hydrogen = st.sidebar.slider("Target Efficiency Hydrogen (%)", 0.0, 1.0, 0.2)
target_efficiency_electricity = st.sidebar.slider("Target Efficiency Electricity (%)", 0.0, 1.0, 0.29)
target_efficiency_carbon = st.sidebar.slider("Target Efficiency Carbon (%)", 0.0, 1.0, 0.4)
target_efficiency_labour = st.sidebar.slider("Target Efficiency Labour (%)", 0.0, 1.0, 0.2)
traditional_price = st.sidebar.number_input("Traditional Price (£/ton)", value=0.3)
target_tipping_year = st.sidebar.number_input("Target Tipping Year", value=1)

st.sidebar.button("Calculate Steel Production Costs")

if base_hydrogen_units and base_electricity_units and base_carbon_units and base_labour_units and hydrogen_prices and electricity_prices and carbon_prices and labour_prices:
    parameters = {
        'base_other_costs': base_other_costs,
        'base_hydrogen_units': base_hydrogen_units,
        'base_electricity_units': base_electricity_units,
        'base_carbon_units': base_carbon_units,
        'base_labour_units': base_labour_units,
        'hydrogen_prices': hydrogen_prices,
        'electricity_prices': electricity_prices,
        'carbon_prices': carbon_prices,
        'labour_prices': labour_prices,
        'fixed_production': fixed_production,
        'years': years,
        'raw_material_utilisation': raw_material_utilisation,
        'operational_labour_efficiency': operational_labour_efficiency,
        'target_efficiency_hydrogen': target_efficiency_hydrogen,
        'target_efficiency_electricity': target_efficiency_electricity,
        'target_efficiency_carbon': target_efficiency_carbon,
        'target_efficiency_labour': target_efficiency_labour,
        'traditional_price': traditional_price,
        'target_tipping_year': target_tipping_year,
    }
    calculate_steel_production_costs(**parameters)
