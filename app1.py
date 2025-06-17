import streamlit as st
import pandas as pd

# Power ratings dictionary
power_ratings = {
    "Tube Light": [20, 40, 60],
    "Fan": [50, 75, 90],
    "Electric Bell": [10],
    "Fridge": [150, 250, 400],
    "AC": [1000, 1500, 2000],
    "Washing Machine": [500, 1000],
    "LED Light": [5, 9, 12],
    "Electric Stove": [1000, 1500],
    "Electric Heater/Geyser": [1500, 2000],
    "Iron Box": [1000, 1500],
    "Others": []
}

st.title("Household Energy Consumption Estimator")

appliances = []
num_appliances = []
selected_powers = []
usage_hours = []

st.subheader("Enter Appliance Details")
for appliance, ratings in power_ratings.items():
    with st.expander(appliance):
        count = st.number_input(f"Number of {appliance}(s)", min_value=0, step=1)
        if ratings:
            power = st.radio(f"Select Power Rating for {appliance} (W)", ratings, index=0)
        else:
            power = st.number_input(f"Enter Custom Power Rating for {appliance} (W)", min_value=0)
        hours = st.number_input(f"Usage per Day for {appliance} (hours)", min_value=0.0, step=0.5)

        appliances.append(appliance)
        num_appliances.append(count)
        selected_powers.append(power)
        usage_hours.append(hours)

solar_share = st.slider("Solar Share (%)", 0, 100, 0)

# Calculation
total_energy = sum([(p * h * n) / 1000 for p, h, n in zip(selected_powers, usage_hours, num_appliances)])
cost = total_energy * 7.4
co2_emission = total_energy * 0.82
renewable_kwh = total_energy * (solar_share / 100)
co2_saved = renewable_kwh * 0.82
carbon_credits = co2_saved * 0.15

# Display Results
st.write(f"### Total Energy Consumed: {total_energy:.2f} kWh/day")
st.write(f"### Total Cost: ₹{cost:.2f}/day")
st.write(f"### Total CO₂ Emission: {co2_emission:.2f} kg/day")
st.write(f"### CO₂ Saved: {co2_saved:.2f} kg/day")
st.write(f"### Carbon Credits Earned: ₹{carbon_credits:.2f}/day")
