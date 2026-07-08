# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 12:39:39 2023

@author: Shahabedin Chatraee Azizabadi
Sonntagsfrage
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import seaborn as sns
from statsmodels.stats.weightstats import ztest as ztest
import statsmodels.stats.weightstats as ws
#-----------------IMPORTANT NOTE----------------------
# DEPENDING ON WHICH DATAFRAME IS USED WE HAVE TWO MAIN FEATURES THAT CAN ALTERNATIVALY REPLACE
# feature1="sum_page_views"or feature1= "sum_total_seconds_spent"
#df=pd.read_csv("C:/Users/sazizaba/Music/SI_project/projects/Wochenendfrage/adobe_full_bild_grouped.csv")
df=pd.read_csv("adobe_full_bild_grouped_time_spend.csv")
df["date"] = pd.to_datetime(df["date"])

df["IsWeekend"] = df["date"].dt.weekday >= 5

# some general stats
gs=df.describe()
# To count the sample size of week and weekend groups: They are almost equal
a=(df["IsWeekend"] == False).sum() # The sample size of the week days

b=(df["IsWeekend"] == True).sum()  # The sample size of the weekend days
#-------------------------------------------------------------------------------

# Splitting week and weekend samples
def week_weekend_spl(df):
    df_week=df.loc[df['IsWeekend'] == False]
    
    df_weekend=df.loc[df['IsWeekend'] == True]
    
    return df_week,df_weekend
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def avg_page_views(df,feature1):
    df_week,df_weekend=week_weekend_spl(df)
    # week_mean=df_week["sum_page_views"].mean()
    # weekend_mean=df_weekend["sum_page_views"].mean()
    week_mean=df_week[feature1].mean()
    weekend_mean=df_weekend[feature1].mean()    
    week_std=df_week[feature1].std()
    weekend_std=df_weekend[feature1].std() 
    return week_mean, weekend_mean, week_std, weekend_std
#------------------------------------------------------------------------------------
df_week,df_weekend=week_weekend_spl(df)

# Investigating the distribution of  the character translated in control and test groups
def plot_dist(df,feature1):
    df_week,df_weekend=week_weekend_spl(df)
    f, ax = plt.subplots(1, 1)
    sns.distplot(getattr(df_week,feature1),label = 'week',ax=ax)
    sns.distplot(getattr(df_weekend,feature1),label = 'weekend',ax=ax)
    ax.legend()
    return

#  A significant Z-test for the number of characters translated, the size of samples are big enough for that test
def two_samp_z_test_charact(df,feature1):
    df_week,df_weekend=week_weekend_spl(df)
    z_stat, p_val= ztest(getattr(df_week,feature1),getattr(df_weekend,feature1),alternative='smaller')
    #z_stat, p_val= CompareMeans.ztest_ind(alternative='smaller', usevar='unequal')

    return z_stat, p_val
# A more specific z-test for unequal stds
def alt_z_test(df,feature1):
    df_week,df_weekend=week_weekend_spl(df)
    col1 = ws.DescrStatsW(getattr(df_week,feature1))
    col2 = ws.DescrStatsW(getattr(df_weekend,feature1))

    cm_obj = ws.CompareMeans(col1, col2)

    zstat2, z_pval2 = cm_obj.ztest_ind(alternative='smaller',usevar='unequal')
    
    return zstat2, z_pval2
#------------------------------------------------------------------------------------
# mean of the page view for the week and weekend
week_mean, weekend_mean, week_std, weekend_std=avg_page_views(df,"sum_total_seconds_spent")
# The result of z-test for the number of characters translated 
z_stat, p_val=two_samp_z_test_charact(df,"sum_total_seconds_spent")
zstat2, z_pval2=alt_z_test(df,"sum_total_seconds_spent")
plo=plot_dist(df,"sum_total_seconds_spent")
print("P-value for sum_of_..=",p_val)
