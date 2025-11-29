import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import HTML, Markdown, Image, JSON

# Create the sample DataFrame
cars = {
    'vin': ['1HGCM82633A123456', '1HGCM82633A654321', '1HGCM82633A789012'],
    'manufacturer': ['Toyota', 'Ford', 'Honda'],
    'year': [2020, 2018, 2021],
    'color': ['black', 'white', 'silver'],
    'body_type': ['Sedan', 'SUV', 'Coupe'],
    'engine_type': ['petrol', 'diesel', 'electric'],
    'transmission': ['manual', 'automatic', 'manual'],
    'fuel_type': ['gasoline', 'diesel', 'electric'],
    'seating_capacity': [5, 7, 4],
    'price': [20000.00, 25000.00, 30000.00],
    'status': ['active', 'sold', 'inactive'],
    'registration_date': ['2020-05-20', '2018-07-15', '2021-01-10']
}
df = pd.DataFrame(cars)
display(df)