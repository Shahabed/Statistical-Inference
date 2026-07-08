# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 16:26:26 2022

@author: Shahabedin Chatraee Azizabadi
RKZ calculation
"""
import pyodbc
import numpy as np
import pandas as pd
import sqlalchemy
from knockknock.teams_sender import teams_sender

#****Define calculation of KPIs*****
# Get the exceptional retailers and remove from the data frame
def get_exceptional_retailers_and_remove_from_df(df ,year = 2022,mon = 1):
    mon2 = mon + 1
    year2 = year
    if mon < 10:
        mon = '0'+str(mon)
    else:
        mon = str(mon)
    if mon2 > 12:
        mon2 = '01'
        year2 = year + 1
    elif mon2 < 10:
        mon2 = '0'+str(mon2)
    else:
        mon2 = str(mon2)

    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=deaxsmapsql01.itservices.asudc.net,6200;'
                          'Database=ABLAGE;'
                          'Trusted_Connection=yes;')
    sql = f""" select
        EH_KEY
        ,START_DATUM
        ,ENDE_DATUM
        ,OGR_KEY
        ,OBJ_KEY from Regulierungsstatistik.dbo.vwAA_REGKENNZ_Herausnahmen where OGR_KEY = 7 and START_DATUM < '{year2}-{mon2}-01' and ENDE_DATUM >= '{year}-{mon}-01'"""
    df_excep = pd.read_sql(sql, conn)
    li_ind = []
    for ind,row in df_excep.iterrows():
        li_ind = li_ind + df.EH_KEY[(df.EH_KEY == row.EH_KEY) & (df.EVT >= row.START_DATUM) & (df.EVT <= row.ENDE_DATUM) & (df.OBJ_KEY == row.OBJ_KEY) & (df.OGR_KEY == row.OGR_KEY) ].index.to_list()
    df = df[~df.index.isin(li_ind)].copy()
    
    sql = f""" select
        HKDFIL2_KEY
        ,START_DATE
        ,END_DATE
        ,OGR_KEY
        ,OBJ_KEY from [Regulierungsstatistik].[dbo].[TB_RKZ_EXCEPTION_HKDFIL] where OGR_KEY = 7 and START_DATE < '{year2}-{mon2}-01' and END_DATE >= '{year}-{mon}-01'"""
    df_excep_hkdfil = pd.read_sql(sql, conn)
    li_ind = []
    for ind,row in df_excep_hkdfil.iterrows():
        li_ind = li_ind + df.EH_KEY[(df.HKDFIL2_KEY == row.HKDFIL2_KEY) & (df.EVT >= row.START_DATE) & (df.EVT <= row.END_DATE) & (df.OBJ_KEY == row.OBJ_KEY) & (df.OGR_KEY == row.OGR_KEY) ].index.to_list()
    df = df[~df.index.isin(li_ind)].copy()        
    return df
#------------------------------------------------------------------------------------------
#

def ajdust_OBJ_TAU(df,hkdfil, obj_old, obj_new, tau_new = None, hkdfil_colname = 'HKDFIL2_KEY', obj_colname = 'OBJ_KEY', tau_colname = 'TAU_KEY'):
    """
    requires pandas as pd
    df: Dataframe to apply changes on
    hkdfil: HKDFIL_KEY to apply changes on
    obj_old: old OBJ_KEY
    obj_new: new OBJ_KEY
    tau_new: new TAU, if None search for existing obj_new for hkdfil and tau and use this existing tau. 
                When no exisitng obj_new for hkdfil can be found no changes will be apllied
    xx_colname: name of column
    """
    if pd.notna(tau_new):
        df.loc[(df[hkdfil_colname] == hkdfil) & (df[obj_colname] == obj_old) , tau_colname] = tau_new
    elif not df.loc[(df[hkdfil_colname] == hkdfil) & (df[obj_colname] == obj_new), obj_colname].empty:
        df.loc[(df[hkdfil_colname] == hkdfil) & (df[obj_colname] == obj_old) , tau_colname] = df.loc[(df[hkdfil_colname] == hkdfil) & (df[obj_colname] == obj_new) , tau_colname].mode().iloc[0]   
    df.loc[(df[hkdfil_colname] == hkdfil) & (df[obj_colname] == obj_old) , obj_colname] = obj_new
    return df
def adjust_old_ir_to_lean(data_rqavq_monsat_vgk, year,tau = True):
    if year>=2022:
        data_rqavq_monsat_vgk.loc[data_rqavq_monsat_vgk.HKDFIL2_KEY == 106600, 'HKDFIL2_KEY'] = 123400
        if tau == False:
            data_rqavq_monsat_vgk['TAU_KEY'] = 0
        data_rqavq_monsat_vgk2 = data_rqavq_monsat_vgk.loc[(data_rqavq_monsat_vgk.HKDFIL2_KEY == 82506) & (data_rqavq_monsat_vgk.OBJ_KEY  == 998), :].copy()
        data_rqavq_monsat_vgk2['OBJ_KEY'] = 993
        data_rqavq_monsat_vgk = data_rqavq_monsat_vgk.append(data_rqavq_monsat_vgk2).copy()
        data_rqavq_monsat_vgk.loc[(data_rqavq_monsat_vgk.HKDFIL2_KEY == 82506) & (data_rqavq_monsat_vgk.OBJ_KEY  == 998), 'OBJ_KEY'] = 997
    
    
    
        #BILD
        li_HKDFIL = [115605,115601,100701,36100,58202,82502,82502,82504,108201,108201,98100,108202, 96503] 
        li_OBJ_OLD = [992  ,995   ,995   ,998   ,997 ,998  ,955  ,998  ,955   ,954   ,998  ,998   ,998] 
        li_OBJ_new = [951  ,922   ,922   ,997   ,993 ,997  ,997  ,997  ,997   ,997   ,997  ,997   ,993] 
        li_tau_new = [None,None,None,5,None,5,5,5,5,3,5,5,5] 
        for hkdfil, obj_old, obj_new, tau_new in zip(li_HKDFIL,li_OBJ_OLD,li_OBJ_new,li_tau_new):
            data_rqavq_monsat_vgk = ajdust_OBJ_TAU(data_rqavq_monsat_vgk,hkdfil, obj_old, obj_new, tau_new)  
        if tau == False:
            data_rqavq_monsat_vgk.drop(columns = ['TAU_KEY'], inplace = True)
            
    return data_rqavq_monsat_vgk

#BILD_IR_COMPLETE = pd.read_excel('2022_Q1_BILD_IR_Sätze_V2.xlsx')
#print(BILD_IR_COMPLETE[(BILD_IR_COMPLETE.OBJ_KEY == 2920) & (BILD_IR_COMPLETE.VGK == -1)].head())
def adjust_mars_tau_to_vis_tau(BAMS_IR_COMPLETE):
    #print(BAMS_IR_COMPLETE.shape)
    BAMS_IR_COMPLETE['HKDFIL2_KEY'] = BAMS_IR_COMPLETE['HKDFIL2_KEY'].astype('int64')
    BAMS_IR_COMPLETE['OBJ_KEY'] = BAMS_IR_COMPLETE['OBJ_KEY'].astype('int64')
    BAMS_IR_COMPLETE.loc[BAMS_IR_COMPLETE.TAU_KEY.isna(),'TAU_KEY'] = 0

    BAMS_IR_COMPLETE['TAU_KEY'] = BAMS_IR_COMPLETE['TAU_KEY'].astype('int64')

    conn = pyodbc.connect('Driver={SQL Server};'
                              'Server=deaxsmapsql01.itservices.asudc.net,6200;'
                              'Database=ABLAGE;'
                              'Trusted_Connection=yes;')
    sql = f"select DISTINCT OBJ_KEY, HKDFIL_KEY AS HKDFIL2_KEY, TAU_KEY from ABLAGE.vis.TB_KENNZAHL_AKT where OGR_KEY = 7 and SPA_KEY in (1,31) and EJAHR = 2022 and LIEF_EH > 0 "
    data_spa = pd.read_sql(sql,conn)
    data_spa['HKDFIL2_KEY'] = data_spa.HKDFIL2_KEY.apply(lambda x: int(np.floor(x/100) * 10 + x%100))
    data_spa = data_spa.drop_duplicates().copy()
    data_spa['HKD_OBJ_TAU'] = data_spa.OBJ_KEY.astype(str)+'_'+data_spa.HKDFIL2_KEY.astype(str)+'_'+data_spa.TAU_KEY.astype(str)

    BAMS_IR_COMPLETE['HKD_OBJ_TAU'] = BAMS_IR_COMPLETE.OBJ_KEY.astype(str)+'_'+BAMS_IR_COMPLETE.HKDFIL2_KEY.astype(str)+'_'+BAMS_IR_COMPLETE.TAU_KEY.astype(str)
    

    df_not_poss = pd.DataFrame()
    #function passende TAUs aus vis zuordnen
    for ind, row in data_spa.iterrows():
        if row['HKD_OBJ_TAU'] in list(BAMS_IR_COMPLETE['HKD_OBJ_TAU']):
            continue
        elif (BAMS_IR_COMPLETE[(BAMS_IR_COMPLETE.HKDFIL2_KEY == row['HKDFIL2_KEY']) & (BAMS_IR_COMPLETE.OBJ_KEY == row['OBJ_KEY'])].shape[0] == 1) & (data_spa[(data_spa.HKDFIL2_KEY == row['HKDFIL2_KEY']) & (data_spa.OBJ_KEY == row['OBJ_KEY'])].shape[0] == 1) :
            BAMS_IR_COMPLETE.loc[(BAMS_IR_COMPLETE.HKDFIL2_KEY == row['HKDFIL2_KEY']) & (BAMS_IR_COMPLETE.OBJ_KEY == row['OBJ_KEY']), 'TAU_KEY'] = row['TAU_KEY']
        elif (BAMS_IR_COMPLETE.loc[(BAMS_IR_COMPLETE.HKDFIL2_KEY == row['HKDFIL2_KEY']) & (BAMS_IR_COMPLETE.OBJ_KEY == row['OBJ_KEY']), 'HKD_OBJ_TAU'].isin(data_spa.HKD_OBJ_TAU).any() == False) & (data_spa[(data_spa.HKDFIL2_KEY == row['HKDFIL2_KEY']) & (data_spa.OBJ_KEY == row['OBJ_KEY'])].shape[0] == 1):
            BAMS_IR_COMPLETE.loc[(BAMS_IR_COMPLETE.HKDFIL2_KEY == row['HKDFIL2_KEY']) & (BAMS_IR_COMPLETE.OBJ_KEY == row['OBJ_KEY']), 'TAU_KEY'] = row['TAU_KEY']
        else:
            df_not_poss = df_not_poss.append(BAMS_IR_COMPLETE[(BAMS_IR_COMPLETE.HKDFIL2_KEY == row['HKDFIL2_KEY']) & (BAMS_IR_COMPLETE.OBJ_KEY == row['OBJ_KEY'])])
    #print(BAMS_IR_COMPLETE.shape)
    BAMS_IR_COMPLETE['HKD_OBJ_TAU'] = BAMS_IR_COMPLETE.OBJ_KEY.astype(str)+'_'+BAMS_IR_COMPLETE.HKDFIL2_KEY.astype(str)+'_'+BAMS_IR_COMPLETE.TAU_KEY.astype(str)
    return BAMS_IR_COMPLETE.copy()
def IR_HKDFIL(df_filobj_final):
    df = df_filobj_final[(df_filobj_final.IR_SATZ == 0) | (df_filobj_final.IR_SATZ.isna())].copy()
    #df.loc[df.HKDFIL2_KEY == 938001, 'HKDFIL2_KEY'] = 938003
    assert df.shape[0] == 0,f"check SQL table TB_RISK_SOLLWERTE for missing entries for {df[['HKDFIL2_KEY', 'OBJ_KEY']]}"
    df_filobj_final['IRxBEZ'] = df_filobj_final.BEZUG * df_filobj_final.IR_SATZ
    df_IR_HKDFIL_OBJ = df_filobj_final.groupby(['HKDFIL2_KEY', 'OGR_KEY']).IRxBEZ.sum() / df_filobj_final.groupby(['HKDFIL2_KEY', 'OGR_KEY']).BEZUG.sum()
    df_IR_HKDFIL_OBJ = df_IR_HKDFIL_OBJ.reset_index(name = 'IR_SATZ_HKDFIL')
    df_filobj_final.drop(columns = ['IRxBEZ'], inplace = True)
    df_filobj_final = df_filobj_final.merge(df_IR_HKDFIL_OBJ, on = ['HKDFIL2_KEY', 'OGR_KEY'], how = 'left')
    df_filobj_final['IRxBEZ'] = df_filobj_final.BEZUG * df_filobj_final.IST_RQ
    df_IR_HKDFIL_OBJ = df_filobj_final.groupby(['HKDFIL2_KEY', 'OGR_KEY']).IRxBEZ.sum() / df_filobj_final.groupby(['HKDFIL2_KEY', 'OGR_KEY']).BEZUG.sum()
    df_IR_HKDFIL_OBJ = df_IR_HKDFIL_OBJ.reset_index(name = 'IST_IR_HKDFIL')
    df_filobj_final.drop(columns = ['IRxBEZ'], inplace = True)
    df_filobj_final = df_filobj_final.merge(df_IR_HKDFIL_OBJ, on = ['HKDFIL2_KEY', 'OGR_KEY'], how = 'left')
    
    df_filobj_final['IRxBEZ'] = df_filobj_final.ANZ_EH * df_filobj_final.AV_QUOTE
    df_IR_HKDFIL_OBJ = df_filobj_final.groupby(['HKDFIL2_KEY', 'OGR_KEY']).IRxBEZ.sum() / df_filobj_final.groupby(['HKDFIL2_KEY', 'OGR_KEY']).ANZ_EH.sum()
    df_IR_HKDFIL_OBJ = df_IR_HKDFIL_OBJ.reset_index(name = 'AV_QUOTE_HKDFIL')
    df_filobj_final.drop(columns = ['IRxBEZ'], inplace = True)
    df_filobj_final = df_filobj_final.merge(df_IR_HKDFIL_OBJ, on = ['HKDFIL2_KEY', 'OGR_KEY'], how = 'left')
    df_filobj_final['IRxBEZ'] = df_filobj_final.ANZ_EH * df_filobj_final.IST_AVQ
    df_IR_HKDFIL_OBJ = df_filobj_final.groupby(['HKDFIL2_KEY', 'OGR_KEY']).IRxBEZ.sum() / df_filobj_final.groupby(['HKDFIL2_KEY', 'OGR_KEY']).ANZ_EH.sum()
    df_IR_HKDFIL_OBJ = df_IR_HKDFIL_OBJ.reset_index(name = 'IST_AVQ_HKDFIL')
    df_filobj_final.drop(columns = ['IRxBEZ'], inplace = True)
    df_filobj_final = df_filobj_final.merge(df_IR_HKDFIL_OBJ, on = ['HKDFIL2_KEY', 'OGR_KEY'], how = 'left')    
    return df_filobj_final

def HKDFIL_OBJ_EXC(df):   
    df = df[~((df.HKDFIL2_KEY == 918003) & (df.OBJ_KEY == 920))].copy()    
    df = df[~((df.HKDFIL2_KEY == 918002) & (df.OBJ_KEY == 920))].copy()    
    return df





#*********************************************************************************************************
def create_performance_kpi_pair_dfs(df, df_targets=None, top_agg_level=['Product_Category', 'Product_Location'], bottom_agg_level=['Product'],year=2022):
    # df = data_daily
    # df_targets=data_targets_hkdfil 
    # top_agg_level=['OGR_KEY', 'HKDFIL2_KEY']
    # bottom_agg_level=['EH_KEY']

    '''Returns a top level and a bottom level dataframe with individual KPIs.
       The KPIs are based on the top-level targets.
       The bottom level KPIs sum up to to top level KPI.
       Additionaly, we calculated leave-one-out KPIs for bottom level.

       Requires a time-based dataframe with a bit of 
       nomenclature for the column names mapping:

           *Product - Bottom level aggretation columns.
           *Product_Category - Top level aggretation columns.
           *Product_Location - Top level aggretation columns.
           Time - Time unit.
           Stock - Excess stock at end of time point.
           Demand - Demand (sales plus lost sales) per time point.
           Sales - Sales per time point.
           Offer - Sales plus Stock at end of time point.
           Sellout - True if stock <= 0 at end of time point.
           Lost_sales - Demand minus sales per time point.
           Total_Revenue - Total revenue per time point.
           Lost_Revenue - Lost revenue per time point.

       It is also possible to pass df_targets with:

           *Product_Category - Top level aggretation columns.
           *Product_Location - Top level aggretation columns.
           Target_overstock_rate - A target for overstock.
           Target_sellout_rate - A target for sellout.

    '''

    # translate signature inputs to actual variables (old school and probably unnecessary)
    df = df
    df_targets = df_targets
    top_agg_level = top_agg_level
    bottom_agg_level = bottom_agg_level

    # set aggregation number of bottom level
    per_how_many_bottom_units_val = 0.1

    # aggregate per category
    df_cat_loc = df.groupby(by=top_agg_level).agg({'Lost_Revenue':'sum', 'Total_Revenue':'sum', 'Sales':'sum', 'Lost_sales':'sum', 'Stock':'sum', 'Demand':'sum', 'Offer':'sum', 'Time':'count', 'Sellout':'sum', bottom_agg_level[0]: 'nunique'}).reset_index()
    df_cat_loc.rename(columns={'Lost_Revenue': 'Cat_Lost_Revenue', 'Total_Revenue': 'Cat_Total_Revenue', 'Sales': 'Cat_Sales', 'Lost_sales': 'Cat_Lost_sales', 'Stock': 'Cat_Stock', 'Demand': 'Cat_Demand', 'Offer': 'Cat_Offer', 'Time': 'Cat_Days', 'Sellout': 'Cat_Sellout', bottom_agg_level[0]: 'Cat_Product'}, inplace=True)

    # calculate as-is
    df_cat_loc['Overstock_rate'] = df_cat_loc.Cat_Stock / df_cat_loc.Cat_Offer * 100
    df_cat_loc['Sellout_rate'] = df_cat_loc.Cat_Sellout / df_cat_loc.Cat_Days * 100

    # get targets from inputs
    df_cat_loc = df_cat_loc.merge(df_targets, on=top_agg_level, how='left')
    df_cat_loc['Cat_Target_overstock_rate'] = df_cat_loc.Target_overstock_rate
    df_cat_loc['Cat_Target_sellout_rate'] = df_cat_loc.Target_sellout_rate

    df_cat_loc['Sales_Lost_Sales_ratio'] = df_cat_loc.Cat_Sales / df_cat_loc.Cat_Lost_sales
    df_cat_loc.loc[df_cat_loc.Sales_Lost_Sales_ratio == np.inf, 'Sales_Lost_Sales_ratio'] = 1.0
    days_count = df.Time.drop_duplicates().count()
    df_avq = df.groupby(top_agg_level+['VGK']).agg({'EH_KEY': 'count','Sellout':'sum', 'AV_QUOTE_VGK2':'mean'}).reset_index()
    df_avq['AVQ_IST'] = df_avq.Sellout / df_avq.EH_KEY*100
    df_avq.rename(columns = {'EH_KEY': 'ANZ_EH'}, inplace = True)
    #df_avq.drop(columns = ['Sellout'], inplace = True)
    df_avq['AV_QUOTE_VGK2'] = df_avq['AV_QUOTE_VGK2'].round(1)
    df_avq['AVQ_IST'] = df_avq['AVQ_IST'].round(1)
    # #EV dazu
    df_EV = pd.read_excel('EV_pro_EH_new.xlsx')
    df_EV['AVQuote'] = df_EV['AVQuote'].round(1)
    df_avq['EV_soll'] = df_avq.apply(lambda x:  df_EV.loc[df_EV.AVQuote == x.AV_QUOTE_VGK2,f'EV_KL{int(x.VGK)}'].values[0] if pd.notna(x.AV_QUOTE_VGK2) else None , axis = 1)
    df_avq['EV_ist'] = df_avq.apply(lambda x:  df_EV.loc[df_EV.AVQuote == x.AVQ_IST,f'EV_KL{int(x.VGK)}'].values[0] , axis = 1)
    df_avq['EV_soll'] = df_avq['EV_soll'] * df_avq['ANZ_EH'] / days_count
    df_avq['EV_ist'] = df_avq['EV_ist'] * df_avq['ANZ_EH'] /days_count
    df_avq = df_avq.groupby(top_agg_level).agg({'EV_soll':'sum', 'EV_ist':'sum', 'ANZ_EH':'sum'}).reset_index()
    df_avq['ANZ_EH'] = df_avq['ANZ_EH'] / days_count
    df_cat_loc = df_cat_loc.merge(df_avq, on = top_agg_level, how = 'left')
    #add individual merginal sales, OBJ_GV_RQ_Q42021.xlsx must be calculated with "Mengeneinsatz" script
    df_GV = pd.read_excel('OBJ_GV_RQ_Q42021.xlsx')
    df_GV.rename(columns = {'RQ':'Overstock_rate'}, inplace = True)
    df_GV.drop(columns = ['Unnamed: 0'], inplace = True)
    if 'OBJ_KEY' in top_agg_level:
        df_cat_loc.sort_values(by = ['Overstock_rate', 'OBJ_KEY'], inplace = True)
        df_GV.sort_values(by = ['Overstock_rate', 'OBJ_KEY'], inplace = True)
        df_GV['OBJ_KEY'] = df_GV['OBJ_KEY'].astype('int64')
        df_cat_loc = pd.merge_asof(df_cat_loc,df_GV, on = ['Overstock_rate'], by = ['OBJ_KEY'])
    else:
        df_offer_obj = df.groupby(by = top_agg_level + ['OBJ_KEY'] ).agg({'Offer':'sum'}).reset_index()
        #df_GV['OGR_KEY'] = ogr_key #ogr_defined below
        df_GV = df_GV.merge(df_offer_obj, on = ['OBJ_KEY'], how = 'left')
        df_GV['GV'] = (df_GV['Offer']*df_GV['GV'])
        df_GV = (df_GV.groupby(top_agg_level+[ 'Overstock_rate']).GV.sum() / df_GV.groupby(top_agg_level+[ 'Overstock_rate']).Offer.sum().values).reset_index()
        df_cat_loc.sort_values(by = ['Overstock_rate']+top_agg_level, inplace = True)
        df_GV.sort_values(by = ['Overstock_rate']+top_agg_level, inplace = True)
        df_GV[top_agg_level] = df_GV[top_agg_level].astype('int64')
        df_cat_loc = pd.merge_asof(df_cat_loc,df_GV, on = ['Overstock_rate'], by = top_agg_level)
    def KPI_Top_level(per_how_many_bottom_units, cat_target_overstock, cat_target_sellout, stock, offer, total_revenue, products, sellouts, days, lost_revenue, EV_IST, EV_SOLL, ANZ_EH, GV):
        return (((stock ) - (cat_target_overstock / 100 * offer)) / (ANZ_EH * days_count  / 100) * -1 / GV + (((EV_IST) - (EV_SOLL)) / (ANZ_EH / 100) * -1) )

    # calculate KPI
    df_cat_loc['Cat_Loc_Performance'] = np.vectorize(KPI_Top_level)(per_how_many_bottom_units_val, df_cat_loc.Cat_Target_overstock_rate.values, df_cat_loc.Cat_Target_sellout_rate.values, df_cat_loc.Cat_Stock.values, df_cat_loc.Cat_Offer.values, df_cat_loc.Cat_Total_Revenue.values, df_cat_loc.Cat_Product.values, df_cat_loc.Cat_Sellout.values, df_cat_loc.Cat_Days.values, df_cat_loc.Cat_Lost_Revenue.values, df_cat_loc.EV_ist.values, df_cat_loc.EV_soll.values,df_cat_loc.ANZ_EH.values,df_cat_loc.GV.values )

    # formula for bottom level KPI
    def KPI_Bottom_level(per_how_many_bottom_units, sales_lost_sales_ration, cat_target_overstock, cat_target_sellout, stock, offer, total_revenue, products, sellouts, days, lost_revenue, EV_IST, EV_SOLL, ANZ_EH, GV, target_stock):
        return (((stock ) - (target_stock)) / ((ANZ_EH) * days_count  / 100) * -1 / GV + (((EV_IST) - (EV_SOLL)) / ((ANZ_EH) / 100) * -1) )
    ogr_select_string = df.OGR_KEY.iloc[0]
    #get IR_SATZ and AV_QUOTE per VGK
    conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=deaxsmapsql01.itservices.asudc.net,6200;'
                      'Database=ABLAGE;'
                      'Trusted_Connection=yes;')    
    sql = f"SELECT [OBJEKTGRUPPENNUMMER] AS OGR_KEY,[HAUPTKUNDENNUMMER] * 100 + [HAUPTKUNDENFILIALNUMMER] AS HKDFIL2_KEY,[OBJEKTNUMMER] AS OBJ_KEY, [VGK] as VGK, [TAU_KEY] as TAU_KEY, [IR_SATZ] AS IR_SATZ, [AV_QUOTE] AS AV_QUOTE, ZEITRAUM_GUELTIG_AB FROM [Regulierungsstatistik].[dbo].[TB_RISK_SOLLWERTE_TAU] WHERE ZEITRAUM_ABSCHNITT > 99 AND OBJEKTGRUPPENNUMMER IN ({ogr_select_string}) AND ZEITRAUM_TAGE IN (16) AND VGK >= 1 AND ZEITRAUM_GUELTIG_AB >= '2022-02-01 00:00:00' ORDER BY HKDFIL2_KEY ASC, VGK ASC, ZEITRAUM_GUELTIG_AB DESC"
    data_rqavq_monsat_vgk = pd.read_sql(sql, conn)
    data_rqavq_monsat_vgk.rename(columns={'ZEITRAUM_GUELTIG_AB':'Time', 'IR_SATZ': 'IR_SATZ_VGK', 'AV_QUOTE': 'AV_QUOTE_VGK'}, inplace=True)
    data_rqavq_monsat_vgk = adjust_old_ir_to_lean(data_rqavq_monsat_vgk,year)
    data_rqavq_monsat_vgk = data_rqavq_monsat_vgk.groupby(['OGR_KEY','HKDFIL2_KEY','OBJ_KEY', 'VGK','TAU_KEY','Time']).mean().reset_index()
    data_rqavq_monsat_vgk.sort_values(by=['Time', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','VGK','TAU_KEY'], inplace=True)    
    data_rqavq_monsat_vgk['Time'] = pd.to_datetime(data_rqavq_monsat_vgk['Time'])
    df['EVT'] = pd.to_datetime(df['Time'])
    #df['VGK'] = df['VGK'].astype('int64')
    df = pd.merge_asof(df, data_rqavq_monsat_vgk, on='Time', by = ['OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','VGK','TAU_KEY'])
    
    sql = f"SELECT [OBJEKTGRUPPENNUMMER] AS OGR_KEY,[HAUPTKUNDENNUMMER] * 100 + [HAUPTKUNDENFILIALNUMMER] AS HKDFIL2_KEY,[OBJEKTNUMMER] AS OBJ_KEY, [VGK] as VGK, [IR_SATZ] AS IR_SATZ, [AV_QUOTE] AS AV_QUOTE, ZEITRAUM_GUELTIG_AB FROM [Regulierungsstatistik].[dbo].[TB_RISK_SOLLWERTE] WHERE ZEITRAUM_ABSCHNITT > 99 AND OBJEKTGRUPPENNUMMER IN ({ogr_select_string}) AND ZEITRAUM_TAGE IN (16) AND VGK >= 1 AND ZEITRAUM_GUELTIG_AB >= '2018-01-01 00:00:00' ORDER BY HKDFIL2_KEY ASC, VGK ASC, ZEITRAUM_GUELTIG_AB DESC"
    data_rqavq_monsat_vgk = pd.read_sql(sql, conn)
    data_rqavq_monsat_vgk.rename(columns={'ZEITRAUM_GUELTIG_AB':'Time', 'IR_SATZ': 'IR_SATZ_VGK', 'AV_QUOTE': 'AV_QUOTE_VGK'}, inplace=True)
    data_rqavq_monsat_vgk = adjust_old_ir_to_lean(data_rqavq_monsat_vgk, year,tau = False)
    data_rqavq_monsat_vgk = data_rqavq_monsat_vgk.groupby(['OGR_KEY','HKDFIL2_KEY','OBJ_KEY', 'VGK','Time']).mean().reset_index()
    data_rqavq_monsat_vgk.sort_values(by=['Time', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','VGK'], inplace=True)    
    data_rqavq_monsat_vgk['Time'] = pd.to_datetime(data_rqavq_monsat_vgk['Time'])
    df_temp = df[df.IR_SATZ_VGK.isna()].drop(columns = ['IR_SATZ_VGK','AV_QUOTE_VGK'])
    df_temp = pd.merge_asof(df_temp, data_rqavq_monsat_vgk, on='Time', by = ['OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','VGK'])
    df = df[pd.notna(df.IR_SATZ_VGK)].append(df_temp).copy()
    
    # aggregate per product (each with a unique(!) location and category)
    df_products = df.groupby(by=bottom_agg_level+top_agg_level).agg({'Lost_Revenue':'sum', 'Total_Revenue':'sum', 'Lost_sales':'sum', 'Stock':'sum', 'Demand':'sum', 'Offer':'sum', 'Time':'count', 'Sellout':'sum', 'VGK': 'mean', 'AV_QUOTE_VGK': 'mean'}).reset_index().rename(columns={'Time':'Days', 'Stock':'Stock_EH', 'Offer': 'Offer_EH'})
    df_products['VGK'] = df_products['VGK'].round(0)
    df['IR_SATZ_VGK'] = df['Offer'] * df['IR_SATZ_VGK']
    df_IR_EH = (df.groupby(bottom_agg_level+top_agg_level)['IR_SATZ_VGK'].sum() / df.groupby(bottom_agg_level+top_agg_level)['Offer'].sum().values).reset_index()
    df_products = df_products.merge(df_IR_EH, on = bottom_agg_level+top_agg_level, how = 'left')
    
    # calculate as-is
    df_products['Overstock_rate'] = (df_products.Stock_EH / df_products.Offer_EH * 100)
    df_products['Sellout_rate'] = ((df_products.Sellout / df_products.Days) * 100).round(1)
    df_products['AV_QUOTE_VGK'] = df_products['AV_QUOTE_VGK'].round(1)
    df_products['EV_ist_eh'] = df_products.apply(lambda x:  df_EV.loc[df_EV.AVQuote == x.Sellout_rate,f'EV_KL{int(x.VGK)}'].values[0] , axis = 1)
    df_products['EV_soll_eh'] = df_products.apply(lambda x:  df_EV.loc[df_EV.AVQuote == x.AV_QUOTE_VGK,f'EV_KL{int(x.VGK)}'].values[0] if pd.notna(x.AV_QUOTE_VGK) else None , axis = 1)
    df_products['EV_ist_eh'] = df_products['EV_ist_eh'] * df_products['Days'] / days_count
    df_products['EV_soll_eh'] = df_products['EV_soll_eh'] * df_products['Days'] / days_count
    
    df_products = df_products.merge(df_cat_loc[top_agg_level+['GV','EV_ist','EV_soll', 'ANZ_EH','Sales_Lost_Sales_ratio', 'Cat_Target_overstock_rate', 'Cat_Target_sellout_rate', 'Cat_Loc_Performance', 'Cat_Lost_Revenue', 'Cat_Total_Revenue', 'Cat_Lost_sales', 'Cat_Stock', 'Cat_Demand', 'Cat_Offer', 'Cat_Days', 'Cat_Sellout', 'Cat_Product']], on=top_agg_level, how='left')
    
    #adjust lost sales so LS_HKDFIL_OBJ = SUM(LS_EH), important for SUM(SHOP_EFFECT) = RKZ
    df_adj = ((df_products.groupby(top_agg_level)['EV_ist'].mean() - df_products.groupby(top_agg_level)['EV_ist_eh'].sum().values)/df_products.groupby(top_agg_level)['EH_KEY'].count().values).reset_index()
    df_adj.rename(columns = {'EV_ist': 'adj'}, inplace = True)
    df_products = df_products.merge(df_adj, on = top_agg_level, how = 'left')
    df_products['EV_ist_eh'] = df_products['EV_ist_eh'] + df_products['adj']
    #adjust lost sales so LS_HKDFIL_OBJ = SUM(LS_EH), important for SUM(SHOP_EFFECT) = RKZ
    df_adj = ((df_products.groupby(top_agg_level)['EV_soll'].mean() - df_products.groupby(top_agg_level)['EV_soll_eh'].sum().values)/df_products.groupby(top_agg_level)['EH_KEY'].count().values).reset_index()
    df_adj.rename(columns = {'EV_soll': 'adj_soll'}, inplace = True)
    df_products = df_products.merge(df_adj, on = top_agg_level, how = 'left')
    df_products['EV_soll_eh'] = df_products['EV_soll_eh'] + df_products['adj_soll']
    df_products.drop(columns = ['adj_soll', 'adj'], inplace = True)
    #adjust Remi so Remi_HKDFIL_OBJ = SUM(Remi_EH), important for SUM(SHOP_EFFECT) = RKZ
    df_products['target_stock_eh'] = (df_products['IR_SATZ_VGK']/100*df_products['Offer_EH'])
    df_adj = (((df_products.groupby(top_agg_level)['Cat_Offer'].mean() * df_products.groupby(top_agg_level)['Cat_Target_overstock_rate'].mean().values / 100) - df_products.groupby(top_agg_level)['target_stock_eh'].sum().values)/df_products.groupby(top_agg_level)['EH_KEY'].count().values).reset_index()
    df_adj.rename(columns = {'Cat_Offer': 'adj_stock'}, inplace = True)
    df_products = df_products.merge(df_adj, on = top_agg_level, how = 'left')
    df_products['target_stock_eh'] = df_products['target_stock_eh'] + df_products['adj_stock']
    df_products.drop(columns = ['adj_stock'], inplace = True)
    
    df_products['EV_ist'] = df_products['EV_ist'] - df_products['EV_ist_eh']
    df_products['EV_soll'] = df_products['EV_soll'] - df_products['EV_soll_eh']
    df_products['Stock'] = df_products['Cat_Stock'] - df_products['Stock_EH']
    df_products['Offer'] = df_products['Cat_Offer'] - df_products['Offer_EH']
    df_products['target_stock'] = (df_products['Cat_Target_overstock_rate']/100*df_products['Cat_Offer']) - (df_products['target_stock_eh'])
    # the basic KPI
    print()
    df_products['Product_Performance'] = np.vectorize(KPI_Bottom_level)(per_how_many_bottom_units_val, df_products.Sales_Lost_Sales_ratio.values, df_products.Cat_Target_overstock_rate.values, df_products.Cat_Target_sellout_rate.values, df_products.Stock.values, df_products.Offer.values, df_products.Total_Revenue.values, df_products[bottom_agg_level[0]].values, df_products.Sellout.values, df_products.Days.values, df_products.Lost_Revenue.values, df_products.EV_ist.values, df_products.EV_soll.values,df_products.ANZ_EH.values,df_products.GV.values, df_products.target_stock.values)
    df_products['Product_Performance'] = df_products['Cat_Loc_Performance'] - df_products['Product_Performance']
    # get flop 20 per top aggregation level
    index_flop20 = df_products.groupby(by=top_agg_level)['Product_Performance'].nsmallest(20).index.get_level_values(len(top_agg_level))

    # add adjustment factor for flop 20 category performance
    df_cat_loc_final_check = df_products.loc[index_flop20].groupby(by=top_agg_level).agg({'Product_Performance':'sum'}).reset_index()
    df_cat_loc_final_check['Adjustment_Factor_Flop_20'] = df_cat_loc_final_check.Product_Performance / df_cat_loc.Cat_Loc_Performance
    df_products = df_products.merge(df_cat_loc_final_check[top_agg_level + ['Adjustment_Factor_Flop_20']], on=top_agg_level, how='left')

    df_cat_loc_final_check2 = df_products.groupby(by=top_agg_level).agg({'Product_Performance':'sum'}).reset_index()
    df_cat_loc_final_check2['Adjustment_Factor'] = df_cat_loc_final_check2.Product_Performance / df_cat_loc.Cat_Loc_Performance
    df_products = df_products.merge(df_cat_loc_final_check2[top_agg_level + ['Adjustment_Factor']], on=top_agg_level, how='left')

    # calculate final performance
    df_products['Product_Performance_Adjusted_Flop_20'] = df_products.Product_Performance / df_products.Adjustment_Factor_Flop_20
    df_products['Product_Performance_Adjusted'] = df_products.Product_Performance / df_products.Adjustment_Factor
    df_products['Product_Performance_Plain'] = df_products.Product_Performance
    df_products['Product_Performance_Plain'] = (df_products['Product_Performance_Plain']-min(df_products['Product_Performance_Plain']))/(max(df_products['Product_Performance_Plain'])-min(df_products['Product_Performance_Plain']))

    # save flop 20 with three different bottom level performances
    df_products_flop20 = df_products.loc[index_flop20].copy()

    df_cat_loc['Created_on'] = pd.Timestamp('now')
    df_cat_loc.Cat_Loc_Performance = df_cat_loc.Cat_Loc_Performance.round(2)

    df_products['Created_on'] = pd.Timestamp('now')

    return df_cat_loc, df_products.drop(columns=['Product_Performance_Adjusted_Flop_20']), df_products_flop20
#************************************************************************************************************
@teams_sender("https://moveoffice.webhook.office.com/webhookb2/7da63796-0ef6-4bac-96ec-c20c13e9f787@a1e7a36c-6a48-4768-9d65-3f679c0f3b12/IncomingWebhook/47622c72f9374201ac502814deea630b/8e2cd2bf-a335-46ef-831f-83a01836ee67")

def run_RKZ(data_selection_for_year, month_number, ogr_key, calculate_vgk_flag = True, current_overall_overstock_rate = 31.5, shop_exception = True):

    data_selection_for_year = data_selection_for_year # int
    year=data_selection_for_year
    month_number_string = str(month_number)
    ogr_select_string = str(ogr_key) # string
    calculate_vgk_flag = calculate_vgk_flag
    current_overall_overstock_rate = current_overall_overstock_rate

    # try:
    #     hkdfil_param_string
    #     create_full_pdf = False
    # except:
    #     create_full_pdf = True

    # if create_full_pdf:
    sql_hkdfil_selection_string = ''
# else:
#     sql_hkdfil_selection_string = "AND VK.HKDFIL2_KEY IN (" + hkdfil_param_string + ") "


    conn = pyodbc.connect('Driver={SQL Server};'
                          'Server=deaxsmapsql01.itservices.asudc.net,6200;'
                          'Database=ABLAGE;'
                          'Trusted_Connection=yes;')
    cursor = conn.cursor()


    # if create_full_pdf:
    sql_lookup_selection_string = ''
    # else:
    #     sql_lookup_selection_string = "AND HKD.HKDFIL2_KEY IN (" + hkdfil_param_string + ") "

    sql = "CREATE TABLE #TB_RKZ_LOOKUP_TMP(OGR_KEY int, HKDFIL_KEY int, OBJ_KEY int, EH_KEY int, actual_VD float)"
    cursor.execute(sql)
    conn.commit()

    sql = "INSERT INTO #TB_RKZ_LOOKUP_TMP(OGR_KEY, HKDFIL_KEY, OBJ_KEY, EH_KEY, actual_VD) SELECT VKK.OGR_KEY, HKD.HKDFIL2_KEY AS HKDFIL_KEY, VKK.OBJ_KEY, VKK.EH_KEY, CAST(SUM(VKK.BEZUG-VKK.REMI) AS FLOAT) / CAST(COUNT(VKK.ENR) AS FLOAT) AS actual_VD FROM [ABLAGE].[eh].[TB_VERKAUF_MARS] AS VKK INNER JOIN [ANWENDUNG].[kpi].[TB_EH_S] AS HKD ON VKK.EH_KEY = HKD.EH_KEY WHERE VKK.EJAHR = " + str(data_selection_for_year) + " AND VKK.KALMO IN (" + month_number_string + ") AND VKK.OGR_KEY IN (" + ogr_select_string + ") AND HKDFIL2_KEY <> -1 " + sql_lookup_selection_string + "GROUP BY VKK.OGR_KEY, HKD.HKDFIL2_KEY, VKK.OBJ_KEY, VKK.EH_KEY"
    cursor.execute(sql)
    conn.commit()

    # VGK -1 and all subsequent VGKs for BILD
    bild_VGK_Intervall = [ [-1,99999], [-1,3], [3,6], [6,9] , [9,12], [12,15], [15,20], [20,25], [25,50], [50,70], [70,100], [100,999]]
    bild_ind = [-1] + list(range(1,12))


    data_daily = pd.DataFrame()

    for thresholds, vgk in zip(bild_VGK_Intervall, bild_ind):

            if vgk == -1:
                continue

            sql = "SELECT VK.EJAHR, VK.KALMO, VK.OGR_KEY, VK.HKDFIL2_KEY AS HKDFIL2_KEY, VK.OBJ_KEY, VK.TAU_KEY, VK.EH_KEY, VK.EVT, VK.KALWT - 1 AS WEEKDAY, VK.BEZUG, VK.REMI, VK.BEZUG-VK.REMI AS VERKAUF, HKD.DAT_LB_SO AS DELI_SINCE_DATE, HKD.GA_KEY AS GESA FROM [ABLAGE].[eh].[vwSR_VERKAUF_MARS] AS VK INNER JOIN [ANWENDUNG].[kpi].[TB_EH_S] AS HKD ON VK.EH_KEY = HKD.EH_KEY INNER JOIN (SELECT OBJ_KEY, EH_KEY FROM #TB_RKZ_LOOKUP_TMP WHERE actual_VD >= " + str(thresholds[0]) + " and actual_VD < " + str(thresholds[1]) + ")a ON a.OBJ_KEY = VK.OBJ_KEY AND a.EH_KEY = VK.EH_KEY WHERE VK.EVT >= 20210412 AND VK.EJAHR = " + str(data_selection_for_year) + " AND VK.KALMO IN (" + month_number_string + ") AND VK.OGR_KEY IN (" + ogr_select_string + ") AND VK.HKDFIL2_KEY <> -1 " + sql_hkdfil_selection_string +  " ORDER BY VK.EJAHR, VK.KALMO, VK.OGR_KEY, VK.HKDFIL2_KEY, VK.OBJ_KEY, VK.EH_KEY, VK.EVT"
            data_daily_vgk = pd.read_sql(sql, conn)
            #TAUs anpassen
            data_daily_vgk['VGK'] = vgk

            if data_daily.empty:
                data_daily = data_daily_vgk.copy()
            else:
                data_daily = data_daily.append(data_daily_vgk, sort=False)
                
    #data_daily.loc[data_daily.HKDFIL2_KEY == 123400, 'HKDFIL2_KEY'] = 106600
    data_daily['HKD'] = np.floor(data_daily.HKDFIL2_KEY / 100).astype('int64')
    data_daily['EVT'] = pd.to_datetime(data_daily.EVT, format='%Y%m%d')
    

    # financial figures
    revenue_per_copy = 0.659
    cost_per_copy = 0.065
    
    #exclude some shops
    if shop_exception:
        data_daily = get_exceptional_retailers_and_remove_from_df(data_daily,data_selection_for_year,month_number)
    #return data_daily
    
    # lost sales
    lost_sales = pd.read_feather('Inventory_Simulation_V1.feather')
    lost_sales.columns = ['EH_KEY', 'WEEKDAY', 'SAFETY_STOCK', 'AVG_LOST_SALES',
           'AVG_BEZUG', 'AVG_SERVICE_LEVEL', 'TARGET_RQ', 'VERKAUF', 'CALC_BEZUG',
           'CALC_RQ', 'HKDFIL2_KEY']
    lost_sales.AVG_LOST_SALES = lost_sales.AVG_LOST_SALES * lost_sales.AVG_SERVICE_LEVEL / ((revenue_per_copy - cost_per_copy) / (revenue_per_copy - cost_per_copy + cost_per_copy))
    lost_sales = lost_sales[['EH_KEY', 'WEEKDAY', 'AVG_LOST_SALES']].sort_values(by=['EH_KEY', 'WEEKDAY'])
    data_daily = data_daily.merge(lost_sales, on=['EH_KEY', 'WEEKDAY'], how='left')
    data_daily.AVG_LOST_SALES.fillna(0, inplace=True) # some 2k retailer are not in the data
    data_daily.rename(columns={'AVG_LOST_SALES':'EV'}, inplace=True)
        
    data_daily['Demand'] = data_daily.VERKAUF + data_daily.EV
    data_daily['AVK'] = data_daily.REMI == 0
    data_daily['Total_Revenue'] = data_daily.VERKAUF * 1
    data_daily['Lost_Revenue'] = data_daily.EV * 1

    # match valid targets to daily data VGK
    data_daily = adjust_mars_tau_to_vis_tau(data_daily)    
    data_daily = data_daily.groupby(['HKDFIL2_KEY', 'OBJ_KEY', 'WEEKDAY']).apply(lambda x: adjust_mars_tau_to_vis_tau(x))
    #data_daily.reset_index(drop = True, inplace = True)#*******change
    sql = f"SELECT [OBJEKTGRUPPENNUMMER] AS OGR_KEY,[HAUPTKUNDENNUMMER] * 100 + [HAUPTKUNDENFILIALNUMMER] AS HKDFIL2_KEY,[OBJEKTNUMMER] AS OBJ_KEY, [TAU_KEY] as TAU_KEY, VGK, [IR_SATZ] AS IR_SATZ, [AV_QUOTE] AS AV_QUOTE, ZEITRAUM_GUELTIG_AB, ZEITRAUM_TAGE, ZEITRAUM_JAHR FROM [Regulierungsstatistik].[dbo].[TB_RISK_SOLLWERTE_TAU] WHERE ZEITRAUM_ABSCHNITT > 99 AND OBJEKTGRUPPENNUMMER IN ({ogr_select_string}) AND ZEITRAUM_TAGE IN (16)  AND ZEITRAUM_GUELTIG_AB >= '2022-02-01 00:00:00' ORDER BY HKDFIL2_KEY ASC, ZEITRAUM_GUELTIG_AB DESC"
    data_rqavq_monsat = pd.read_sql(sql, conn)
    data_rqavq_monsat.ZEITRAUM_TAGE = data_rqavq_monsat.ZEITRAUM_TAGE.astype('int64')
    data_rqavq_monsat.rename(columns={'ZEITRAUM_GUELTIG_AB':'EVT'}, inplace=True)
    data_rqavq_monsat = adjust_old_ir_to_lean(data_rqavq_monsat,year)
    data_rqavq_monsat = data_rqavq_monsat.groupby(['OGR_KEY','HKDFIL2_KEY','OBJ_KEY','TAU_KEY', 'VGK','EVT','ZEITRAUM_TAGE','ZEITRAUM_JAHR']).mean().reset_index()
    data_rqavq_monsat.sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY', 'VGK'], inplace=True)
    data_daily.sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY', 'VGK'], inplace=True)

    data_rqavq_monsat['EVT'] = pd.to_datetime(data_rqavq_monsat['EVT'])
    data_daily['EVT'] = pd.to_datetime(data_daily['EVT'])
    data_rqavq_monsat.rename(columns = {'IR_SATZ': 'IR_SATZ_VGK2', 'AV_QUOTE': 'AV_QUOTE_VGK2'}, inplace = True)
    #data_rqavq_monsat.reset_index(drop = True, inplace = True)
    data_daily = pd.merge_asof(data_daily, data_rqavq_monsat, on='EVT', by=['OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY', 'VGK'])

    sql = f"SELECT [OBJEKTGRUPPENNUMMER] AS OGR_KEY,[HAUPTKUNDENNUMMER] * 100 + [HAUPTKUNDENFILIALNUMMER] AS HKDFIL2_KEY,[OBJEKTNUMMER] AS OBJ_KEY, VGK, [IR_SATZ] AS IR_SATZ, [AV_QUOTE] AS AV_QUOTE, ZEITRAUM_GUELTIG_AB, ZEITRAUM_TAGE, ZEITRAUM_JAHR FROM [Regulierungsstatistik].[dbo].[TB_RISK_SOLLWERTE] WHERE ZEITRAUM_ABSCHNITT > 99 AND OBJEKTGRUPPENNUMMER IN ({ogr_select_string}) AND ZEITRAUM_TAGE IN (16)  AND ZEITRAUM_GUELTIG_AB >= '2018-01-01 00:00:00' ORDER BY HKDFIL2_KEY ASC, ZEITRAUM_GUELTIG_AB DESC"
    data_rqavq_monsat = pd.read_sql(sql, conn)
    data_rqavq_monsat.ZEITRAUM_TAGE = data_rqavq_monsat.ZEITRAUM_TAGE.astype('int64')
    data_rqavq_monsat.rename(columns={'ZEITRAUM_GUELTIG_AB':'EVT'}, inplace=True)
    data_rqavq_monsat = adjust_old_ir_to_lean(data_rqavq_monsat,year, tau = False)
    data_rqavq_monsat = data_rqavq_monsat.groupby(['OGR_KEY','HKDFIL2_KEY','OBJ_KEY', 'VGK','EVT','ZEITRAUM_TAGE','ZEITRAUM_JAHR']).mean().reset_index()
    data_rqavq_monsat.sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY', 'VGK'], inplace=True)
    df = data_daily[data_daily.IR_SATZ_VGK2.isna()].sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY', 'VGK'])    
    df.drop(columns = ['IR_SATZ_VGK2','AV_QUOTE_VGK2','ZEITRAUM_TAGE','ZEITRAUM_JAHR' ], inplace = True)
    data_rqavq_monsat['EVT'] = pd.to_datetime(data_rqavq_monsat['EVT'])
    data_rqavq_monsat.rename(columns = {'IR_SATZ': 'IR_SATZ_VGK2', 'AV_QUOTE': 'AV_QUOTE_VGK2'}, inplace = True)
    df = pd.merge_asof(df, data_rqavq_monsat, on='EVT', by=['OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY', 'VGK'])
    data_daily = data_daily[pd.notna(data_daily.IR_SATZ_VGK2)].append(df).copy()
    data_daily.sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY', 'VGK'], inplace=True)
    #data_daily.rename(columns={'EVT':'Time', 'REMI':'Stock', 'VERKAUF':'Sales', 'BEZUG':'Offer', 'AVK':'Sellout', 'EV':'Lost_sales'}, inplace=True)

    # match valid targets to daily data
    data_daily = adjust_mars_tau_to_vis_tau(data_daily)
    sql = f"SELECT [OBJEKTGRUPPENNUMMER] AS OGR_KEY,[HAUPTKUNDENNUMMER] * 100 + [HAUPTKUNDENFILIALNUMMER] AS HKDFIL2_KEY,[OBJEKTNUMMER] AS OBJ_KEY, [TAU_KEY] as TAU_KEY, [IR_SATZ] AS IR_SATZ, [AV_QUOTE] AS AV_QUOTE, ZEITRAUM_GUELTIG_AB, ZEITRAUM_TAGE, ZEITRAUM_JAHR FROM [Regulierungsstatistik].[dbo].[TB_RISK_SOLLWERTE_TAU] WHERE ZEITRAUM_ABSCHNITT > 99 AND OBJEKTGRUPPENNUMMER IN ({ogr_select_string}) AND VGK = -1 AND ZEITRAUM_TAGE IN (16)  AND ZEITRAUM_GUELTIG_AB >= '2022-02-01 00:00:00' ORDER BY HKDFIL2_KEY ASC, ZEITRAUM_GUELTIG_AB DESC"
    data_rqavq_monsat = pd.read_sql(sql, conn)
    data_rqavq_monsat.ZEITRAUM_TAGE = data_rqavq_monsat.ZEITRAUM_TAGE.astype('int64')
    data_rqavq_monsat.rename(columns={'ZEITRAUM_GUELTIG_AB':'EVT'}, inplace=True)
    data_rqavq_monsat = adjust_old_ir_to_lean(data_rqavq_monsat,year)
    data_rqavq_monsat = data_rqavq_monsat.groupby(['OGR_KEY','HKDFIL2_KEY','OBJ_KEY','TAU_KEY', 'EVT','ZEITRAUM_TAGE','ZEITRAUM_JAHR']).mean().reset_index()
    data_rqavq_monsat.sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY'], inplace=True)
    data_daily.sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY'], inplace=True)

    data_rqavq_monsat['EVT'] = pd.to_datetime(data_rqavq_monsat['EVT'])
    data_daily['EVT'] = pd.to_datetime(data_daily['EVT'])
    data_daily = pd.merge_asof(data_daily, data_rqavq_monsat, on='EVT', by=['OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY'])

    sql = f"SELECT [OBJEKTGRUPPENNUMMER] AS OGR_KEY,[HAUPTKUNDENNUMMER] * 100 + [HAUPTKUNDENFILIALNUMMER] AS HKDFIL2_KEY,[OBJEKTNUMMER] AS OBJ_KEY, [IR_SATZ] AS IR_SATZ, [AV_QUOTE] AS AV_QUOTE, ZEITRAUM_GUELTIG_AB, ZEITRAUM_TAGE, ZEITRAUM_JAHR FROM [Regulierungsstatistik].[dbo].[TB_RISK_SOLLWERTE] WHERE ZEITRAUM_ABSCHNITT > 99 AND OBJEKTGRUPPENNUMMER IN ({ogr_select_string}) AND ZEITRAUM_TAGE IN (16) AND VGK = -1  AND ZEITRAUM_GUELTIG_AB >= '2018-01-01 00:00:00' ORDER BY HKDFIL2_KEY ASC, ZEITRAUM_GUELTIG_AB DESC"
    data_rqavq_monsat = pd.read_sql(sql, conn)
    data_rqavq_monsat.ZEITRAUM_TAGE = data_rqavq_monsat.ZEITRAUM_TAGE.astype('int64')
    data_rqavq_monsat.rename(columns={'ZEITRAUM_GUELTIG_AB':'EVT'}, inplace=True)
    data_rqavq_monsat = adjust_old_ir_to_lean(data_rqavq_monsat,year, tau = False)
    data_rqavq_monsat = data_rqavq_monsat.groupby(['OGR_KEY','HKDFIL2_KEY','OBJ_KEY', 'EVT','ZEITRAUM_TAGE','ZEITRAUM_JAHR']).mean().reset_index()
    data_rqavq_monsat.sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY'], inplace=True)
    df = data_daily[data_daily.IR_SATZ.isna()].sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY'])    
    df.drop(columns = ['IR_SATZ','AV_QUOTE' ], inplace = True)
    data_rqavq_monsat['EVT'] = pd.to_datetime(data_rqavq_monsat['EVT'])
    df = pd.merge_asof(df, data_rqavq_monsat, on='EVT', by=['OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY'])
    data_daily = data_daily[pd.notna(data_daily.IR_SATZ)].append(df).copy()
    data_daily.sort_values(by=['EVT', 'OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY'], inplace=True)
    data_daily.rename(columns={'EVT':'Time', 'REMI':'Stock', 'VERKAUF':'Sales', 'BEZUG':'Offer', 'AVK':'Sellout', 'EV':'Lost_sales'}, inplace=True)
    
    
    # also need to aggregate for changing targets within a month    
    data_targets = data_daily[['OGR_KEY', 'HKD', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY', 'Offer', 'EH_KEY', 'IR_SATZ', 'AV_QUOTE']].copy()
    data_targets_weighting = data_targets.groupby(['OGR_KEY', 'HKD', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY']).agg({ 'Offer': 'sum', 'EH_KEY':'count'}).reset_index().rename(columns={'Offer':'Sum_Offer', 'EH_KEY':'Count_EH_KEY'})
    data_targets = data_targets.merge(data_targets_weighting, on=['OGR_KEY', 'HKD', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY'], how='left')
    data_targets['IR_SATZ'] = data_targets.IR_SATZ * (data_targets.Offer / data_targets.Sum_Offer)
    data_targets['AV_QUOTE'] = data_targets.AV_QUOTE * (1 / data_targets.Count_EH_KEY)
    data_targets = data_targets.groupby(['OGR_KEY', 'HKD', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY']).agg({ 'IR_SATZ': 'sum', 'AV_QUOTE': 'sum'}).reset_index()
    data_targets.rename(columns={'IR_SATZ': 'Target_overstock_rate', 'AV_QUOTE': 'Target_sellout_rate'}, inplace=True)
    data_targets

    # Calculate for HKDFIL-OBJ-TAU
    #return data_daily
    df_filobj_tau, df_shops_adjusted_to_filobj_tau, df_shops_adjusted_to_filobj_tau_flop20 = create_performance_kpi_pair_dfs(data_daily, df_targets=data_targets, top_agg_level=['OGR_KEY', 'HKD', 'HKDFIL2_KEY', 'OBJ_KEY','TAU_KEY'], bottom_agg_level=['EH_KEY'],year=year)

    # View results

    df_filobj_tau.rename(columns={'Cat_Loc_Performance':'RKZ_HKDFIL_OBJ_TAU'}, inplace=True)
    df_filobj_tau[['OGR_KEY', 'RKZ_HKDFIL_OBJ_TAU']]

    df_filobj_tau.RKZ_HKDFIL_OBJ_TAU.min()

    df_filobj_tau.RKZ_HKDFIL_OBJ_TAU.mean()

    df_filobj_tau.RKZ_HKDFIL_OBJ_TAU.max()

    # favorite(!) performance measure, but have a few others in df too
    df_shops_adjusted_to_filobj_tau_flop20.rename(columns={'Product_Performance_Adjusted':'RKZ'}, inplace=True)
    df_shops_adjusted_to_filobj_tau_flop20.RKZ
    
    # Special version for HKDFIL-OBJ

    data_targets_ogr = data_daily[['OGR_KEY','HKD', 'HKDFIL2_KEY', 'OBJ_KEY', 'Offer', 'EH_KEY', 'IR_SATZ', 'AV_QUOTE']].copy()
    data_targets_ogr_weighting = data_targets_ogr.groupby(['OGR_KEY','HKD', 'HKDFIL2_KEY', 'OBJ_KEY']).agg({ 'Offer': 'sum', 'EH_KEY':'count'}).reset_index().rename(columns={'Offer':'Sum_Offer', 'EH_KEY':'Count_EH_KEY'})
    data_targets_ogr = data_targets_ogr.merge(data_targets_ogr_weighting, on=['OGR_KEY','HKD', 'HKDFIL2_KEY', 'OBJ_KEY'], how='left')
    data_targets_ogr['IR_SATZ'] = data_targets_ogr.IR_SATZ * (data_targets_ogr.Offer / data_targets_ogr.Sum_Offer)
    data_targets_ogr['AV_QUOTE'] = data_targets_ogr.AV_QUOTE * (1 / data_targets_ogr.Count_EH_KEY)
    data_targets_ogr = data_targets_ogr.groupby(['OGR_KEY','HKD', 'HKDFIL2_KEY', 'OBJ_KEY']).agg({ 'IR_SATZ': 'sum', 'AV_QUOTE': 'sum'}).reset_index()
    data_targets_ogr.rename(columns={'IR_SATZ': 'Target_overstock_rate', 'AV_QUOTE': 'Target_sellout_rate'}, inplace=True)
    data_targets_ogr

    df_filobj, df_shops_adjusted_to_filobj, df_shops_adjusted_to_filobj_flop20 = create_performance_kpi_pair_dfs(data_daily, df_targets=data_targets_ogr, top_agg_level=['OGR_KEY', 'HKD', 'HKDFIL2_KEY', 'OBJ_KEY'], bottom_agg_level=['EH_KEY'],year=year)

    df_filobj.rename(columns={'Cat_Loc_Performance':'RKZ_HKDFIL_OBJ'}, inplace=True)
    df_filobj[['OGR_KEY', 'RKZ_HKDFIL_OBJ']]

    # Special version for OGR

    data_targets_ogr = data_daily[['OGR_KEY', 'Offer', 'EH_KEY', 'IR_SATZ', 'AV_QUOTE']].copy()
    data_targets_ogr_weighting = data_targets_ogr.groupby(['OGR_KEY']).agg({ 'Offer': 'sum', 'EH_KEY':'count'}).reset_index().rename(columns={'Offer':'Sum_Offer', 'EH_KEY':'Count_EH_KEY'})
    data_targets_ogr = data_targets_ogr.merge(data_targets_ogr_weighting, on=['OGR_KEY'], how='left')
    data_targets_ogr['IR_SATZ'] = data_targets_ogr.IR_SATZ * (data_targets_ogr.Offer / data_targets_ogr.Sum_Offer)
    data_targets_ogr['AV_QUOTE'] = data_targets_ogr.AV_QUOTE * (1 / data_targets_ogr.Count_EH_KEY)
    data_targets_ogr = data_targets_ogr.groupby(['OGR_KEY']).agg({ 'IR_SATZ': 'sum', 'AV_QUOTE': 'sum'}).reset_index()
    data_targets_ogr.rename(columns={'IR_SATZ': 'Target_overstock_rate', 'AV_QUOTE': 'Target_sellout_rate'}, inplace=True)
    data_targets_ogr.at[0, 'Target_overstock_rate'] = current_overall_overstock_rate # overwrite with correct remission quota aka Target_overstock_rate
    data_targets_ogr

    df_ogr, df_shops_adjusted_to_ogr, df_shops_adjusted_to_ogr_flop20 = create_performance_kpi_pair_dfs(data_daily, df_targets=data_targets_ogr, top_agg_level=['OGR_KEY'], bottom_agg_level=['EH_KEY'],year=year)

    df_ogr.rename(columns={'Cat_Loc_Performance':'RKZ_OGR'}, inplace=True)
    df_ogr[['OGR_KEY', 'RKZ_OGR']]

    # Special version for HKD

    data_targets_hkd = data_daily[['OGR_KEY', 'HKD', 'Offer', 'EH_KEY', 'IR_SATZ', 'AV_QUOTE']].copy()
    data_targets_hkd_weighting = data_targets_hkd.groupby(['OGR_KEY', 'HKD']).agg({ 'Offer': 'sum', 'EH_KEY':'count'}).reset_index().rename(columns={'Offer':'Sum_Offer', 'EH_KEY':'Count_EH_KEY'})
    data_targets_hkd = data_targets_hkd.merge(data_targets_hkd_weighting, on=['OGR_KEY', 'HKD'], how='left')
    data_targets_hkd['IR_SATZ'] = data_targets_hkd.IR_SATZ * (data_targets_hkd.Offer / data_targets_hkd.Sum_Offer)
    data_targets_hkd['AV_QUOTE'] = data_targets_hkd.AV_QUOTE * (1 / data_targets_hkd.Count_EH_KEY)
    data_targets_hkd = data_targets_hkd.groupby(['OGR_KEY', 'HKD']).agg({ 'IR_SATZ': 'sum', 'AV_QUOTE': 'sum'}).reset_index()
    data_targets_hkd.rename(columns={'IR_SATZ': 'Target_overstock_rate', 'AV_QUOTE': 'Target_sellout_rate'}, inplace=True)
    data_targets_hkd

    df_hkd, df_shops_adjusted_to_hkd, df_shops_adjusted_to_hkd_flop20 = create_performance_kpi_pair_dfs(data_daily, df_targets=data_targets_hkd, top_agg_level=['OGR_KEY', 'HKD'], bottom_agg_level=['EH_KEY'],year=year)

    df_hkd.rename(columns={'Cat_Loc_Performance':'RKZ_HKD'}, inplace=True)
    df_hkd[['HKD', 'RKZ_HKD']]

    # Special version for HKDFIL

    data_targets_hkdfil = data_daily[['OGR_KEY', 'HKDFIL2_KEY', 'OBJ_KEY', 'Offer', 'EH_KEY', 'IR_SATZ', 'AV_QUOTE']].copy()
    data_targets_hkdfil_weighting = data_targets_hkdfil.groupby(['OGR_KEY', 'HKDFIL2_KEY']).agg({ 'Offer': 'sum', 'EH_KEY':'count'}).reset_index().rename(columns={'Offer':'Sum_Offer', 'EH_KEY':'Count_EH_KEY'})
    data_targets_hkdfil = data_targets_hkdfil.merge(data_targets_hkdfil_weighting, on=['OGR_KEY', 'HKDFIL2_KEY'], how='left')
    data_targets_hkdfil['IR_SATZ'] = data_targets_hkdfil.IR_SATZ * (data_targets_hkdfil.Offer / data_targets_hkdfil.Sum_Offer)
    data_targets_hkdfil['AV_QUOTE'] = data_targets_hkdfil.AV_QUOTE * (1 / data_targets_hkdfil.Count_EH_KEY)
    data_targets_hkdfil = data_targets_hkdfil.groupby(['OGR_KEY', 'HKDFIL2_KEY']).agg({ 'IR_SATZ': 'sum', 'AV_QUOTE': 'sum'}).reset_index()
    data_targets_hkdfil.rename(columns={'IR_SATZ': 'Target_overstock_rate', 'AV_QUOTE': 'Target_sellout_rate'}, inplace=True)
    data_targets_hkdfil

    df_hkdfil, df_shops_adjusted_to_hkdfil, df_shops_adjusted_to_hkdfil_flop20 = create_performance_kpi_pair_dfs(data_daily, df_targets=data_targets_hkdfil, top_agg_level=['OGR_KEY', 'HKDFIL2_KEY'], bottom_agg_level=['EH_KEY'],year=year)

    df_hkdfil.rename(columns={'Cat_Loc_Performance':'RKZ_HKDFIL'}, inplace=True)
    df_hkdfil[['HKDFIL2_KEY', 'RKZ_HKDFIL']]

    # Persist results df_filobj_tau
    df_filobj_final = df_filobj_tau.merge(df_filobj[['HKDFIL2_KEY', 'OBJ_KEY', 'RKZ_HKDFIL_OBJ']], on=['HKDFIL2_KEY', 'OBJ_KEY'], how='left').copy()
    df_filobj_final = df_filobj_final.merge(df_ogr[['OGR_KEY', 'RKZ_OGR']], on=['OGR_KEY'], how='left')
    df_filobj_final = df_filobj_final.merge(df_hkd[['HKD', 'RKZ_HKD']], on=['HKD'], how='left')
    df_filobj_final = df_filobj_final.merge(df_hkdfil[['HKDFIL2_KEY', 'RKZ_HKDFIL']], on=['HKDFIL2_KEY'], how='left').copy()
    df_filobj_final['KALMO'] = int(month_number_string) # add month
    df_filobj_final['EJAHR'] = int(data_selection_for_year) # add year

    # change order of columns
    df_filobj_final = df_filobj_final[['EJAHR', 'KALMO', 'OGR_KEY',
     'HKD',
     'HKDFIL2_KEY',
     'OBJ_KEY',
     'Cat_Sales',
     'Cat_Lost_sales',
     'Cat_Stock',
     'Cat_Demand',
     'Cat_Offer',
     'Cat_Days',
     'Cat_Sellout',
     'Cat_Product',
     'Overstock_rate',
     'Sellout_rate',
     'Cat_Target_overstock_rate',
     'Cat_Target_sellout_rate',
     'Sales_Lost_Sales_ratio',
     'Cat_Total_Revenue',
     'Cat_Lost_Revenue',
     'RKZ_OGR',
     'RKZ_HKD',
     'RKZ_HKDFIL',
     'RKZ_HKDFIL_OBJ',
     'Created_on',    
     'RKZ_HKDFIL_OBJ_TAU', 
      'TAU_KEY' ]].copy()

    # rename columns
    df_filobj_final.rename(columns={'Cat_Sales': 'VERKAUF', 'Cat_Lost_sales': 'EV', 'Cat_Stock': 'REMI', 'Cat_Demand': 'd', 'Cat_Offer':'BEZUG', 'Cat_Days':'ANZ_EVT', 'Cat_Sellout':'AVK', 'Cat_Product':'ANZ_EH', 'Overstock_rate':'IST_RQ', 'Sellout_rate':'IST_AVQ', 'Cat_Target_overstock_rate':'IR_SATZ', 'Cat_Target_sellout_rate':'AV_QUOTE', 'Sales_Lost_Sales_ratio': 'GV', 'Cat_Lost_Revenue': 'EV_EUR', 'Cat_Total_Revenue':'UMSATZ_EUR'}, inplace=True)

    # round and change dtype
    df_filobj_final.IST_RQ = df_filobj_final.IST_RQ.round(2)
    df_filobj_final.IST_AVQ = df_filobj_final.IST_AVQ.round(2)
    df_filobj_final.IR_SATZ = df_filobj_final.IR_SATZ.round(2)
    df_filobj_final.AV_QUOTE = df_filobj_final.AV_QUOTE.round(2)
    df_filobj_final.GV = df_filobj_final.GV.round(2)
    df_filobj_final.EV_EUR = df_filobj_final.EV_EUR.astype('int64')
    df_filobj_final.EV = df_filobj_final.EV.astype('int64')
    df_filobj_final.d = df_filobj_final.d.astype('int64')

    # magic with sqlalchemy
    engine = sqlalchemy.create_engine('mssql://deaxsmapsql01.itservices.asudc.net,6200/Regulierungsstatistik?trusted_connection=yes&driver=SQL+Server', fast_executemany=True)

    # persist
    if shop_exception:
        table_name_suff = ''
    else:
        table_name_suff = '_BRUTTO'
    df_filobj_final = HKDFIL_OBJ_EXC(df_filobj_final)
    df_filobj_final = IR_HKDFIL(df_filobj_final)     
    df_filobj_final.to_sql(name='TB_RKZ_NEU_HKDFIL_OBJ'+table_name_suff, schema='dbo', con=engine, index=False, method='multi', chunksize=int(round(2100/df_filobj_final.shape[1]-1)), if_exists='append')
        
    df_shops_adjusted_to_filobj = df_shops_adjusted_to_filobj_tau[['OGR_KEY', 'HKD', 'HKDFIL2_KEY', 'OBJ_KEY', 'EH_KEY', 'Overstock_rate', 'Sellout_rate', 'Cat_Target_overstock_rate', 'Cat_Target_sellout_rate', 'Product_Performance_Adjusted', 'Product_Performance', 'Product_Performance_Plain', 'Created_on', 'TAU_KEY']].copy()
    df_shops_adjusted_to_filobj.rename(columns={'Overstock_rate':'IST_RQ', 'Sellout_rate':'IST_AVQ', 'Product_Performance_Adjusted':'RKZ', 'Product_Performance':'RKZ2', 'Cat_Target_overstock_rate':'IR_SATZ', 'Cat_Target_sellout_rate':'AV_QUOTE', 'Product_Performance_Plain':'RKZ3'}, inplace=True)
    
    df_shops_adjusted_to_filobj.IST_RQ = df_shops_adjusted_to_filobj.IST_RQ.round(2)
    df_shops_adjusted_to_filobj.IST_AVQ = df_shops_adjusted_to_filobj.IST_AVQ.round(2)
    df_shops_adjusted_to_filobj.IR_SATZ = df_shops_adjusted_to_filobj.IR_SATZ.round(2)
    df_shops_adjusted_to_filobj.AV_QUOTE = df_shops_adjusted_to_filobj.AV_QUOTE.round(2)
    df_shops_adjusted_to_filobj.RKZ = df_shops_adjusted_to_filobj.RKZ.round(2)
    df_shops_adjusted_to_filobj.RKZ2 = df_shops_adjusted_to_filobj.RKZ2.round(3)
    df_shops_adjusted_to_filobj.RKZ3 = df_shops_adjusted_to_filobj.RKZ3.round(3)
    df_shops_adjusted_to_filobj['YEAR'] = int(data_selection_for_year)
    df_shops_adjusted_to_filobj['MONTH'] = int(month_number)
    
    df_shops_adjusted_to_filobj.to_sql(name='TB_RKZ_NEU_HKDFIL_OBJ_EH_TEST'+table_name_suff, schema='dbo', con=engine, index=False, chunksize=int(round(2100/df_shops_adjusted_to_filobj.shape[1]-1)), if_exists='append')
    
    mini = df_filobj_final.RKZ_HKDFIL_OBJ.min()
    mean = round(df_filobj_final.RKZ_HKDFIL_OBJ.mean(), 2)
    maxi = df_filobj_final.RKZ_HKDFIL_OBJ.max()
    
    string = f'<pre>RKZ_HKDFIL_OBJ for {month_number_string}/{data_selection_for_year}: Min: {mini}. Mean: {mean}. Max: {maxi}</pre>'
    return df_filobj_final,data_targets,data_daily,df_filobj_tau,df_shops_adjusted_to_filobj
    #return {'log': string} 
# for i in [12]:    
#     #test_brutto = run_RKZ(data_selection_for_year = 2021, month_number = i, ogr_key = 7, calculate_vgk_flag = True, current_overall_overstock_rate = 31.5,shop_exception = False)
#     test = run_RKZ(data_selection_for_year = 2021, month_number = i, ogr_key = 7, calculate_vgk_flag = True, current_overall_overstock_rate = 31.5,shop_exception = True)
    
#     print('Done!', i)