# Select columns
display(df[['manufacturer','price']])

# # Select row with .loc (label) and .iloc (position)
# print("Select row with .loc (label)")
# display(df.loc[0])
# print("Select row with .iloc (position)")
# display(df.iloc[0])

# # Conditional selection
# display(df[df['price'] > 22000])

# # Setting index
# df_indexed = df.set_index('vin')
# display(df_indexed.head())