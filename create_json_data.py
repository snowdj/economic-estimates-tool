import pandas as pd
import numpy as np

# gva
def read_reg_gva(year):
    df = pd.read_excel('Regional_GVA_2016_Sector_tables.xlsx', sheet_name=year, skiprows=[0,1,2,3,4,5])
    df = df[0:9]
    df = df.drop('UK total', axis=1)
    df = df.set_index('Sector')
    df = df.drop('% of total GVA')
    # df = df.drop('All Sectors')
    df = df.stack()
    df = df.reset_index()
    df['Year'] = int(year)
    df.columns = ['Sector', 'Region', 'GVA', 'Year']
    df = df.set_index(['Sector', 'Region', 'Year'])
    return df

years = [str(y) for y in list(range(2010, 2017))]
data = [read_reg_gva(y) for y in years]
df = pd.concat(data)
df = df.rename(index={'All DCMS sectors (excl Tourism and Civil Society)': 'All DCMS Sectors'})
df = df.rename(index={'All Sectors': 'UK'})
gva = df.copy()

# employment

# all sectors
df = pd.read_excel('Tables_1-19-DCMS_Sectors_Economic_Estimates_Employment_2017_tables.xlsx', sheet_name="3 - Region (000's)", skiprows=[0,1,2,3,4,5])
df = df.loc[0:11,['Region (Regional Area Code)', 'Unnamed: 5']]
df.columns = ['Region', 'Employment']
df['Region'] = df['Region'].apply(lambda x: x.split(' (')[0])
df['Year'] = 2017
df['Sector'] = 'All DCMS Sectors'
df[['Sector', 'Region', 'Year', 'Employment']]
allemp = df.copy()


# ci
df = pd.read_excel('Tables_20-30-DCMS_Sectors_Economic_Estimates_Employment_Creative_Industries_Subsectors.xlsx', sheet_name="22 - Region (000's)", skiprows=[0,1,2,3,4])
df = df.fillna(method='ffill')
df = df.drop(['% Change 2016-17', '% Change 2011-17'], axis=1)
newcolnames = list(df.columns)
newcolnames[0] = 'Region'
newcolnames[1] = 'Sector'
df.columns = newcolnames
df['Region'] = df['Region'].apply(lambda x: x.split('\n')[0])
df = df.set_index(['Sector', 'Region'])
df.columns.name = 'Year'
df = df.stack()
df = df.loc[['Creative Industries']]
df = df.drop(index='UK', level=1)
df = df.drop(index='England', level=1)
df.name = 'Employment'
df = df.reset_index()
ci = df.copy()

# digital
df = pd.read_excel('Tables_31-41-DCMS_Sectors_Economic_Estimates_Employment_Digital_Sector_Subsectors.xlsx', sheet_name="33 - Region (000's)", skiprows=[0,1,2,3,4])
df = df.fillna(method='ffill')
df = df.set_index('Sub-sector')
df = df.loc['Digital Sector']
df = df.drop(['% Change 2016-17', 'Unnamed: 7'], axis=1)
df = df.reset_index()
newcolnames = list(df.columns)
newcolnames[0] = 'Sector'
newcolnames[1] = 'Region'
df.columns = newcolnames
df['Region'] = df['Region'].apply(lambda x: x.split('\n')[0])
df = df.set_index(['Sector', 'Region'])
df.columns.name = 'Year'
df = df.stack()
df = df.drop(index='UK', level=1)
df = df.drop(index='England', level=1)
df.name = 'Employment'
df = df.reset_index()
digital = df.copy()

# culture
df = pd.read_excel('Tables_42-52-DCMS_Sectors_Economic_Estimates_Employment_Cultural_Sector_Subsectors.xlsx', sheet_name="44 - Region (000's)", skiprows=[0,1,2,3,4,5])
df = df.fillna(method='ffill')
df = df.set_index('Sub-sector')
df.columns.name = 'Region'
df = df.stack()
df.name = 'Employment'
df = df.reset_index()
df['Year'] = '2017'
df = df.rename(columns = {'Sub-sector': 'Sector'})
df = df.set_index(['Sector', 'Region', 'Year'])
df = df.loc[['Cultural Sector']]
df = df.drop(index='UK', level=1)
df = df.drop(index='England', level=1)
df = df.reset_index()
culture = df.copy()


employment = pd.concat([ci, digital, culture, allemp])
employment = employment.set_index(['Sector', 'Region', 'Year'])


# business sites
def set_to_nan(x):
    if not isinstance(x, int):
        return np.nan
    else:
        return x

df = pd.read_excel('DCMS_Economic_Estimates_February_2018_Business_sectors.xlsx', sheet_name="4_Business_sites_region", skiprows=[0,1,2,3,4], header=[0,2])
colnames = df.columns.to_frame()
colnames.columns = ['Year', 'Region']
colnames['Year'] = colnames['Year'].apply(set_to_nan)
colnames['Year'] = colnames['Year'].fillna(method='ffill')
colnames = colnames.set_index(['Year', 'Region'])
df.columns = colnames.index
df = df.drop([8,9,10,11,12,13,14])
columnNumbers = [x for x in range(df.shape[1])]  # list of columns' integer indices
columnNumbers.remove(13)
columnNumbers.remove(14)
columnNumbers.remove(27)
columnNumbers.remove(28)
df = df.iloc[:, columnNumbers] 
df = df.set_index([(np.nan, 'Sector')])
df.index.name = 'Sector'
df = df.rename(index={'All DCMS sectors (excl Civil Society)2,3': 'All DCMS Sectors'})
df = df.stack().stack()
df.name = 'Number of business sites'
df = df.reset_index()
df['Year'] = df['Year'].apply(int)
df = df.set_index(['Sector', 'Region', 'Year'])
businesses = df.copy()

# combine all measures
ee = pd.concat([gva.sort_index(), employment.sort_index(), businesses.sort_index()], axis=1).sort_index()
# there is no point rounding here as data manipulation in javascript means the data will need to be rounded again anyway
ee['GVA'] = ee['GVA'] / 1000
# ee['Number of business sites'] = round(ee['Number of business sites'],1)
ee.to_csv('static/data/ee_agg.csv')