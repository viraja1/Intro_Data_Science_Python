
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[4]:

import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[5]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[6]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    df = pd.read_csv("university_towns.txt", sep="\n", header=None)
    df["RegionName"] = df[0].apply(lambda x: x.split("(")[0].strip() if x.count("(") else np.NaN if x.count("[ed") else x)
    df["State"] = df[0].apply(lambda x: x.split("[")[0].strip() if x.count("[ed") else np.NaN).fillna(method="ffill")
    df = df.dropna().drop(0, axis=1).reindex(columns=["State", "RegionName"]).reset_index(drop=True)
    return df

get_list_of_university_towns()


# In[7]:

def get_gdp_data():
    gdp = pd.read_excel("gdplev.xls", header=4, index_col=4)
    gdp = gdp[["GDP in billions of current dollars.1", "GDP in billions of chained 2009 dollars.1"]]
    gdp = gdp.dropna()
    gdp = gdp.drop(gdp.index[0: gdp.index.get_loc("2000q1")])
    gdp["diff"] = gdp["GDP in billions of chained 2009 dollars.1"].diff()
    gdp["diff"] = gdp["diff"].apply(lambda x: 1 if x > 0 else 0)
    return gdp

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    gdp = get_gdp_data()
    diff_string = ''.join(str(x) for x in gdp["diff"].values)
    pattern = "0011"
    start_of_pattern = diff_string.index("0011")
    before_pattern = diff_string[0:start_of_pattern]
    recession_start_index = before_pattern.rindex("1") + 1
    return gdp.index[recession_start_index]
get_recession_start()


# In[8]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    gdp = get_gdp_data()
    diff_string = ''.join(str(x) for x in gdp["diff"].values)
    pattern = "0011"
    start_of_pattern = diff_string.index("0011")
    recession_end_index = start_of_pattern + len(pattern) - 1
    return gdp.index[recession_end_index]   

get_recession_end()


# In[9]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    gdp = get_gdp_data()
    recession_start = get_recession_start()
    recession_start_index = gdp.index.get_loc(recession_start)
    recession_end = get_recession_end()
    recession_end_index = gdp.index.get_loc(recession_end)
    recession = gdp.iloc[recession_start_index:recession_end_index+1]
    return recession["GDP in billions of chained 2009 dollars.1"].idxmin()

get_recession_bottom()


# In[10]:

def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    housing_data = pd.read_csv("City_Zhvi_AllHomes.csv")
    column_list = list(housing_data.columns)
    start_of_list = column_list.index('2000-01')
    date_list = column_list[start_of_list:]
    tdf = housing_data[date_list]
    tdf.columns = tdf.columns.map(lambda x: pd.to_datetime(x))
    mdf = tdf.T.resample('Q').mean().T
    mdf.columns = mdf.columns.map(lambda x: '{}q{}'.format(x.year, x.quarter))
    mdf["RegionName"] = housing_data["RegionName"]
    mdf["State"] = housing_data["State"].apply(lambda x: states.get(x))
    final_df = mdf.set_index(['State', 'RegionName'])
    return final_df

convert_housing_data_to_quarters()


# In[31]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    recession_start = get_recession_start()
    recession_bottom = get_recession_bottom()
    gdp = get_gdp_data()
    quarter_before_recession_start = gdp.index[gdp.index.get_loc(recession_start) - 1]
    housing_data = convert_housing_data_to_quarters()
    housing_data["price_ratio"] = housing_data[quarter_before_recession_start].div(housing_data[recession_bottom])
    university_town_tuples = [tuple(x) for x in get_list_of_university_towns().values]
    university_towns = housing_data.loc[university_town_tuples]
    non_university_towns = housing_data[~housing_data.index.isin(university_town_tuples)]
    p = ttest_ind(university_towns["price_ratio"].dropna(), non_university_towns["price_ratio"].dropna())[1]
    different = True if p < 0.01 else False
    university_town_price_ratio_mean = university_towns["price_ratio"].mean()
    non_university_town_price_ratio_mean = non_university_towns["price_ratio"].mean()
    better = "university town" if university_town_price_ratio_mean < non_university_town_price_ratio_mean else "non-university town"
    return (different, p, better)

run_ttest()


# In[ ]:



