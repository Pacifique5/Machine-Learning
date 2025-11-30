display(df.groupby('brand')['price'].mean())

display(df.agg({'price':['sum','mean','max'], 'seating_capacity':['min','max']}))

# What pivot_table() Does?
# A pivot table groups your data and performs an aggregation (like average, sum, count, etc.).
# The default is mean
display(df.pivot_table(values='price', index='brand'))

# Pivot table with multiple aggregations for price and quantity
pivot = df.pivot_table(
    index='brand',
    values=['price', 'seating_capacity'],
    aggfunc={'price': ['mean', 'max', 'min'], 'seating_capacity': ['sum', 'mean']}
)
# Flatten multi-level columns
pivot.columns = ['_'.join(col).strip() for col in pivot.columns.values]
display(pivot)

#It counts the frequency of combinations of two categorical variables.
display(pd.crosstab(df['engine_type'], df['transmission']))

#Aquestion for intelligent people is how to visualize the above