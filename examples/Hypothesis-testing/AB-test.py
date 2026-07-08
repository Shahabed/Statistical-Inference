# -*- coding: utf-8 -*-
"""
AB test for a customer experience in a website: a case study
Shahabedin Chatraee Azizabadi

"""
import pandas as pd
import numpy as np
import scipy.stats as sst 
import seaborn as sns
from statsmodels.stats.weightstats import ztest as ztest
# 1. Reading the CSV file

df=pd.read_csv("session_data.csv")

# some general stats
df.describe()
#Uniqueness of session_id
df["session_id"].nunique()

# To count the sample size of control and test groups: They are almost equal
a=(df["variant_id"] == 0).sum()

b=(df["variant_id"] == 1).sum()

# Splitting control and test sample
def control_test_spl(df):
    df_cont=df.loc[df['variant_id'] == 0]
    
    df_test=df.loc[df['variant_id'] == 1]
    
    return df_cont,df_test

# Chi-Squared Test for conversion rate

def chi_test_conv(df):
    df_cont,df_test=control_test_spl(df)
    Aconv=(df_cont["conversion"] == 1).sum()
    Anoconv=(df_cont["conversion"] == 0).sum()
    Bconv=(df_test["conversion"] == 1).sum()
    Bnoconv=(df_test["conversion"] == 0).sum()
    
    
    T = np.array([[Aconv, Anoconv], [Bconv, Bnoconv]])
    
    p=sst.chi2_contingency(T,correction=False)[1]
   
    return p

# Investigating the distribution of  the character translated in control and test groups
#sns.distplot(df_cont.characters_translated)
#sns.distplot(df_test.characters_translated)

    
#  A significant Z-test for the number of characters translated, the size of samples are big enough for that test
def two_samp_z_test_charact():
    df_cont,df_test=control_test_spl(df)
    z_stat, p_val= ztest(df_cont.characters_translated,df_test.characters_translated)
    return z_stat, p_val

## Alternatively, one can use a significant T-test for the number of characters translated

#def two_samp_t_test_charact():
#    df_cont,df_test=control_test_spl(df)
#    t_stat, p_val= sst.ttest_ind(df_cont.characters_translated,df_test.characters_translated)
#    return t_stat , p_val


# The result of  Chi-Squared Test for the conversion rate is a p-value
p_chi2_test=chi_test_conv(df)
print("P-value for conversion rate=",p_chi2_test)

# The result of z-test for the number of characters translated 
z_stat, p_val=two_samp_z_test_charact()
print("P-value for characters translated=",p_val)
