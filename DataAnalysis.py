# -*- coding: utf-8 -*-
"""
Created on Fri May 20 17:27:36 2016

@author: cristiano
"""
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.cluster import KMeans
import locale
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

# Read csv from DataBank (Get from http://databank.worldbank.org/data/reports.aspx?source=education-statistics-~-all-indicators#)
pisa_data = pd.read_csv("PisaData.csv",na_values='..')
# Select only the last year available
pisa_data = pisa_data[['Country','Country Code','Series Code','2012 [YR2012]']]
# Remove missing values
pisa_data = pisa_data[pd.isnull(pisa_data['2012 [YR2012]']) == False]
# Aggregate countries
pisa_data = pd.pivot_table(pisa_data,index=['Country','Country Code'],values=['2012 [YR2012]'],columns=['Series Code'], aggfunc=np.sum)
pisa_data.reset_index(inplace=True)
# Since the columns are tuples, get the second name:
c_name = [i[1] for i in pisa_data.columns]
c_name[0] = 'Country' #except for Country
c_name[1] = 'wbcode' #except for Country
pisa_data.columns = c_name

# Read CPI data (from http://www.transparency.org/cpi2015/)
cpi_data = pd.read_excel("2015_CPI_data.xlsx",skiprows=1)
cpi_data = cpi_data[['Country','wbcode','CPI2015','Rank']]
cpi_data.columns = ['Country','wbcode','CPI2015','Rank.CPI']

# Reading and cleaning GDP Data (from http://data.worldbank.org/data-catalog/GDP-ranking-table)
gdp_data = pd.read_csv("GDP.csv",encoding = "ISO-8859-1",na_values='..',thousands=',')
gdp_data = gdp_data.iloc[:,[0,1,3,4]]
gdp_data.dropna(how='any',inplace=True)
# Rename columns
gdp_data.columns = ['wbcode','Rank.GDP','Country','GDP'] 
gdp_data['GDP'] = gdp_data['GDP'].apply(lambda x: locale.atoi(x)) 
gdp_data['GDP.Norm'] = gdp_data['GDP']/gdp_data['GDP'].max()
gdp_data['Rank.GDP'] = gdp_data['Rank.GDP'].astype(int)

# Reading HDI data
hdi_data = pd.read_excel('2015_HDI.xls',skiprows=8)
hdi_data = hdi_data.iloc[:,0:3]
hdi_data.dropna(how='any',inplace=True)
hdi_data.columns = ['Rank.HDI','Country','HDI.Index']

# Merge pisa,cpi and gdp data by country code
merged_data = pd.merge(pisa_data,cpi_data,on='wbcode').merge(gdp_data,on='wbcode')
merged_data = merged_data[['Country','wbcode','GDP','GDP.Norm','LO.PISA.MAT','LO.PISA.REA','LO.PISA.SCI','CPI2015','Rank.CPI','Rank.GDP']]

# Since names are a little different , lets use a method to compare them
# List Countries we have already merged
def verify_country_names(merged_data,hdi_data):
    # Just to show a method to compare strings
    from difflib import SequenceMatcher
    l_merged = list(merged_data['Country'])
    l_hdi = list(hdi_data['Country'])
    count = 0
    for c in l_merged:
        cname = ''
        ratio = 0.0
        for cm in l_hdi:
            if SequenceMatcher(None, c, cm).ratio() == 1.0:
                cname = cm
                ratio = SequenceMatcher(None, c, cm).ratio()
                count += 1
                exit
        if ratio < 1.0:
            print(c,cname,ratio)
    
    print(count)
    # After running this function edit the HDI data

merged_data = pd.merge(merged_data,hdi_data,on='Country')

#verify_country_names(merged_data,hdi_data)
# Let's compare variable pairwise
sns.pairplot(merged_data[['LO.PISA.REA','LO.PISA.SCI','CPI2015','GDP.Norm','HDI.Index']])
sns.plt.show()

# LO.PISA.REA and  LO.PISA.SCI seems to be very dependent, let's use only LO.PISA.REA
# To cluster our data
clustering_data = merged_data[['LO.PISA.REA','CPI2015','GDP.Norm','HDI.Index']]
# 
kmeans_model = KMeans(n_clusters=3, random_state=1)
countries_distances = kmeans_model.fit_transform(clustering_data)
countries_labels = kmeans_model.labels_
merged_data["cluster"] = countries_labels

