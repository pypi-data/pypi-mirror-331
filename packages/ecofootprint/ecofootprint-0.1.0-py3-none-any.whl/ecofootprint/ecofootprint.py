"""
ecofootprint.py

A module to calculate and analyze your carbon footprint from daily activities.
It provides functions to estimate CO2 emissions from transportation,
electricity consumption, and food intake, as well as suggestions for reducing your footprint.
"""

def carbon_footprint_transportation(distance_km, vehicle_type='gasoline'):
    """
    Estimate carbon emissions for transportation.
    
    Args:
        distance_km (float): Distance traveled in kilometers.
        vehicle_type (str): Vehicle type ('gasoline', 'diesel', 'electric').
            Approximate emission rates:
              - gasoline: ~0.24 kg CO2/km
              - diesel: ~0.27 kg CO2/km
              - electric: ~0.05 kg CO2/km (varies with power source)
    
    Returns:
        float: Estimated CO2 emissions in kilograms.
    """
    rates = {
        'gasoline': 0.24,
        'diesel': 0.27,
        'electric': 0.05
    }
    rate = rates.get(vehicle_type.lower(), 0.24)
    return distance_km * rate

def carbon_footprint_electricity(kwh, region='global'):
    """
    Estimate carbon emissions from electricity usage.
    
    Args:
        kwh (float): Electricity consumed in kilowatt-hours.
        region (str): Region to adjust emission factor (e.g., 'usa', 'eu').
            Defaults to global average (~0.475 kg CO2/kWh).
    
    Returns:
        float: Estimated CO2 emissions in kilograms.
    """
    factors = {
        'global': 0.475,
        'usa': 0.453,
        'eu': 0.300
    }
    emission_factor = factors.get(region.lower(), 0.475)
    return kwh * emission_factor

def carbon_footprint_food(food_type, amount_kg):
    """
    Estimate carbon emissions based on food consumption.
    
    Args:
        food_type (str): Type of food ('beef', 'chicken', 'vegetarian').
            Approximate factors (kg CO2 per kg of food):
              - beef: ~27.0
              - chicken: ~6.9
              - vegetarian: ~2.0
        amount_kg (float): Amount of food in kilograms.
    
    Returns:
        float: Estimated CO2 emissions in kilograms.
    """
    factors = {
        'beef': 27.0,
        'chicken': 6.9,
        'vegetarian': 2.0
    }
    factor = factors.get(food_type.lower(), 2.0)
    return amount_kg * factor

def total_carbon_footprint(transport_km=0, vehicle_type='gasoline', electricity_kwh=0, region='global', food_data=None):
    """
    Aggregate carbon emissions from multiple sources.
    
    Args:
        transport_km (float): Total distance traveled (km).
        vehicle_type (str): Vehicle type for transportation.
        electricity_kwh (float): Total electricity consumption (kWh).
        region (str): Region for electricity emission factor.
        food_data (list of tuples): Each tuple in the form (food_type, amount_kg).
    
    Returns:
        float: Total estimated CO2 emissions in kilograms.
    """
    total = 0
    total += carbon_footprint_transportation(transport_km, vehicle_type)
    total += carbon_footprint_electricity(electricity_kwh, region)
    if food_data:
        for food_type, amount in food_data:
            total += carbon_footprint_food(food_type, amount)
    return total

def suggestions(total_emission):
    """
    Provide suggestions based on the total carbon footprint.
    
    Args:
        total_emission (float): Total CO2 emissions in kilograms.
    
    Returns:
        str: Recommendation message.
    """
    if total_emission < 100:
        return "Your carbon footprint is low. Keep up the sustainable practices!"
    elif total_emission < 500:
        return "Consider reducing your transportation emissions and switching to renewable energy."
    else:
        return "High carbon footprint detected. Consider significant lifestyle changes like using public transport, reducing meat consumption, and opting for renewable energy."

class EcoFootprintCalculator:
    """
    A class to aggregate and analyze your personal carbon footprint.
    """
    def __init__(self):
        self.transport_km = 0
        self.vehicle_type = 'gasoline'
        self.electricity_kwh = 0
        self.region = 'global'
        self.food_data = []

    def add_transport(self, km, vehicle_type='gasoline'):
        self.transport_km += km
        self.vehicle_type = vehicle_type

    def add_electricity(self, kwh, region='global'):
        self.electricity_kwh += kwh
        self.region = region

    def add_food(self, food_type, amount_kg):
        self.food_data.append((food_type, amount_kg))

    def calculate_total(self):
        return total_carbon_footprint(
            transport_km=self.transport_km,
            vehicle_type=self.vehicle_type,
            electricity_kwh=self.electricity_kwh,
            region=self.region,
            food_data=self.food_data
        )

    def get_suggestions(self):
        return suggestions(self.calculate_total())
