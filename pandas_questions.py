"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

  The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # We join them on the region code
    combined_areas = pd.merge(departments, regions, on='code_reg')
    
    # We only keep the specific columns the project asked for
    final_cols = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return combined_areas[final_cols]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """

    # Attach the region info to every vote count
    full_data = pd.merge(referendum, regions_and_departments, on='code_dep')
    
    # Filter: We use the 'tilde' symbol (~) to say "Keep everything that 
    # does NOT contain Z"
    is_overseas = full_data['code_dep'].str.contains('Z') | full_data['code_reg'].str.contains('Z')
    metropolitan_data = full_data[~is_overseas].copy()

    return metropolitan_data


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    # We list the numeric columns we want to total up
    vote_columns = ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    
    # We group by the region code and name
    regional_totals = referendum_and_areas.groupby(['code_reg', 'name_reg'])[vote_columns].sum()
    
    # The instructions asked for the index to be 'code_reg', 
    # so we move 'name_reg' back to a regular column.
    return regional_totals.reset_index(level='name_reg')


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    # Load the shapes of the regions
    france_map = gpd.read_file('regions.geojson')
    
    # Join our calculated results to the map shapes
    # (Assuming the GeoJSON uses 'code' for the region ID)
    merged_map = france_map.merge(
        referendum_result_by_regions, 
        left_on='code', 
        right_index=True
    )
    
    # Calculate the 'Ratio': How well did Choice A do compared to Choice B?
    # Expressed ballots = A + B
    merged_map['ratio'] = merged_map['Choice A'] / (merged_map['Choice A'] + merged_map['Choice B'])
    
    # Create the plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    
    # We use a color map (cmap) like 'RdBu' (Red/Blue) or 'YlGnBu'
    merged_map.plot(
        column='ratio',
        cmap='coolwarm', 
        legend=True,
        ax=ax,
        edgecolor='white', # Add white borders between regions
        linewidth=0.5
    )
    
    # Clean up the look
    ax.set_title("Referendum Results: Percentage of 'Choice A'", fontsize=15)
    ax.axis('off') # We don't need latitude/longitude lines for a map

    return merged_map


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()
