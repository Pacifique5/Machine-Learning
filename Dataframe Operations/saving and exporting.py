csv_path = '/data/cars_export.csv'
df.to_csv(csv_path, index=False)
print('Saved CSV to', csv_path)

excel_path = '/data/cars_export.xlsx'
df.to_excel(excel_path, index=False)
print('Saved Excel to', excel_path)

json_path = '/data/cars_export.json'
df.to_json(json_path, orient='records', date_format='iso')
print('Saved JSON to', json_path)

# For SQL: use df.to_sql('cars', con=engine) with a SQLAlchemy engine (not executed here).