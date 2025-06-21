import pandas as pd

# Load the CSV file
df = pd.read_csv("AI-forecast.csv")

# Convert 'date' to datetime format
df['date'] = pd.to_datetime(df['date'])

# Step 1: Sum predictions across all part numbers per day
daily_total = df.groupby('date')['pred'].sum().reset_index(name='daily_total_pred')

# Step 2: Compute monthly sum across all part numbers
df['month'] = df['date'].dt.to_period('M')
monthly_total = df.groupby('month')['pred'].sum().reset_index(name='monthly_total_pred')

# Display the monthly totals
print(monthly_total)

# Optionally, save results to CSV
# monthly_total.to_csv("monthly_totals.csv", index=False)

