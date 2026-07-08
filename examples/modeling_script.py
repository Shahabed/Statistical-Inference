# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 14:51:47 2022

@author: Shahabedin Chatraee Azizabadi
Modeling script for Cross-selling 
"""

import pyodbc
import pandas as pd
import datetime
from sqlalchemy import create_engine
import inference_script
from pycaret.classification import *
from sklearn.metrics import average_precision_score
from sklearn.metrics import log_loss
from sklearn.metrics import jaccard_score

cnxn = pyodbc.connect("Driver={SQL Server};"
                      "Server=DEAXSMAPSQL02.itservices.asudc.net,6202;"
                      "Database=AboMart;"
                      "Trusted_Connection=yes;")
cursor = cnxn.cursor()

# Connection to Oracle Evolution via pyodbc
cnxn_ora = pyodbc.connect('DRIVER={Oracle in instantclient_21_3};DBQ=35.157.157.241:1521/ecrm;UID=SALES_IMPACT;PWD=tempts-y7kdg;')
#cnxn_ora = pyodbc.connect('DRIVER={Oracle in instantclient_19_6};DBQ=asbi02db04-vip.linux.asinfra.net:1521/ASPROD_BISVC;UID=CRM_DATA_ANALYTICS;PWD=paw-QzurcxN;')
cursor_ora = cnxn_ora.cursor()

#****Select cross-selling campaigns: Always the new campaigns should be added here!!****
#--------------------------------------------------------------------------------------
df_campaigns = pd.read_sql(f''' SELECT *
                FROM crm_sas_mart.lov_ASP_KID
                WHERE (KID IN ('BRB5BIA425A01LN','BRB6BTA425A01LN','BRB5BIA425A02LN','BRB6BTA425A02LN','BRB5BIA425A03LN','BRB6BTA425A03LN','BRB5BIA425A01LN','BRB6BTA425A01LN','BRB5BIA425A02LN','BRB6BTA425A02LN','BRB5BIA425A03LN','BRB6BTA425A03LN','BRB5BIA395A01LN', 'BRB5BIA315A01LN', 'BRB5BIA375A01LN', 'BRB0BIA255A01LN', 'BRB0BIA205A01LN', 'BRB0BIA155A01LN', 'BRB0BIA045A01LN', 'BRB0BIA015A01LN')) OR (Substr(KID, 1, 9) IN ('BR1835000', 'BR1835001', 'BR1835002', 'BR1855000', 'BR1885000', 'BR1985000', 'BR1935001','BR1935000', 'BR1955000', 'BR1935555') AND KID NOT IN ('BR1885100BA18SZ', 'BR1885100BI10SZ', 'BR1885100BI12SZ')) OR (Substr(KID, 1, 2) in ('BR') and Substr(KID, 7,3) in ('A04', 'A02', 'A01',  'A03'))
''', cnxn_ora)

df_campaigns['Titel'] = df_campaigns.KID.apply(lambda x: str(x)[9:11] if str(x)[2:4] in ['18', '19'] else str(x)[4:6])
df_campaigns['DKAMP'] = df_campaigns.KID.str[0:9]
df_campaigns['DL'] = df_campaigns.KID.str[13:15]
df_campaigns['WW'] = df_campaigns.DL.map({'LN':'MAILING', 'WM':'MAILING', 'ED':'E-MAIL', 'WM':'E-MAIL', 'EN':'TM','EE':'TM','EH':'TM','FR':'TM', 'F5':'TM','TG':'TM', 'SZ':'MAILING'})

#df_campaigns.shape
#df_campaigns[df_campaigns.KID.isin(['BRB5BIA395A01LN'])] # example of a 2021 campaign

#***Select contact points with subscribers(add the new campaigns)***
#-------------------------------------------------------------------------------
# Wall time: 6min 54s

df_contacts = pd.read_sql(f''' SELECT PERSONEN_ID, KAMPAGNE, AKTIONSDATUM, Neuzugang, ANSPRACHEDATUM, ResponseTyp
        FROM   crm_sas_mart.kontakthistorie
        WHERE (KAMPAGNE IN ('BRB5BIA425A01LN','BRB6BTA425A01LN','BRB5BIA425A02LN','BRB6BTA425A02LN','BRB5BIA425A03LN','BRB6BTA425A03LN','BRB5BIA395A01LN', 'BRB5BIA315A01LN', 'BRB5BIA375A01LN', 'BRB0BIA255A01LN', 'BRB0BIA205A01LN', 'BRB0BIA155A01LN', 'BRB0BIA045A01LN', 'BRB0BIA015A01LN')) OR (Substr(KAMPAGNE, 1, 9) IN ('BR1835000', 'BR1835001', 'BR1835002', 'BR1855000', 'BR1885000', 'BR1985000', 'BR1935001','BR1935000', 'BR1955000', 'BR1935555') AND KAMPAGNE NOT IN ('BR1885100BA18SZ', 'BR1885100BI10SZ', 'BR1885100BI12SZ')) OR (Substr(KAMPAGNE, 1, 2) in ('BR') and Substr(KAMPAGNE, 7,3) in ('A04', 'A02', 'A01',  'A03'))''', cnxn_ora)
        
#--------------------------------------------------------------------------        
df_contacts['JahrKontakt'] = df_contacts.NEUZUGANG.dt.year
df_contacts['DKAMP'] = df_contacts.KAMPAGNE.str[0:9]
df_contacts['KID_11'] = df_contacts.KAMPAGNE.str[0:12]
df_contacts['DL'] = df_contacts.KAMPAGNE.str[13:15]
df_contacts['WW'] = df_contacts.DL.map({'LN':'MAILING', 'WM':'MAILING', 'ED':'E-MAIL', 'WM':'E-MAIL', 'EN':'TM','EE':'TM','EH':'TM','FR':'TM', 'F5':'TM','TG':'TM', 'SZ':'MAILING'})
df_contacts['Titel'] = df_contacts.KAMPAGNE.apply(lambda x: str(x)[9:11] if str(x)[2:4] in ['18', '19'] else str(x)[4:6])
df_contacts['TopResponse'] = df_contacts.RESPONSETYP.apply(lambda x: 1 if x == '~' else 0)
df_contacts = df_contacts[#(df_contacts.JahrKontakt.isin([2018, 2019])) & # do not filter for old campaigns only
    (df_contacts.Titel == 'BI')]

df_contacts.PERSONEN_ID = df_contacts.PERSONEN_ID.astype('int')
df_contacts['Ident'] = df_contacts.apply(lambda x: f'{x.PERSONEN_ID}_{x.DKAMP}_{x.WW}', axis='columns')
df_contacts_bams = df_contacts[['PERSONEN_ID', 'KAMPAGNE', 'AKTIONSDATUM', 'ANSPRACHEDATUM', 'JahrKontakt', 'WW', 'DKAMP']].drop_duplicates().copy()
#df_contacts_bams.columns
#df_contacts_bams.shape
# ***Select definite BamS subscribers in the past****
# Wall time: 41min 59s
# BamS subscriptions without temporary and without future (before today minus 10 days) positions
df_bams_oracle = pd.read_sql(f'''SELECT c.*
FROM   (SELECT b.*,
                Row_number()
                  over (
                    PARTITION BY ID, POSNR
                    ORDER BY ID DESC, POSNR DESC) AS SEQNUM
        FROM   (SELECT PERSONEN_ID_WE  AS PERSONEN_ID,
                        GPAG,
                        ABOAUFTRAG_STATUS,
                        VBELN,
                        POSEX,
                        POSNR,
                        DRERZ,
                        ABO_VON         AS ABO_GUELTIG_VON,
                        ABO_BIS         AS ABO_GUELTIG_BIS,
                        XSTORNO         AS ABO_STORNO_JN,
                        ZZ_AUFTRAGSFORM AS ABO_AUFTRFORM_ID,
                        ZZ_KID          AS WAKT_KAMP_ID,
                        Substr(ZZ_KID, 1,9) AS DKAMP,
                        GUELTIGVON,
                        GUELTIGBIS,
                        PERSONEN_ID_WE || '_' || VBELN || '_' || POSEX AS ID
                FROM   crm_sas_mart.auftrag_abo_mc5
                WHERE  DRERZ IN ( '00002600' ) AND GUELTIGVON < TO_DATE('{datetime.date.today()-datetime.timedelta(days=10)}', 'YYYY-MM-DD') AND NOT (XSTORNO = 'X' AND Substr(ZZ_AUFTRAGSFORM, 1, 4) = 'A000' AND Substr(ZZ_AUFTRAGSFORM, 7, 4) = '000N' AND POSNR > '000001') ) b) c
WHERE  SEQNUM = 1 ''', cnxn_ora)

df_bams_oracle.PERSONEN_ID = df_bams_oracle.PERSONEN_ID.astype('int')
df_bams_oracle.POSEX = df_bams_oracle.POSEX.astype('int')
df_bams_oracle.VBELN = df_bams_oracle.VBELN.apply(lambda x: int(x))

#Merge definite BamS subscribers with contacting info from campaigns
df_bams_orders_max_pos = df_bams_oracle.merge(df_contacts_bams, on=['PERSONEN_ID'], how='inner')
df_bams_orders_max_pos['Titel'] = df_bams_orders_max_pos.KAMPAGNE.apply(lambda x: str(x)[9:11] if str(x)[2:4] in ['18', '19'] else str(x)[4:6])
df_bams_orders_max_pos['DKAMP'] = df_bams_orders_max_pos.KAMPAGNE.str[0:9]
#df_bams_orders_max_pos.shape
#Filter for specific cross-selling campaigns and append results: creat a list for the new campaigns
# number of sent offers way too low! (358.537/~610.000 in previous SAS analysis)
# run some very campaign specific logic to find the successful responses for BamS
# the listed campaigns were trying to sell BILD to BamS readers
# this code is a translation from SAS and could be optimised

# older campaigns
li_camp1 = ['BR1885000BI02ED', 'BR1885000BI04ED', 'BR1885000BI05ED', 'BR1885000BI07ED', 'BR1885000BI09ED', 'BR1885000BI19ED', 'BR1885000BI99ED']
li_camp2 = ['BR1855000BI01LN', 'BR1855000BI03LN', 'BR1855000BI05LN', 'BR1855000BI07LN', 'BR1855000BI09LN']
li_camp3 = ['BR1835000BI01EH', 'BR1835000BI01FR', 'BR1835002BI01EH']
li_camp4 = ['BR1985000BI10ED', 'BR1985000BI20ED', 'BR1985000BI30ED']
li_camp5 = ['BR1955000BI10LN', 'BR1955000BI30LN']
li_camp6 = ['BR1935000BI01EH']
li_camp7 = ['BRB0BIA018B01WM', 'BRB0BIA028A01WM', 'BRB0BIA038A01WM', 'BRB0BIA048C01WM', 'BRB0BIA048C11WM']
# 2019 campaigns
li_camp8 = ['BRB0BIA015A01LN', 'BRB0BIA045A01LN']
# newly added 2020 and 2021 campaigns
li_camp9 = ['BRB5BIA315A01LN', 'BRB5BIA375A01LN', 'BRB0BIA255A01LN', 'BRB0BIA205A01LN', 'BRB0BIA155A01LN']
# last 2021 campaign
li_camp10 = ['BRB5BIA395A01LN', 'BRB6BTA395A01LN', 'BRB5BIA395A02LN', 'BRB6BTA395A02LN', 'BRB5BIA395A03LN', 'BRB6BTA395A03LN']
# last 2022 campaign
li_camp11=['BRB5BIA425A01LN','BRB6BTA425A01LN','BRB5BIA425A02LN','BRB6BTA425A02LN','BRB5BIA425A03LN','BRB6BTA425A03LN']
# enter new campaign here


li_loop = [li_camp1, li_camp2, li_camp3, li_camp4, li_camp5, li_camp6, li_camp7, li_camp8, li_camp9, li_camp10,li_camp11]
drerz = '00002600'
df_sent_offers = pd.DataFrame()

for li_ca in li_loop:
    df_camp_tmp = df_bams_orders_max_pos[(df_bams_orders_max_pos.KAMPAGNE.isin(li_ca)) & (df_bams_orders_max_pos.DRERZ == drerz) & (df_bams_orders_max_pos.ABO_GUELTIG_BIS < df_bams_orders_max_pos.ANSPRACHEDATUM)].copy()
    df_camp_tmp['IDD'] = df_camp_tmp.apply(lambda x: f'{x.DKAMP}_{x.ANSPRACHEDATUM}_{x.PERSONEN_ID}', axis='columns')
    df_tmp = df_camp_tmp.groupby('IDD').agg({'ABO_GUELTIG_BIS':'count'}).reset_index()
    li_idd = df_tmp[df_tmp.ABO_GUELTIG_BIS >= 1].IDD.tolist()
    df_camp_tmp = df_camp_tmp[df_camp_tmp.IDD.isin(li_idd)]
    if df_sent_offers.empty:
        df_sent_offers = df_camp_tmp.copy()
    else:
        df_sent_offers = df_sent_offers.append(df_camp_tmp.copy(), sort=False)

#get BILD subscribers
# Wall time: 9.99 s
df_bild_oracle = pd.read_sql(f'''SELECT c.*
FROM   (SELECT b.*,
               Row_number()
                 over (
                   PARTITION BY ID, POSNR
                   ORDER BY ID DESC, POSNR DESC) AS SEQNUM
        FROM   (SELECT PERSONEN_ID_WE  AS PERSONEN_ID,
                       GPAG,
                       ABOAUFTRAG_STATUS,
                       VBELN,
                       POSEX,
                       POSNR,
                       DRERZ,
                       ABO_VON         AS ABO_GUELTIG_VON,
                       ABO_BIS         AS ABO_GUELTIG_BIS,
                       XSTORNO         AS ABO_STORNO_JN,
                       ZZ_AUFTRAGSFORM AS ABO_AUFTRFORM_ID,
                       ZZ_KID          AS WAKT_KAMP_ID,
                       Substr(ZZ_KID, 1,9) AS DKAMP,
                       GUELTIGVON,
                       GUELTIGBIS,
                       PERSONEN_ID_WE || '_' || VBELN || '_' || POSEX AS ID
                FROM   crm_sas_mart.auftrag_abo_mc5
                WHERE  ( Substr(ZZ_KID,1,9) in ('BR1835000', 'BR1835001', 'BR1835002', 'BR1855000', 'BR1885000', 'BR1985000', 'BR1935001','BR1935000', 'BR1955000', 'BR1935555') and ZZ_KID NOT IN ('BR1885100BA18SZ', 'BR1885100BI10SZ', 'BR1885100BI12SZ')) OR (Substr(ZZ_KID, 1, 2) in ('BR') and Substr(ZZ_KID, 7,3) in ( 'A04', 'A06', 'A02', 'A01', 'A03', 'A09', 'A11','A13','A14','A15','A16' )) AND
                
                DRERZ IN ( '00002700', '00002770' ) AND GUELTIGVON < TO_DATE('{datetime.date.today()-datetime.timedelta(days=10)}', 'YYYY-MM-DD') AND NOT (XSTORNO = 'X' AND Substr(ZZ_AUFTRAGSFORM, 1, 4) = 'A000' AND Substr(ZZ_AUFTRAGSFORM, 7, 4) = '000N' AND POSNR > '000001')) b) c
WHERE  SEQNUM = 1 ''', cnxn_ora)

df_bild_oracle['Titel'] = df_bild_oracle.WAKT_KAMP_ID.apply(lambda x: str(x)[9:11] if str(x)[2:4] in ['18', '19'] else str(x)[4:6])
df_bild_oracle['DKAMP'] = df_bild_oracle.WAKT_KAMP_ID.str[0:9]
df_bild_oracle.loc[df_bild_oracle.DKAMP.isin(['BR00BIA01', 'BR00BTA01', 'BRB1BTA01']), 'DKAMP'] = 'BRB0BIA01'
df_bild_oracle.loc[df_bild_oracle.DKAMP.isin(['BR00BIA02', 'BR00BTA02' , 'BRB1BTA02']), 'DKAMP'] = 'BRB0BIA02'
df_bild_oracle.loc[df_bild_oracle.DKAMP.isin(['BR00BIA03', 'BR00BTA03', 'BRB1BTA03']), 'DKAMP'] = 'BRB0BIA03'
df_bild_oracle.loc[df_bild_oracle.DKAMP.isin(['BR00BIA04', 'BR00BTA04' , 'BRB1BTA04']), 'DKAMP'] = 'BRB0BIA04'
df_bild_oracle['responsekezi'] = 'X'
# merge successful orders BILD with BamS
df_result = df_sent_offers.merge(df_bild_oracle[['PERSONEN_ID', 'DKAMP', 'Titel', 'responsekezi']], on=['PERSONEN_ID', 'DKAMP', 'Titel'], how='left')
df_result.responsekezi.fillna('O', inplace=True)
df_result.drop(columns=['DKAMP_x', 'DKAMP_y', 'IDD', 'SEQNUM', 'ID'], inplace=True)
df_result.rename(columns={'GPAG':'WE_GP_ID', 'VBELN':'PK_AUFTRAGS_ID', 'POSEX': 'PK_EXT_POS_ID'}, inplace=True)
df_result.WE_GP_ID = df_result.WE_GP_ID.astype('int')
df_result_bak = df_result.copy()
# df_result = df_result_bak.copy()
#df_result.shape
#--------------------------------------
#****Add data from AboMart*****
engine = create_engine('mssql://DEAXSMAPSQL02.itservices.asudc.net,6202/AboMart?trusted_connection=yes&driver=SQL+Server')
df_result.loc[:, ['PK_AUFTRAGS_ID', 'PK_EXT_POS_ID']].to_sql('#MERGER', con=engine, chunksize=200, method='multi', index=False, if_exists='replace')
df_bams_to_be_merged = pd.read_sql(f'''SELECT A.PK_AUFTRAGS_ID, A.PK_EXT_POS_ID, A.ABO_AUFTRFORMGRP_ID, A.ABO_ERSTE_NP_RG_BEZ, A.ABO_KDAUFART_ID, A.ABO_KOMBI_ID, A.OBJ_ID, A.POS_KUENDGRUND_ID, A.POS_AKAT1_ID, A.VSG_HKD_ID, A.VSG_FIL_ID, A.WAKT_AKTART_ID, A.WAKT_EVENT_ID, A.WAKT_WERBEART_ID, A.WAKT_ZIELGRP_ID, A.ABO_BESTWEG_ID, A.ABO_ZAHLWEG_ID, A.ABO_ZAHLRHY_ID, A.WERB_PRAEMIEN_ID, A.WERB_WERBEWEG_ID, A.WE_ANREDE_ID, A.WE_VORNAME_FIRMA, A.WE_NAME, A.KGS22, A.ABO_PG_ID, A.POS_BEZUGSPER_ID, A.POS_LIEFART_ID, A.ZAHLWEG_TYP1_ID, A.WERBEWEG_TYP1_ID, A.AUFTRAGSFORM_TYP1_ID, A.ZAHLRHYTHMUS_TYP1_ID, A.BESTELLWEG_TYP1_ID, A.AKTIONSART_TYP1_ID, A.LIEFERENDE_TYP1_ID, A.ABO_LREKL, A.ABO_LMFR, A.ABO_PREKL, A.ABO_PMFR, A.WAKT_DKAMP_ID FROM DBO.VW_BWP_LS AS A INNER JOIN #MERGER AS B ON A.PK_AUFTRAGS_ID = B.PK_AUFTRAGS_ID AND
A.PK_EXT_POS_ID = B.PK_EXT_POS_ID WHERE OGR_ID IN ( 6 )''', engine)
engine.dispose()
# merge AboMart data with CRM DWH data and drop duplicates (!)
df_result_new = df_result.merge(df_bams_to_be_merged, on=['PK_AUFTRAGS_ID', 'PK_EXT_POS_ID'], how='left').drop_duplicates()
#df_result_new.shape
#******Add age of the subscriber****
engine = create_engine('mssql://DEAXSMAPSQL02.itservices.asudc.net,6202/AboMart?trusted_connection=yes&driver=SQL+Server')
df_result_new.loc[:, 'WE_GP_ID'].to_sql('#GP_ID_AGE', con=engine, chunksize=200, method='multi', index=False, if_exists='replace')
df_ages = pd.read_sql(f'select B.WE_GP_ID, BEST_ALTER from AboMart.dbo.TB_AM_DIM_WE_Alter AS A RIGHT JOIN #GP_ID_AGE AS B ON A.WE_GP_ID = B.WE_GP_ID', engine)
df_ages.drop_duplicates(inplace=True) # business partners may occur multiple times
engine.dispose()

df_result_enhanced = df_result_new.merge(df_ages, on=['WE_GP_ID'], how='left')
#df_result_enhanced.shape
#***Add duration of subscription in days***
today = datetime.date.today()
df_result_enhanced['ABODAUER'] = df_result_enhanced.ABO_GUELTIG_VON.apply(lambda x: (today - x.date()).days)

#***Remove missing durations, impute some values***
df_result_enhanced.dropna(subset=['ABODAUER'], inplace=True)
df_result_enhanced.ABO_STORNO_JN = df_result_enhanced.ABO_STORNO_JN.apply(lambda x: "0" if x == pd.isna(x) else x)
df_result_enhanced.ZAHLWEG_TYP1_ID.fillna(0, inplace=True)
df_result_enhanced.ZAHLRHYTHMUS_TYP1_ID.fillna(-9999, inplace=True)
df_result_enhanced.ABO_KOMBI_ID = df_result_enhanced.ABO_KOMBI_ID.apply(lambda x: "0" if x == pd.isna(x) else x)

#***Add more features***
df_result_enhanced['Verpflichtung1'] = df_result_enhanced.ABO_AUFTRFORM_ID.str[1:4]
df_result_enhanced['Verpflichtung2'] = df_result_enhanced.ABO_AUFTRFORM_ID.str[6:9]
df_result_enhanced['Bula'] = df_result_enhanced.KGS22.str[0:2]
df_result_enhanced['KGS16'] = df_result_enhanced.KGS22.str[0:17]
df_result_enhanced.Verpflichtung1 = df_result_enhanced.apply(lambda x: x.Verpflichtung2 if x.Verpflichtung1 == 0 else x.Verpflichtung1, axis='columns')

li_werbeweg = ['AZ', 'BEIL', 'DIREKT', 'EMAIL', 'INT', 'MAIL', 'TM', 'VST']
df_result_enhanced['WERBEWEG_GRP'] = df_result_enhanced.WERB_WERBEWEG_ID.apply(lambda x: 'SONST' if x not in li_werbeweg else x)

df_result_enhanced['letzteAbodauer'] = pd.cut(df_result_enhanced.ABODAUER, bins = [0, 182, 365, 728, 1825, 99999999999999999], labels = [182, 365, 728, 1825, 3651])
#df_result_enhanced.letzteAbodauer.value_counts()
#df_result_enhanced.shape
#***Add even more features***: this feature doesn't exist anymore in the database (!)
#***Add contact points***
df_result_enhanced['Ansprachedatum2'] = datetime.date.today() # to be improved
# select a list of people
df_people = df_result_enhanced[['PERSONEN_ID', 'Ansprachedatum2']].drop_duplicates().copy()
# select a list of campaigns where a person (PERSONEN_ID) was addressed only once (CNT == 1) under a specific campaign (DKAMP) 
# Wall time: 18min 40s

df_campaigns = pd.read_sql(f'''
SELECT a.*
FROM   (SELECT PERSONEN_ID,
               Substr(KAMPAGNE, 1, 9) AS DKAMP,
               ANSPRACHEDATUM,
               Count(*)               AS CNT
        FROM   crm_sas_mart.kontakthistorie
        WHERE  VERTRIEBS_ORG = 'BGZS'
               AND DRUCKERZEUGNISKUERZEL IN ( 'BA', 'BI' )
        GROUP  BY PERSONEN_ID,
                  Substr(KAMPAGNE, 1, 9),
                  ANSPRACHEDATUM) a
WHERE  a.CNT = 1
''', cnxn_ora)

df_campaigns.PERSONEN_ID = df_campaigns.PERSONEN_ID.astype('int')
#df_campaigns.shape
df_contacts = df_people.merge(df_campaigns, on=['PERSONEN_ID'], how='inner')
df_contacts = df_contacts[df_contacts.Ansprachedatum2 > df_contacts.ANSPRACHEDATUM] # person addressed in the past
df_contacts = df_contacts.groupby(by=['PERSONEN_ID', 'Ansprachedatum2']).agg({'DKAMP' : 'count'}).rename(columns={'DKAMP':'Kontakte'}).reset_index(drop=False)
# merge into original dataset
df_result_enhanced = df_result_enhanced.merge(df_contacts[['PERSONEN_ID', 'Kontakte']], on=['PERSONEN_ID'], how='left')
# group contact points into new feature
df_result_enhanced['GRP_Kontakte'] = pd.cut(df_result_enhanced.Kontakte, bins = [0, 1, 2, 5, 10, 20, 99999], labels = [1, 2, 5, 10, 20, 21])
#df_result_enhanced.GRP_Kontakte.value_counts()
#df_result_enhanced.shape
#****Add opt-in********line 
# retrieve that last optin decision per person
df_optin = pd.read_sql(f'''
SELECT a.* FROM (SELECT PERSONEN_ID, OPTIN AS PERSONEN_OPTIN,
       ERFASSUNGSDATUM,
       Row_number()
         over (
           PARTITION BY PERSONEN_ID, ERFASSUNGSDATUM
           ORDER BY PERSONEN_ID, ERFASSUNGSDATUM DESC) AS rn
FROM crm_sas_mart.personen_optin) a WHERE rn = 1
''', cnxn_ora)

df_optin.PERSONEN_ID = df_optin.PERSONEN_ID.astype('int')
df_optin.PERSONEN_OPTIN = df_optin.PERSONEN_OPTIN.map({'J':1, 'N':0})

df_result_enhanced = df_result_enhanced.merge(df_optin[['PERSONEN_ID', 'PERSONEN_OPTIN']], on=['PERSONEN_ID'], how='left')
df_result_enhanced.PERSONEN_OPTIN.fillna(99, inplace=True)
df_result_enhanced.PERSONEN_OPTIN.value_counts(dropna=False)
#df_result_enhanced.shape
#*****Add previous BamS subscriptions*****
#from sqlalchemy import create_engine

engine = create_engine('mssql://DEAXSMAPSQL02.itservices.asudc.net,6202/AboMart?trusted_connection=yes&driver=SQL+Server')
df_result_enhanced.loc[:, ['PERSONEN_ID', 'WE_GP_ID']].to_sql('#PERSONS', con=engine, chunksize=200, method='multi', index=False, if_exists='replace')
df_subscriptions = pd.read_sql(f'''select B.PERSONEN_ID, B.WE_GP_ID, A.PK_AUFTRAGS_ID, A.PK_EXT_POS_ID, A.ABO_GUELTIG_BIS from AboMart.dbo.TB_AM_ABO_Kennzahlen AS A RIGHT JOIN #PERSONS AS B ON A.WE_GP_ID = B.WE_GP_ID WHERE A.OGR_ID = 6 AND A.ABO_KDAUFART_ID IN ('ZABO', 'LABO', 'ZLAB', 'ZWBZ', 'WBZA', 'LGES', 'ZPKO', 'ZPGE')''', engine)
df_subscriptions.PERSONEN_ID = df_subscriptions.PERSONEN_ID.astype('int')
engine.dispose()

df_subscriptions['Ansprachedatum'] = datetime.datetime.today() # to be improved
df_subscriptions = df_subscriptions[df_subscriptions.Ansprachedatum > df_subscriptions.ABO_GUELTIG_BIS]
df_subscriptions = df_subscriptions.groupby(by=['PERSONEN_ID', 'Ansprachedatum']).agg({'WE_GP_ID' : 'count'}).rename(columns={'WE_GP_ID':'Subscriptions'}).reset_index(drop=False)
df_subscriptions['GRP_Subscriptions'] = pd.cut(df_subscriptions.Subscriptions, bins = [0, 0.999, 1.99999, 2.99999, 3.99999, 4.99999, 5.99999, 999999], labels = [0, 1, 2, 3, 4 ,5 ,6])

df_result_enhanced = df_result_enhanced.merge(df_subscriptions[['PERSONEN_ID', 'Subscriptions', 'GRP_Subscriptions']], on=['PERSONEN_ID'], how='left')
df_result_enhanced.GRP_Subscriptions.value_counts()
#df_result_enhanced.shape
#*****And another feature transformation*********
df_result_enhanced['GRP_Alter'] = pd.cut(df_result_enhanced.BEST_ALTER, bins = [0, 20, 30, 40, 50, 60, 70, 80, 9999], labels = [20, 30, 40, 50, 60, 70, 80, 81])
df_result_enhanced.GRP_Alter.value_counts()
#df_result_enhanced.shape
#*******Digital subscriptions from M/SD (SAP) via AboMart************
# read related digital subscriptions
engine = create_engine('mssql://DEAXSMAPSQL02.itservices.asudc.net,6202/AboMart?trusted_connection=yes&driver=SQL+Server')
df_digital = pd.read_sql(f'''select OGR_ID, PK_AUFTRAGS_ID, PK_EXT_POS_ID, ABO_AUFTRFORM_ID, ABO_KDAUFART_ID, ABO_GUELTIG_VON, ABO_GUELTIG_BIS, ABO_STORNO_JN, ABO_ERSTER_EVT, ABO_LETZTER_EVT, ABO_ERSTE_NP_RG_BEZ, WAKT_DKAMP_ID, WE_GP_ID from AboMart.dbo.VW_BWP_LS WHERE OGR_ID in (2110, 2710) AND ABO_KDAUFART_ID IN ('ZABO', 'LABO', 'ZLAB', 'ZWBZ', 'WBZA', 'LGES', 'ZPKO', 'ZPGE')''', engine)
df_digital['Verpflichtung1'] = df_digital.ABO_AUFTRFORM_ID.str[1:4]
df_digital['Verpflichtung2'] = df_digital.ABO_AUFTRFORM_ID.str[6:9]
df_digital['Option'] = df_digital.ABO_AUFTRFORM_ID.str[9:10]
df_digital['Angebot'] = df_digital.ABO_AUFTRFORM_ID.str[0:1]
df_digital.Verpflichtung1 = df_digital.apply(lambda x: x.Verpflichtung2 if x.Verpflichtung1 == 0 else x.Verpflichtung1, axis='columns')
df_digital['Angebot_Digi'] = df_digital.apply(lambda x: f'{x.Angebot}{x.Verpflichtung1}{x.Option}', axis='columns')
df_digital['VERTRIEBS_ORG_MSD'] = df_digital.OGR_ID.map({2110:'ZGB', 2710:'BGZS'})
df_digital.VERTRIEBS_ORG_MSD = df_digital.VERTRIEBS_ORG_MSD.fillna('WRONG')

# again get list of persons
df_persons = df_result_enhanced.loc[:, ['PERSONEN_ID', 'WE_GP_ID']].copy()
df_persons['Ansprachedatum'] = datetime.datetime.today()

# merge
df_digital_subscriptions = df_digital[['WE_GP_ID', 'PK_AUFTRAGS_ID', 'PK_EXT_POS_ID', 'ABO_GUELTIG_BIS', 'Angebot_Digi', 'VERTRIEBS_ORG_MSD']].merge(df_persons, on=['WE_GP_ID'], how='inner')
# subset with those who were addresses after subscription ended
df_digital_subscriptions = df_digital_subscriptions[df_digital_subscriptions.Ansprachedatum > df_digital_subscriptions.ABO_GUELTIG_BIS]

df_digital_subscriptions_agg_bild = df_digital_subscriptions[df_digital_subscriptions.VERTRIEBS_ORG_MSD == 'BGZS'].groupby(by=['PERSONEN_ID', 'Ansprachedatum']).agg({'WE_GP_ID' : 'count'}).rename(columns={'WE_GP_ID':'ANZ_BILD_digi_MSD'}).reset_index(drop=False)
df_digital_subscriptions_agg_welt = df_digital_subscriptions[df_digital_subscriptions.VERTRIEBS_ORG_MSD == 'ZGB'].groupby(by=['PERSONEN_ID', 'Ansprachedatum']).agg({'WE_GP_ID' : 'count'}).rename(columns={'WE_GP_ID':'ANZ_WELT_digi_MSD'}).reset_index(drop=False)

# new aggregated dataset
df_digital_subscriptions_agg = df_digital_subscriptions_agg_bild[['PERSONEN_ID', 'ANZ_BILD_digi_MSD']].merge(df_digital_subscriptions_agg_welt[['PERSONEN_ID', 'ANZ_WELT_digi_MSD']], on=['PERSONEN_ID'], how='outer').fillna(0) # fillna for occurance of zero

df_result_enhanced = df_result_enhanced.merge(df_digital_subscriptions_agg, on=['PERSONEN_ID'], how='left')
#df_result_enhanced.shape
#******Digital subscriptions from CRM DWH (Oracle)********start from line 54
df_oracle_subscription_mapping = pd.read_sql(f'''
SELECT Personen_ID_D, Personen_ID_P AS PERSONEN_ID
FROM crm_sas_mart.REFERENZ_PRINT_DIGITAL
''', cnxn_ora)

df_oracle_subscription_mapping.PERSONEN_ID = df_oracle_subscription_mapping.PERSONEN_ID.astype('int')
df_oracle_subscription_mapping.PERSONEN_ID_D = df_oracle_subscription_mapping.PERSONEN_ID_D.astype('int')
# erroneous mapping as only a few entries can be mapped
df_part_a = df_result_enhanced[['PERSONEN_ID', 'PK_AUFTRAGS_ID', 'ABO_GUELTIG_BIS']].merge(df_oracle_subscription_mapping, on=['PERSONEN_ID'], how='left')
# only a few thousand solely order BamS and have a digital subscription
df_part_a.PERSONEN_ID_D.dropna().count()
df_result_enhanced.PERSONEN_ID.head()
df_oracle_subscription_mapping.head()
# takes terribly long b/c we can't fill temporary tables with Oracle and sqlalchemy
# workaround exists but isn't implemented yet... look at the inference part
# Wall time: 1h 28min 53s

df_part_b = pd.read_sql('SELECT d.PERSONEN_ID_WE, d.vbeln_basis AS vbeln_basis_d, d.vbeln AS vbeln_d, d.abo_von AS abo_von_d, d.abo_bis AS abo_bis_d, d.aboauftrag_status as aboauftrag_status_d, d.material AS material_d, d.bundle AS bundle_d, e.vertriebs_org AS vertriebs_org_d, e.bezeichnung AS bezeichnung_d FROM crm_sas_mart.auftrag_abo_sc5 d LEFT JOIN crm_sas_mart.lov_vertriebs_org e ON d.MATERIAL=e.MATERIAL', cnxn_ora)
df_part_b.PERSONEN_ID_WE = df_part_b.PERSONEN_ID_WE.astype('int')
df_full = df_part_a.merge(df_part_b, left_on='PERSONEN_ID_D', right_on='PERSONEN_ID_WE', how='inner')
df_full[df_full.PERSONEN_ID == 1094721].BEZEICHNUNG_D.unique()
df_full['Ansprachedatum'] = datetime.datetime.today()
df_full = df_full[df_full.Ansprachedatum > df_full.ABO_BIS_D] # as in old script
df_full = df_full[['PERSONEN_ID', 'Ansprachedatum', 'VBELN_D', 'VERTRIEBS_ORG_D', 'PK_AUFTRAGS_ID']]

df_full_agg_bild = df_full[df_full.VERTRIEBS_ORG_D == 'BD'].groupby(by=['PERSONEN_ID', 'Ansprachedatum']).agg({'PK_AUFTRAGS_ID' : 'count'}).rename(columns={'PK_AUFTRAGS_ID':'ANZ_BILD_digi_SD'}).reset_index(drop=False)
df_full_agg_welt = df_full[df_full.VERTRIEBS_ORG_D == 'ZGB'].groupby(by=['PERSONEN_ID', 'Ansprachedatum']).agg({'PK_AUFTRAGS_ID' : 'count'}).rename(columns={'PK_AUFTRAGS_ID':'ANZ_WELT_digi_SD'}).reset_index(drop=False)
df_full_agg_others = df_full[~df_full.VERTRIEBS_ORG_D.isin(['ZGB','BD',''])].groupby(by=['PERSONEN_ID', 'Ansprachedatum']).agg({'PK_AUFTRAGS_ID' : 'count'}).rename(columns={'PK_AUFTRAGS_ID':'ANZ_SO_digi_SD'}).reset_index(drop=False)

# new aggregated dataset
df_full_agg = df_full_agg_bild.merge(df_full_agg_welt, on=['PERSONEN_ID'], how='outer')
df_full_agg = df_full_agg.merge(df_full_agg_others, on=['PERSONEN_ID'], how='outer')
df_full_agg.iloc[80]
# merge digital subscription number data
df_result_enhanced = df_result_enhanced.merge(df_full_agg, on=['PERSONEN_ID'], how='left')
#df_result_enhanced.shape

#*****Create feature from linked digital subscriptions***** start from line 66
# at least one digital subscription existing in the data
df_result_enhanced['ANZ_DIGI'] = df_result_enhanced.apply(lambda x: 1 if pd.notna(x.ANZ_WELT_digi_MSD) or pd.notna(x.ANZ_WELT_digi_SD) or pd.notna(x.ANZ_BILD_digi_SD) or pd.notna(x.ANZ_BILD_digi_MSD) or pd.notna(x.ANZ_SO_digi_SD) else 0, axis='columns')
df_result_enhanced.to_pickle('data_raw_final_v1.pkl', protocol = 4)
# df_result_enhanced = pd.read_pickle('data_raw.pkl')
df_result_enhanced.info()
df_result_enhanced.ANZ_WELT_digi_MSD.value_counts()
df_result_enhanced.ANZ_WELT_digi_SD.value_counts()
df_result_enhanced.ANZ_BILD_digi_SD.value_counts()
df_result_enhanced.ANZ_BILD_digi_MSD.value_counts()
df_result_enhanced.ANZ_SO_digi_SD.value_counts()
df_result_enhanced.ANZ_DIGI.value_counts()
#df_result_enhanced.shape
df_result_enhanced.info()

#*****Final steps for a modelling dataset*************
df_result_enhanced['GRP_ANZ_WELT_digi_MSD']  = pd.cut(df_result_enhanced.ANZ_WELT_digi_MSD, bins=10)
df_result_enhanced['GRP_ANZ_WELT_digi_SD']  = pd.cut(df_result_enhanced.ANZ_WELT_digi_SD, bins=10)
df_result_enhanced['GRP_ANZ_BILD_digi_SD']  = pd.cut(df_result_enhanced.ANZ_BILD_digi_SD, bins=10)
df_result_enhanced['GRP_ANZ_BILD_digi_MSD']  = pd.cut(df_result_enhanced.ANZ_BILD_digi_MSD, bins=10)
df_result_enhanced['GRP_ANZ_SO_digi_SD']  = pd.cut(df_result_enhanced.ANZ_SO_digi_SD, bins=10)
df_result_enhanced.PERSONEN_ID.to_pickle('data_final_final_identities.pkl', protocol = 4)
df_result_enhanced_final = df_result_enhanced[['responsekezi', 'ANZ_SO_digi_SD','ANZ_BILD_digi_MSD','ANZ_BILD_digi_SD','ANZ_WELT_digi_SD','ANZ_WELT_digi_MSD', 'ANZ_DIGI', 'Kontakte', 'BEST_ALTER', 'Subscriptions', 'PERSONEN_OPTIN', 'WERBEWEG_GRP', 'ABODAUER']].copy()
df_result_enhanced_final.to_pickle('data_final_final_v1.pkl', protocol = 4)

#*****Finally! The modelling part :-)****************************************
#*How to make this score a bit more exciting during the DSE presentation?****** start from line 82
# we have severe class imbalance: what solution we can find here!
df_result_enhanced_final.responsekezi.value_counts()
# we have a success quota of 0.8962% and according to the businesss stakeholder, already 0.4% are considered "very good"
df_result_enhanced_final.responsekezi.value_counts(normalize=True)
df_result_enhanced_final.head(100)
# Herein, we can add a script to impute the data, as data contains many NaNs. 
# For some features replacing the NaNs with zeros would make most sense. 
# We want to have the figure for past subscriptions, so if none, they should be zero
## Keep in mind that pycaret automatically imputes nan! by mean and constant!

exp_clf_cross_selling = setup(data = df_result_enhanced_final, target = 'responsekezi', session_id = 20211003, feature_interaction = True, interaction_threshold = 0.01, categorical_features = ['ANZ_DIGI', 'PERSONEN_OPTIN', 'WERBEWEG_GRP'], silent = True)

add_metric('apc', 'APC', average_precision_score, target = 'pred_proba')

add_metric('logloss', 'LogLoss', log_loss, greater_is_better = False)

add_metric('jacc', 'JACC', jaccard_score) # jaccard score
# throw a couple of models in the arena
model_list = ['lightgbm', 'lr', 'rf', 'dt', 'svm', 'qda', 'lda']
#trains and evaluates the performance of all estimators available in the model library
top3 = compare_models(sort='jacc', include = model_list, n_select = 3)
# in-sample evaluation required => why when we do 10-fold cross validation?
# explain Kappa, MCC
# logloss?!
# correct order => AUC => Whats the final threshold? How many are usually selected for a campaign?
# correct prob => logloss
tuned_top3 = [tune_model(x, optimize='jacc') for x in top3]

# trains a Soft Voting / Majority Rule classifier for select models passed in
blender = blend_models(tuned_top3, optimize='jacc')
#trains a meta-model over select estimators passed in

stacker = stack_models(tuned_top3, optimize='jacc')
#-------------------------------------------
#*******Model Optimised for Jaccard score******
best_jacc_model = automl(optimize = 'jacc')
# let the best model talk
plot_model(best_jacc_model, plot = 'auc')

plot_model(best_jacc_model, plot = 'confusion_matrix')

best_jacc_final_opt = optimize_threshold(best_jacc_model, optimize='jacc', grid_interval=0.1)

best_jacc_final = finalize_model(best_jacc_final_opt)

#saving the model
save_model(best_jacc_final, 'voting_jacc_score')

#****!!!!Go to the inference script and run it separately!!!!****

inference_script.inference() 
#---------------------------------------------------------------
# Part following inference script
pred_data = pd.read_pickle('data_inference_final_final_v1.pkl') # 18 MByte
pred_data
preds = predict_model(best_jacc_final, data = pred_data)
preds.Label.value_counts(normalize=True)
preds.Label.value_counts()
preds.Score.value_counts()
# What is the reason for the moving preds score by 1?
preds.Score = 1 - preds.Score

preds.Score.value_counts()

pred_final = pd.read_pickle('data_inference_final_final_personen_v1.pkl') # 18 MByte

pred_ulti = pred_final.merge(preds[['Score']], left_index=True, right_index=True)

pred_ulti = pred_ulti[pd.notna(pred_ulti.personen_id)]

pred_ulti.personen_id = pred_ulti.personen_id.astype('int64')

pred_ulti['Identifier'] = 'DIGE_XSELL_BI'
pred_ulti['Bereich'] = 'BGZS'
pred_ulti.rename(columns={'personen_id':'PERSONEN_ID', 'Score':'Value_Num_1'}, inplace=True)

pred_ulti = pred_ulti[['Identifier', 'PERSONEN_ID', 'Bereich', 'Value_Num_1']]

pred_ulti.sort_values(by='Value_Num_1', inplace=True)
pred_ulti['Value_Num_1'] = pred_ulti['Value_Num_1'] * 100
pred_ulti['Value_Num_1'] = pred_ulti['Value_Num_1'].round(2)
# pred_ulti.to_csv(f'Cross_BamS_{datetime.datetime.now().strftime("%Y%m%d")}.csv', index=False)

# all subscribers
pred_ulti[(~pred_ulti.PERSONEN_ID.duplicated())].to_csv(f'Cross_BamS_V2_{datetime.datetime.now().strftime("%Y%m%d")}.csv', index=False, sep=';', decimal=',')

pred_ulti.Value_Num_1.value_counts()

# ****It is aquestion that should I run the following code!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!***
# only small subscriber numbers
#pred_ulti[(~pred_ulti.PERSONEN_ID.duplicated()) & (pred_ulti.PERSONEN_ID <= 99999999)].to_csv(f'Cross_BamS_V2_{datetime.datetime.now().strftime("%Y%m%d")}.csv', index=False, sep=';', decimal=',')
#pred_ulti[(~pred_ulti.PERSONEN_ID.duplicated()) & (pred_ulti.PERSONEN_ID <= 99999999)].shape




















