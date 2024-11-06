import pandas as pd
import requests
import geopandas as gpd
import matplotlib.pyplot as plt

# Get population data
popurl = 'https://api.census.gov/data/2020/dec/pl?get=NAME,P1_001N&for=state:*'
popdata = requests.get(popurl).json()

df_pop = pd.DataFrame(popdata[1:], columns=popdata[0]).rename(columns={'P1_001N': 'POP'})
df_pop['POP'] = df_pop['POP'].astype(int)

# Get electoral vote counts
df_electoral = pd.read_csv('data/statevotes.csv')

# Merge the 2 dfs
df = df_pop.merge(df_electoral, on=['NAME'])

# calcualte individual vote weight and fair number of votes based on population
df['VOTE_WEIGHT'] = df['NUM_VOTES'] / df['POP']
df['FAIR_NUM_VOTES'] = df['NUM_VOTES'].sum() / df['POP'].sum() * df['POP']
df['VOTE_DELTA'] = df['NUM_VOTES'] - df['FAIR_NUM_VOTES']

# Sort the df by weight
df = df.sort_values(by=['VOTE_WEIGHT'], ascending=False)
df.head()

# get gdf of state boundaries
gdf = gpd.read_file('data/US_State_Boundaries/US_State_Boundaries.shp')

# merge df to gd
gdf_merge = gdf.merge(df)

# Create a figure with two subplots
fig, axes = plt.subplots(3, 1, figsize=(10, 10))
fig.patch.set_facecolor('lightgray')

# Plot the first map (using default classification)
gdf_merge.plot(column='VOTE_WEIGHT', ax=axes[0],
               cmap='YlOrRd')
axes[0].set_title('Voter Weight (Straight)', loc='center')
axes[0].set_axis_off()

# Plot the second map (using quantiles classification)
gdf_merge.plot(column='VOTE_WEIGHT', ax=axes[1], scheme='quantiles',
               cmap='YlOrRd')
axes[1].set_title('Voter Weight (Quantile)', loc='center')
axes[1].set_axis_off()

# Plot the second map (using quantiles classification)
gdf_merge.plot(column='VOTE_DELTA', ax=axes[2], legend=True,
               legend_kwds={"orientation": "horizontal", "pad": 0.01},
               cmap='coolwarm')
axes[2].set_title('Under/Over Electoral Representation', loc='center')
axes[2].set_axis_off()

# Adjust layout to ensure maps don't overlap
plt.tight_layout()

plt.show()