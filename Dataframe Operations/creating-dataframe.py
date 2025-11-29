# From dictionary
df_from_dict = pd.DataFrame(cars)
display(df_from_dict)

# From lists/arrays
df_from_list = pd.DataFrame([[1, 'Arnauld'], [2, 'Leandre'], [3, 'Pacifique'], [4, 'Pascal']], columns=['student_id','names'])
display(df_from_list)

# From CSV / Excel
#Use pd.read_csv("file.csv") and pd.read_excel("file.xlsx") to load files.