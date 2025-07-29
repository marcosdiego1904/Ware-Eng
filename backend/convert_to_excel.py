import pandas as pd

pd.read_csv('data/comprehensive_inventory_test.csv').to_excel('data/comprehensive_inventory_test.xlsx', index=False)
