import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import pandas as pd
from streamlit import info as st_info

# Define the function for steel production cost calculation
def calculate_steel_production_costs(
    base_other_costs, 
    base_hydrogen_units, 
    base_electricity_units,
    base_ironore_units,
    base_carbon_units, 
    base_labour_units,
    hydrogen_prices,
    electricity_prices,
    ironore_prices,
    carbon_prices,
    labour_prices, 
    years, 
    raw_material_utilisation, 
    operational_labour_efficiency, 
    target_efficiency_hydrogen, 
    target_efficiency_electricity, 
    target_efficiency_ironore,
    target_efficiency_carbon, 
    target_efficiency_labour, 
    traditional_price,
    target_tipping_year,
    ):
    
    fixed_production = 1000
    # calculate base costs
    base_hydrogen_costs = base_hydrogen_units * hydrogen_prices[0]
    base_electricity_costs = base_electricity_units * electricity_prices[0]
    base_ironore_costs = base_ironore_units * ironore_prices[0]
    base_carbon_costs = base_carbon_units * carbon_prices[0]
    base_labour_costs = base_labour_units * labour_prices[0]
    
    # Initialize empty lists for projection
    other_costs_projection = [base_other_costs]
    hydrogen_costs_projection = [base_hydrogen_costs]
    electricity_costs_projection = [base_electricity_costs]
    ironore_costs_projection = [base_ironore_costs]
    carbon_costs_projection = [base_carbon_costs]
    labour_costs_projection = [base_labour_costs]

    # Initialize empty lists for aggregated projections
    total_costs = []
    cumulative_production = []
    costs_per_ton = []

    base_wasted_hydrogen_units = base_hydrogen_units * (1 - raw_material_utilisation)
    base_wasted_electricity_units = base_electricity_units * (1 - raw_material_utilisation)
    base_wasted_ironore_units = base_ironore_units * (1 - raw_material_utilisation)
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
                + ironore_costs_projection[i]
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

            wasted_ironore_units = base_wasted_ironore_units * (1 - target_efficiency_ironore) ** i
            ironore_savings_units = base_wasted_ironore_units - wasted_ironore_units
            ironore_units_calculated = base_ironore_units - ironore_savings_units
            ironore_costs_calculated = ironore_units_calculated * ironore_prices[i]
            ironore_costs_projection.append(ironore_costs_calculated)

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
                + ironore_costs_projection[i]
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
    plt.rcParams['axes.facecolor'] = 'black'
    # Set the text color to white
    plt.rcParams['text.color'] = 'white'
    
    plt.plot(range(years), [traditional_price] * years, linestyle='--', label='Traditional Price')
    plt.plot(range(years), costs_per_ton, label='Cost per Ton')
    min_value = min(costs_per_ton) - 0.1  # Subtract a small value for some padding
    max_value = max(costs_per_ton) + 0.1  # Add a small value for some padding
    plt.ylim(min_value, max_value)
    # plt.ylim(0, 1)  # Set the y-axis minimum to 0
    plt.xlabel('Years')
    plt.ylabel('Costs per Ton')
    plt.title(f'Cost per Ton of Steel Production Over Time (with target tipping point in year {target_tipping_year} and required subsidy)')
    
    # Set arrow color to white for all annotations
    arrow_props = dict(arrowstyle='->', color='white')
    
    plt.annotate(f'Required Subsidy: £{round(subsidy, 4)}/ton', xy=(target_tipping_year, costs_per_ton[target_tipping_year]), xytext=(target_tipping_year + 1, costs_per_ton[target_tipping_year] ), arrowprops=arrow_props)
    # only one line may be specified; ymin & ymax specified as a percentage of y-range
    plt.axvline(x=target_tipping_year, ymin=traditional_price, ymax=costs_per_ton[target_tipping_year - 1], color='green', ls='--', label='subsidy')
    
    if intersection_year is not None:
        plt.annotate(f'Tipping Calendar Year: {intersection_year}', xy=(intersection_year, traditional_price), xytext=(intersection_year + 1, traditional_price * 1.5), arrowprops=arrow_props)
    
    plt.legend()
    st.pyplot(plt)


