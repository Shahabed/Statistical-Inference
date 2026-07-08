# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 15:27:41 2023

@author: Shahabedin Chatraee Azizabadi
"""

import pandas as pd
import numpy as np

def watemp(temperatures):
    # Define the area(sq^2) for each German state
    states_area = [
        ('Baden-Württemberg', 35751),
        ('Bavaria', 70550),
        ('Berlin', 891),
        ('Brandenburg', 29479),
        ('Bremen', 419),
        ('Hamburg', 755),
        ('Hesse', 21115),
        ('Mecklenburg-Vorpommern', 23180),
        ('Lower Saxony', 47624),
        ('North Rhine-Westphalia', 34085),
        ('Rhineland-Palatinate', 19853),
        ('Saarland', 2569),
        ('Saxony', 18416),
        ('Saxony-Anhalt', 20447),
        ('Schleswig-Holstein', 15799),
        ('Thuringia', 16171)
    ]

    # Find the maximum area
    max_area_state = max(states_area, key=lambda x: x[1])
    max_area = max_area_state[1]

    # Normalize the areas
    normalized_areas = [area / max_area for state, area in states_area]

    # Calculate the weighted average temperature
    weighted_sum = 0
    total_weight = 0
    for state, temp in temperatures.items():
        # Find the area for the current state
        area = next(area for state_name, area in states_area if state_name == state)
        # Find the normalized area for the current state
        normalized_area = next(area for state_name, area in zip(states_area, normalized_areas) if state_name[0] == state)
        # Calculate the weight for the current state
        weight = normalized_area * area
        weighted_sum += weight * temp
        total_weight += weight
    weighted_avg = weighted_sum / total_weight
        
    return weighted_avg
    
#Example of implimentation
temperatures = {
    'Berlin': 8,
    'Bremen': 7,
    'Hamburg': 7,
    'Saarland': 10,
    'Bavaria': 7,
    'Brandenburg': 7,
    'Hesse': 8,
    'Mecklenburg-Vorpommern': 7,
    'Lower Saxony': 7,
    'North Rhine-Westphalia': 9,
    'Rhineland-Palatinate': 9,
    'Schleswig-Holstein': 7,
    'Saxony': 7,
    'Saxony-Anhalt': 7,
    'Thuringia': 7
}

w_temp=watemp(temperatures)
