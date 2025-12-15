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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    code_reg = []
    name_reg = []
    code_dep = []
    name_dep = []
    for i in range(len(departments)):
        for j in range(len(regions)):
            if departments["region_code"][i] == regions["code"][j]:
                code_dep.append(departments["code"][i])
                name_dep.append(departments["name"][i])
                code_reg.append(regions["code"][j])
                name_reg.append(regions["name"][j])
    regions_and_departments = {
        'code_reg' : code_reg,
        'name_reg': name_reg,
        'code_dep': code_dep,
        'name_dep' : name_dep
        }
    return pd.DataFrame(data=regions_and_departments)



def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad, which all have a code that contains `Z`.

    DOM-TOM-COM departments are departements that are remote from metropolitan
    France, like Guadaloupe, Reunion, or Tahiti.
    """
    ref_clean = referendum.copy()
    reg_clean = regions_and_departments.copy()

    ref_clean["Department code"] = ref_clean["Department code"].astype(str).str.zfill(2)
    reg_clean["code_dep"] = reg_clean["code_dep"].astype(str).str.zfill(2)
    ref_clean = ref_clean[~ref_clean["Department code"].str.contains("Z")]

    merged_df = pd.merge(
        ref_clean,
        reg_clean,
        left_on="Department code",
        right_on="code_dep",
        how="inner"
    )

    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    aggregations = {
        'name_reg': 'first',
        'Registered': 'sum',
        'Abstentions': 'sum',
        'Null': 'sum',
        'Choice A': 'sum',
        'Choice B': 'sum'
    }

    result = referendum_and_areas.groupby('code_reg').agg(aggregations)
    ordered_columns = ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    return result[ordered_columns]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions = gpd.read_file('data/regions.geojson')

    gdf = regions.merge(
        referendum_result_by_regions,
        left_on='code',
        right_index=True
    )
    gdf['ratio'] = gdf['Choice A'] / (gdf['Choice A'] + gdf['Choice B'])

    gdf.plot(column='ratio', legend=True, figsize=(10, 10), cmap='coolwarm')
    plt.title("Taux de vote 'Choice A' par région")
    plt.axis('off')
    return gdf


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