# Streamlit UI
st.title("Green Steel Production Cost Calculator")

st.warning(
    """
    1) This is a quick version made in less than 48 hours, full debugging and development still needs to happen.

    2) Default data is populated with mock data. Default data can soon be actual averages observed.    
    """)


st.markdown(
    """
    *This is a simplified and interactive cost-competitivity model for green steel production. (**Note: Default data is populated with mock data**).*
    
    Enter your input parameters in the sidebar,
    and the dynamic chart will display the cost per ton of steel production over time and the required subsidy to meet competitive cost levels. 
    
    - [Model Overview](#model-overview)
    - [Use Cases & Limitations](#use-cases-and-limitations)
    - [Input Parameter Explanations](#input-parameter-explanations)

    --- 
    """
)

st.sidebar.header("**Input Parameters**")
st.sidebar.write(
    """
    These parameters are for toggling and the cost model chart will change dynamically.

    *For explanations of input parameters please find Section 3 below graph.*

    **Note:** The number of years in the model can only be as long as the length of each "exogenous price projection series".
    """
)

st.sidebar.markdown("&nbsp;")
st.sidebar.write("### **Waste Efficiency YoY Targets**")
target_efficiency_hydrogen = st.sidebar.slider("Target Efficiency Hydrogen (%)", 0.0, 1.0, 0.2)
target_efficiency_electricity = st.sidebar.slider("Target Efficiency Electricity (%)", 0.0, 1.0, 0.29)
target_efficiency_ironore = st.sidebar.slider("Target Efficiency Iron Ore (%)", 0.0, 1.0, 0.4)
target_efficiency_carbon = st.sidebar.slider("Target Efficiency Carbon (%)", 0.0, 1.0, 0.4)
target_efficiency_labour = st.sidebar.slider("Target Efficiency Labour (%)", 0.0, 1.0, 0.2)
# Add a gap above the "Base Year Values" title
st.sidebar.markdown("&nbsp;")
st.sidebar.write("### **Base Year Efficiency Values**")
raw_material_utilisation = st.sidebar.slider("Raw Material Utilisation (%)", 0.0, 1.0, 0.2)
operational_labour_efficiency = st.sidebar.slider("Operational Labour Efficiency (%)", 0.0, 1.0, 0.3)
st.sidebar.markdown("&nbsp;")
st.sidebar.write("### **Base Year Input Values**")
st.sidebar.write("These values are to produce 1 ton of Green Steel")
base_other_costs = st.sidebar.number_input("Base Other Costs (£)", value=100)
base_hydrogen_units = st.sidebar.number_input("Base Hydrogen Units (00's kg)", value=20)
base_electricity_units = st.sidebar.number_input("Base Electricity Units (kWh)", value=10)
base_ironore_units = st.sidebar.number_input("Base Iron Ore Units (00's kg)", value=5)
base_carbon_units = st.sidebar.number_input("Base Carbon Units (00's kg)", value=10)
base_labour_units = st.sidebar.number_input("Base Labour Units (hours)", value=5)
# Add a gap above the "Exogenous Price Projections" title
st.sidebar.markdown("&nbsp;")
st.sidebar.write("### **Exogenous Price Projections**")
hydrogen_prices = st.sidebar.text_area("Hydrogen Prices (£/kg) separated by comma", "10,9,9,8,8,8,8,8,8,8")
hydrogen_prices = [float(price) for price in hydrogen_prices.split(",")]
electricity_prices = st.sidebar.text_area("Electricity Prices (£/kWh) separated by comma", "15,15,13,13,14,14,13,13,13,13")
electricity_prices = [float(price) for price in electricity_prices.split(",")]
ironore_prices = st.sidebar.text_area("Iron Ore Prices (£/kg) separated by comma", "4,4,5,5,6,4,3,4,3,3")
ironore_prices = [float(price) for price in ironore_prices.split(",")]
carbon_prices = st.sidebar.text_area("Carbon Prices (£/kg) separated by comma", "7,8,8,8,9,9,9,9,9,9")
carbon_prices = [float(price) for price in carbon_prices.split(",")]
labour_prices = st.sidebar.text_area("Labour Prices (£/hour) separated by comma", "16,17,18,18,18,20,20,20,20,22")
labour_prices = [float(price) for price in labour_prices.split(",")]
st.sidebar.markdown("&nbsp;")
st.sidebar.write("### **Model Calibration**")
years = st.sidebar.number_input("Number of Years", value=10)
traditional_price = st.sidebar.number_input("Traditional Price (£/ton)", value=0.3)
target_tipping_year = st.sidebar.number_input("Target Tipping Year", value=1)

