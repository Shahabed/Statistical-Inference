# Analysis of the AB test for the user experience


## The goal of the project: 
Herein, we want to analysis the result of the AB test. By using the significant test we want to observe if the change in the website was an effective improvement in the user experience and beneficial for the company.


## 1. Reading the data, primary analysis: 
Here, as a first step,  we read the CSV file. Then we do some primary analysis of data like the general statistical properties of data and investigate whether the season_id is unique. Also, we count the sample size of the control and test groups and conclude that they are almost equal.

## 2. Splitting control and test sample:

We use the function `control_test_spl` to split the control and the test group. This is the necessary step for the significant test. 

## 3. Chi-Squared Test for conversion rate:

The main metric that can be used in the significant test is the conversion(rate). It is a binary distributed metric and thats the reason for implementing the Chi-Squared Test. The function `chi_test_conv` is used for the significant test. We compute the conversion/ non-conversion scenarios for both the control and test groups and use these four parameters in the final computation of the p-value.

## 4.  A significant Z-test for the number of characters translated:

Alternatively, we can apply the significant test for the number of characters translated. The samples sizes are large enough for that test. the respective function for that test is `two_samp_z_test_charact`. 