st.sidebar.button("Calculate Steel Production Costs")

if base_hydrogen_units and base_electricity_units and base_carbon_units and base_labour_units and hydrogen_prices and electricity_prices and carbon_prices and labour_prices:
    parameters = {
        'base_other_costs': base_other_costs,
        'base_hydrogen_units': base_hydrogen_units,
        'base_electricity_units': base_electricity_units,
        'base_ironore_units': base_ironore_units,
        'base_carbon_units': base_carbon_units,
        'base_labour_units': base_labour_units,
        'hydrogen_prices': hydrogen_prices,
        'electricity_prices': electricity_prices,
        'ironore_prices': ironore_prices,
        'carbon_prices': carbon_prices,
        'labour_prices': labour_prices,
        'years': years,
        'raw_material_utilisation': raw_material_utilisation,
        'operational_labour_efficiency': operational_labour_efficiency,
        'target_efficiency_hydrogen': target_efficiency_hydrogen,
        'target_efficiency_electricity': target_efficiency_electricity,
        'target_efficiency_ironore': target_efficiency_ironore,
        'target_efficiency_carbon': target_efficiency_carbon,
        'target_efficiency_labour': target_efficiency_labour,
        'traditional_price': traditional_price,
        'target_tipping_year': target_tipping_year,
    }
    calculate_steel_production_costs(**parameters)

    st.write("This is a Steel Production Cost Calculator. Enter your input parameters in the sidebar, and the app will calculate and display the cost per ton of steel production over time.")

    st.markdown(
        """
        ## Model Overview
        **Purpose**: 
        
        This is a simplified model to assist the conception of a mental model and guide scenario analysis to understand the compeitivity of a green steel industry 
        (e.g by changing the input price projections in the sidebar).

        **Model Framework**: 
        
        Economies of scale is essentially *'cheaper costs per unit of output produced'*.
        Production can be viewed as a function of labour and capital. Technology and learning-by-doing can increase efficiency of production.
        Efficiency is defined as the reduction of **'wasted resource-units'**

        Wasted resource-units are defined as the difference between the current units required for production and the optimum amount of units required for production.
        The reason why an efficiency rate should not be applied to the aggregate amount of units for each production input, 
        is because not all of the input units stock can be diminished.
        
        *An example can illustrate this:*
        
        Initially a labour, in period one, utilises capital inefficiently due to lack of experience using the technology. 
        This lowers the physical capital utilisation rate during the period.
        After each period, their efficieny improves with diminishing returns. 
        Note that efficiency isn't applied across the 'work' but should be viewed as shortening the 'wasted labour resource-units',
        with 'wasted labour resource-units' defined as the difference between current labour units required and the optimum amount.

        There is a starting value for the **resource-units** (defined as 'base year efficiency value').
        There is an efficiency rate that is either targetted by management or organically materialised - diminishing all wasted **resource-units** (defined as 'Waste Efficiency YoY Targets').
        The costs of inputs is calculated as the multiplication of the resource-units and their respective prices in that period (defined as 'Exogenous Price Projections').


        
        ## Use Cases & Limitations
        *Inputting the price projections allows for preliminary scenario planning.*

        **Use Cases**
        
        The helps answer the following questions:

        - *Which key drivers have the most contribution to achieving economies of scale?*
        
        - *When does green steel become cost competitive?*
        
        - *How much would the government need to subsidise in a target year, if technology wasn't yet cost competitive?*
        
        - *How does the cost curve change given different sets of hydrogen and electricity prices*

        - *Given the base value of efficiencies for different resource inputs, what efficiency rates (for diminishing wasted resource-units) should be targetted?*


        ## Input Parameter Explanations
        Detailed explanations of input parameters.

        - **Base Year Input Values**
        *Each Input is the amount required per ton of steel in the base year.*
            
            - Base Other Costs
            Definition: These are the fixed costs of production 
            Assumption: These fixed costs don't have wasted resources that can be diminished.
            Limitation: There can be efficiencies, eg take space efficiency of manufacture, which would make land more efficiently used.

            - Base Hydrogen Units
            Definition: This is the required amount of hydrogen needed to be produced for steel in the base year.
            Assumption: Perhaps the handling of hydrogen and the technology doesn't allow for all hydrogen to be used.        

            - Base Electricity Units
            Definition: This is the required amount of electricity needed to be produced for steel in the base year.
            Assumption: Perhaps the handling of electricity and the technology doesn't allow for all electricity to be used.
        
            - Base Carbon Units
            Definition: This is the required amount of carbon needed to be produced for steel in the base year.
            Assumption: Perhaps the handling of carbon and the technology doesn't allow for all carbon to be used.
        
            - Base Labour Units
            Definition: This is the required amount of labour needed to be produced for steel in the base year.
            Assumption: Given the new technology, perhaps labour on average is still inexperienced, meaning that there is wasted labour resource-units being spent for instance 'figuring out what to do'.
        
        - **Base Year Efficiency Values**
        *This set of input parameters defines how efficiently the the inputs of production are initially used. 
        Consequently, this defines the amount of wasted resource-units in each production period that needs to be diminished, achieving economies of scale.
        Wasted resource-units converge to zero with target YoY efficiency gains form 'Waste Efficiency YoY Targets'*.
            
            - Raw Material Utilisation
            Definition: How much the raw materials are being used going into the production process. 
            This can be thought of as the mass of the physical inputs divided by the mass of the output.
            This metric applies to hydrogen, electricity, carbon and iron ore.
            Assumption: Efficiency gains are homogenous across the raw material input set.
            Limitation: Efficiency gains are definitely not homogenous across the raw material input set, but this assumption was made for version 1 of this simple model.
        
            - Operational Labour Efficiency
            Definition: This parameter is defined as the relationship between 'the average labour units required for producing a ton of steel in the base year' 
            and the optimum amount of labour units required. 

        - **Waste Efficiency YoY Targets**
        *These parameters define the rate at which the wasted resource-units diminish over time.*
            
            - Target Efficiency Hydrogen
            Definition: This is the YoY rate that wasted hydrogen diminishes.

            - Target Efficiency Electricity
            Definition: This is the YoY rate that wasted electricity diminishes.

            - Target Efficiency Carbon
            Definition: This is the YoY rate that wasted carbon diminishes.

            - Target Efficiency Labour
            Definition: This is the YoY rate that wasted labour diminishes.

        - **Exogenous Price Projections**
        *Each price series can be changed to conduct scenario analysis.
        Note that each series has to be the same length of the number of years calibrated by the model.*
            
            - Hydrogen Prices
            Definition: The price movements of hydrogen

            - Electricity Prices
            Definition: The price movements of electricity.

            - Carbon Prices
            Definition: The price movements of carbon.

            - Labour Prices
            Definition: The price movements of average wages.

        - **Model Calibration**
        *This sets the projection of the model, the traditional price benchmark (that defines cost competitivity), 
        and the target tipping year (which defines the required government subsidy to support the targeted cost competitivity)

            - Number of Years
            Definition: The number of years for the projection. This must be the same or less than each of the lengths of the exogenous price projection series.

            - Tradition Price
            Definition: This defines the cost competitivity benchmark. This can be the international price of Steel or that which is produced by the country.
            Assumption: This model assumes that steel producers are price takers not price setters, and that the international steel price doesn't move.
            Limitation: This is a very broad assumption used for model simplification in version 1.
        
        """
    )
