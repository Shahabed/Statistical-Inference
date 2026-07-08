# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 11:33:52 2022

@author: Shahabedin Chatraee Azizabadi
the inference script for cross-selling score computation
"""
import pandas as pd
import datetime
#pip install cx_Oracle
import cx_Oracle
import pyodbc
#from sqlalchemy import create_engine
from sqlalchemy import create_engine, Column, Integer, MetaData
from sqlalchemy.ext.declarative import declarative_base
def inference():
    engine = create_engine('mssql://DEAXSMAPSQL02.itservices.asudc.net,6202/AboMart?trusted_connection=yes&driver=SQL+Server')
    df_bams = pd.read_sql(f"""SELECT
            PK_AUFTRAGS_ID,
            PK_EXT_POS_ID,
            OGR_ID,
            WERB_PRAEMIEN_ID,
            POS_BEZUGSPER_ID,
            Zahlweg_Typ1_id,
            Zahlrhythmus_Typ1_id,
            ABO_AUFTRFORM_ID,
            ABO_GUELTIG_VON,
            ABO_GUELTIG_BIS,
            KGS22,
            ABO_KDAUFART_ID,
            WE_GP_ID,
            ABO_STORNO_JN,
            ABO_KOMBI_ID,
            WAKT_DKAMP_ID,
            WE_LAND,
            ABO_AUFTRFORMGRP_ID,
            WERB_WERBEWEG_ID,
            Werbeweg_Typ1_id
    FROM   dbo.vw_bwp_ls
    WHERE  ogr_id IN (6) AND abo_gueltig_bis > '{datetime.datetime.now().strftime("%Y-%m-%d")}' AND abo_kdaufart_id in ('ZABO', 'LABO', 'ZLAB')""", engine)
    
    engine.dispose()
    #df_bams.shape
    Base = declarative_base()
    
    class TEMP_TABLE(Base):
        __tablename__ = "my_temp_table"
        PK_AUFTRAGS_ID = Column(Integer, primary_key=True)
        PK_EXT_POS_ID = Column(Integer, primary_key=True)
        
    #engine = create_engine("oracle+cx_oracle://CRM_DATA_ANALYTICS:paw-QzurcxN@asbi02db04-vip.linux.asinfra.net:1521/?service_name=ASPROD_BISVC")
    #engine = create_engine("oracle+cx_oracle://SALES_IMPACT:tempts-y7kdg@35.157.157.241:1521/?service_name=ecrm")
    engine = create_engine("oracle+cx_oracle://CRM_INDIVIDUAL:pithy-7Z*t2W4@35.157.157.241:1521/?service_name=ecrm")
    
    Base.metadata.drop_all(engine, tables=[TEMP_TABLE.__table__])
    
    Base.metadata.create_all(engine)    
    
    
    connection = cx_Oracle.connect(user="CRM_INDIVIDUAL", password="pithy-7Z*t2W4",
                                   dsn="35.157.157.241:1521/ecrm",
                                   encoding="UTF-8")
    
    cursor = connection.cursor()
    
    data = df_bams.loc[:, ['PK_AUFTRAGS_ID', 'PK_EXT_POS_ID']].values.tolist()
    
    cursor.executemany("""
            insert into my_temp_table (PK_AUFTRAGS_ID, PK_EXT_POS_ID)
            values (:1, :2)""", data)
    
    connection.commit()
    connection.close()
    
    df_test = pd.read_sql(f'''SELECT COUNT(*) AS CNT FROM my_temp_table''', engine)
    assert df_test.cnt.iloc[0] > 0 # test for row count larger zero
    
    engine.dispose()
    engine = create_engine("oracle+cx_oracle://CRM_INDIVIDUAL:pithy-7Z*t2W4@35.157.157.241:1521/?service_name=ecrm")
    
    df_bams_oracle = pd.read_sql(f'''SELECT c.*
    FROM   (SELECT b.*,
                   Row_number()
                     over (
                       PARTITION BY ID, POSNR
                       ORDER BY ID DESC, POSNR DESC) AS SEQNUM
            FROM   (SELECT CAST(PERSONEN_ID_WE AS INTEGER)  AS PERSONEN_ID,
                           CAST(GPAG AS INTEGER) AS GPAG,
                           ABOAUFTRAG_STATUS,
                           CAST(VBELN AS INTEGER) AS VBELN,
                           CAST(POSEX AS INTEGER) AS POSEX,
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
                    FROM   crm_sas_mart.auftrag_abo_mc5 a INNER JOIN my_temp_table ON my_temp_table.pk_auftrags_id = a.VBELN AND my_temp_table.pk_ext_pos_id = a.POSEX
                    WHERE  DRERZ IN ('00002600')) b) c
    WHERE SEQNUM = 1''', engine)
    
    df_bams_oracle.personen_id = df_bams_oracle.personen_id.astype('int')
    df_bams_oracle.posex = df_bams_oracle.posex.astype('int')
    df_bams_oracle.vbeln = df_bams_oracle.vbeln.apply(lambda x: int(x))
    
    engine.dispose()
    df_bams_oracle = df_bams_oracle.sort_values(by=['gpag', 'abo_gueltig_bis']).drop_duplicates(subset=['gpag'], keep='last')
    df_bams = df_bams.merge(df_bams_oracle, left_on=['PK_AUFTRAGS_ID', 'PK_EXT_POS_ID'], right_on=['vbeln', 'posex'], how='left')
    df_bams = df_bams.sort_values(by=['WE_GP_ID', 'ABO_GUELTIG_BIS']).drop_duplicates(subset=['WE_GP_ID'], keep='last')
    #df_bams.shape
    #****Select active BILD customers******-------------------------------------
    engine = create_engine('mssql://DEAXSMAPSQL02.itservices.asudc.net,6202/AboMart?trusted_connection=yes&driver=SQL+Server')
    df_bild = pd.read_sql(f"""SELECT WE_GP_ID, PK_AUFTRAGS_ID, PK_EXT_POS_ID
        FROM dbo.vw_bwp_ls
    WHERE  ogr_id IN (7) AND abo_gueltig_bis > '{datetime.datetime.now().strftime("%Y-%m-%d")}'""", engine)
    
    engine.dispose()
    # drop and create temporary table, then fill it with data and join later
    
       
    Base = declarative_base()
    
    class TEMP_TABLE(Base):
        __tablename__ = "my_temp_table"
        PK_AUFTRAGS_ID = Column(Integer, primary_key=True)
        PK_EXT_POS_ID = Column(Integer, primary_key=True)
        
    #engine = create_engine("oracle+cx_oracle://CRM_DATA_ANALYTICS:paw-QzurcxN@asbi02db04-vip.linux.asinfra.net:1521/?service_name=ASPROD_BISVC")
    engine = create_engine("oracle+cx_oracle://CRM_INDIVIDUAL:pithy-7Z*t2W4@35.157.157.241:1521/?service_name=ecrm")
    
    Base.metadata.drop_all(engine, tables=[TEMP_TABLE.__table__])
    
    Base.metadata.create_all(engine)
        
    connection = cx_Oracle.connect(user="CRM_INDIVIDUAL", password="pithy-7Z*t2W4",
                                   dsn="35.157.157.241:1521/ecrm",
                                   encoding="UTF-8")
    
    cursor = connection.cursor()
    
    data = df_bild.loc[:, ['PK_AUFTRAGS_ID', 'PK_EXT_POS_ID']].values.tolist()
    
    cursor.executemany("""
            insert into my_temp_table (PK_AUFTRAGS_ID, PK_EXT_POS_ID)
            values (:1, :2)""", data)
    
    connection.commit()
    connection.close()
    
    df_test = pd.read_sql(f'''SELECT COUNT(*) AS CNT FROM my_temp_table''', engine)
    assert df_test.cnt.iloc[0] > 0 # test for row count larger zero
    
    engine.dispose()
    # line 12 start here
    engine = create_engine("oracle+cx_oracle://CRM_INDIVIDUAL:pithy-7Z*t2W4@35.157.157.241:1521/?service_name=ecrm")
    
    df_bild_oracle = pd.read_sql(f'''SELECT c.*
    FROM   (SELECT b.*,
                   Row_number()
                     over (
                       PARTITION BY ID, POSNR
                       ORDER BY ID DESC, POSNR DESC) AS SEQNUM
            FROM   (SELECT CAST(PERSONEN_ID_WE AS INTEGER)  AS PERSONEN_ID,
                           CAST(GPAG AS INTEGER) AS GPAG,
                           ABOAUFTRAG_STATUS,
                           CAST(VBELN AS INTEGER) AS VBELN,
                           CAST(POSEX AS INTEGER) AS POSEX,
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
                    FROM   crm_sas_mart.auftrag_abo_mc5 a INNER JOIN my_temp_table ON my_temp_table.pk_auftrags_id = a.VBELN AND my_temp_table.pk_ext_pos_id = a.POSEX
                    WHERE  DRERZ IN ('00002700', '00002770')) b) c
    WHERE SEQNUM = 1''', engine)
    
    df_bild_oracle.personen_id = df_bild_oracle.personen_id.astype('int')
    df_bild_oracle.posex = df_bild_oracle.posex.astype('int')
    df_bild_oracle.vbeln = df_bild_oracle.vbeln.apply(lambda x: int(x))
    
    engine.dispose()
    df_bild = df_bild.merge(df_bild_oracle, left_on=['PK_AUFTRAGS_ID', 'PK_EXT_POS_ID'], right_on=['vbeln', 'posex'], how='left')
    #****Remove BILD subscriptions****
    df_bams_reduced = df_bams[~df_bams.WE_GP_ID.isin(df_bild.gpag.tolist())].copy()   
    #df_bams_reduced.shape
    #*****************# Remove BILD subscriptions in the past 4 years
    
    
    #engine = create_engine("oracle+cx_oracle://CRM_DATA_ANALYTICS:paw-QzurcxN@asbi02db04-vip.linux.asinfra.net:1521/?service_name=ASPROD_BISVC")
    engine = create_engine("oracle+cx_oracle://CRM_INDIVIDUAL:pithy-7Z*t2W4@35.157.157.241:1521/?service_name=ecrm")
    
    df_bild_oracle_past_four_years = pd.read_sql(f'''SELECT c.*
    FROM   (SELECT b.*,
                   Row_number()
                     over (
                       PARTITION BY ID, POSNR
                       ORDER BY ID DESC, POSNR DESC) AS SEQNUM
            FROM   (SELECT CAST(PERSONEN_ID_WE AS INTEGER)  AS PERSONEN_ID,
                           CAST(GPAG AS INTEGER) AS GPAG,
                           ABOAUFTRAG_STATUS,
                           CAST(VBELN AS INTEGER) AS VBELN,
                           CAST(POSEX AS INTEGER) AS POSEX,
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
                    WHERE  DRERZ IN ('00002700', '00002770') AND ABO_VON >= TO_DATE('{datetime.date.today()-datetime.timedelta(days=1460)}', 'YYYY-MM-DD')) b) c
    WHERE SEQNUM = 1''', engine)
    
    df_bild_oracle_past_four_years.personen_id = df_bild_oracle_past_four_years.personen_id.astype('int')
    df_bild_oracle_past_four_years.posex = df_bild_oracle_past_four_years.posex.astype('int')
    df_bild_oracle_past_four_years.vbeln = df_bild_oracle_past_four_years.vbeln.apply(lambda x: int(x))
    
    engine.dispose() 
    # remove subscriptions with subscribed BILD in past 4 years
    df_bams_reduced = df_bams_reduced[~df_bams_reduced.personen_id.isin(df_bild_oracle_past_four_years.personen_id)]
    
    #df_bams_reduced.shape
    #**********# Add age*******************
    engine = create_engine('mssql://DEAXSMAPSQL02.itservices.asudc.net,6202/AboMart?trusted_connection=yes&driver=SQL+Server')
    df_bams_reduced.loc[:, 'WE_GP_ID'].to_sql('#GP_ID_AGE', con=engine, chunksize=200, method='multi', index=False, if_exists='replace')
    df_ages = pd.read_sql(f'select B.WE_GP_ID, BEST_ALTER from AboMart.dbo.TB_AM_DIM_WE_Alter AS A RIGHT JOIN #GP_ID_AGE AS B ON A.WE_GP_ID = B.WE_GP_ID', engine)
    df_ages.sort_values(by=['WE_GP_ID', 'BEST_ALTER'], ascending=[True, False]).drop_duplicates(inplace=True) # business partners may occur multiple times
    engine.dispose()
    
    df_bams_reduced = df_bams_reduced.merge(df_ages, on=['WE_GP_ID'], how='left')
    #df_bams_reduced.shape
    #*********************Add duration of subscription in days*************************
    today = datetime.date.today()
    df_bams_reduced['ABODAUER'] = df_bams_reduced.ABO_GUELTIG_VON.apply(lambda x: (today - x.date()).days)
    #****************Impute some values, drop missing ABODAUER**************************
    df_bams_reduced.dropna(subset=['ABODAUER'], inplace=True)
    df_bams_reduced.ABO_STORNO_JN = df_bams_reduced.ABO_STORNO_JN.apply(lambda x: "0" if x == pd.isna(x) or x == '' else x)
    df_bams_reduced.Zahlweg_Typ1_id.fillna(0, inplace=True)
    df_bams_reduced.Zahlrhythmus_Typ1_id.fillna(-9999, inplace=True)
    df_bams_reduced.ABO_KOMBI_ID = df_bams_reduced.ABO_KOMBI_ID.apply(lambda x: "0" if x == pd.isna(x) or x == '' else x)
    #df_bams_reduced.columns
    #***************Add more features*********************
    df_bams_reduced['Verpflichtung1'] = df_bams_reduced.ABO_AUFTRFORM_ID.str[1:4]
    df_bams_reduced['Verpflichtung2'] = df_bams_reduced.ABO_AUFTRFORM_ID.str[6:9]
    df_bams_reduced['Bula'] = df_bams_reduced.KGS22.str[0:2]
    df_bams_reduced['KGS16'] = df_bams_reduced.KGS22.str[0:17]
    df_bams_reduced.Verpflichtung1 = df_bams_reduced.apply(lambda x: x.Verpflichtung2 if x.Verpflichtung1 == 0 else x.Verpflichtung1, axis='columns')
    
    li_werbeweg = ['AZ', 'BEIL', 'DIREKT', 'EMAIL', 'INT', 'MAIL', 'TM', 'VST']
    df_bams_reduced['WERBEWEG_GRP'] = df_bams_reduced.WERB_WERBEWEG_ID.apply(lambda x: 'SONST' if x not in li_werbeweg else x)
    df_bams_reduced['letzteAbodauer'] = pd.cut(df_bams_reduced.ABODAUER, bins = [0, 182, 365, 728, 1825, 99999999999999999], labels = [182, 365, 728, 1825, 3651])
    #*************Add contact points*****************
    df_bams_reduced['Ansprachedatum2'] = datetime.date.today() # to be improved
    # select a list of people
    df_people = df_bams_reduced[['personen_id', 'Ansprachedatum2']].drop_duplicates().copy()
    # create table with PERSONEN_IDs
    
    Base = declarative_base()
    
    class TEMP_TABLE(Base):
        __tablename__ = "my_temp_table"
        personen_id = Column(Integer, primary_key=True)
        
    #engine = create_engine("oracle+cx_oracle://CRM_DATA_ANALYTICS:paw-QzurcxN@asbi02db04-vip.linux.asinfra.net:1521/?service_name=ASPROD_BISVC")
    engine = create_engine("oracle+cx_oracle://CRM_INDIVIDUAL:pithy-7Z*t2W4@35.157.157.241:1521/?service_name=ecrm")
    
    Base.metadata.drop_all(engine, tables=[TEMP_TABLE.__table__])
    
    Base.metadata.create_all(engine)
    
    connection = cx_Oracle.connect(user="CRM_INDIVIDUAL", password="pithy-7Z*t2W4",
                                   dsn="35.157.157.241:1521/ecrm",
                                   encoding="UTF-8")
    cursor = connection.cursor()
    
    data = df_bams_reduced.loc[:, ['personen_id']].dropna(axis='index').astype('int64').drop_duplicates().values.tolist()
    
    cursor.executemany("insert into my_temp_table (personen_id) values (:1)", data)
    
    connection.commit()
    connection.close()
    
    df_test = pd.read_sql(f'SELECT COUNT(*) AS CNT FROM my_temp_table', engine)
    assert df_test.cnt.iloc[0] > 0 # test for row count larger zero
    engine.dispose()
    # select a list of campaigns where a person (PERSONEN_ID) was addressed only once (CNT == 1) under a specific campaign (DKAMP) 
    # Wall time: 18min 40s
    #cnxn_ora = pyodbc.connect('DRIVER={Oracle in instantclient_19_6};DBQ=asbi02db04-vip.linux.asinfra.net:1521/ASPROD_BISVC;UID=CRM_DATA_ANALYTICS;PWD=paw-QzurcxN;')
    cnxn_ora = pyodbc.connect('DRIVER={Oracle in instantclient_21_3};DBQ=35.157.157.241:1521/ecrm;UID=CRM_INDIVIDUAL;PWD=pithy-7Z*t2W4;')
    cursor_ora = cnxn_ora.cursor()
    
    df_campaigns = pd.read_sql(f'''
    SELECT b.*
    FROM   (SELECT a.PERSONEN_ID,
                   Substr(KAMPAGNE, 1, 9) AS DKAMP,
                   ANSPRACHEDATUM,
                   Count(*)               AS CNT
            FROM   crm_sas_mart.kontakthistorie a INNER JOIN my_temp_table ON my_temp_table.personen_id = a.PERSONEN_ID
            WHERE  VERTRIEBS_ORG = 'BGZS'
                   AND DRUCKERZEUGNISKUERZEL IN ( 'BA', 'BI' )
            GROUP BY a.PERSONEN_ID,
                      Substr(KAMPAGNE, 1, 9),
                      ANSPRACHEDATUM) b
    WHERE  b.CNT = 1
    ''', cnxn_ora)
    
    df_campaigns.PERSONEN_ID = df_campaigns.PERSONEN_ID.astype('int64')
    df_campaigns.rename(columns={'PERSONEN_ID': 'personen_id'}, inplace=True)
    #1.681.547
    #df_campaigns.shape
    df_contacts = df_people.merge(df_campaigns, on=['personen_id'], how='inner')
    df_contacts = df_contacts[df_contacts.Ansprachedatum2 > df_contacts.ANSPRACHEDATUM] # person addressed in the past
    df_contacts = df_contacts.groupby(by=['personen_id', 'Ansprachedatum2']).agg({'DKAMP' : 'count'}).rename(columns={'DKAMP':'Kontakte'}).reset_index(drop=False)
    # merge into original dataset
    df_bams_reduced = df_bams_reduced.merge(df_contacts[['personen_id', 'Kontakte']], on=['personen_id'], how='left')
    # group contact points into new feature
    df_bams_reduced['GRP_Kontakte'] = pd.cut(df_bams_reduced.Kontakte, bins = [0, 1, 2, 5, 10, 20, 99999], labels = [1, 2, 5, 10, 20, 21])
    df_bams_reduced.GRP_Kontakte.value_counts()
    #df_bams_reduced.shape
    #***********Add optin**************
    # retrieve that last optin decision per person
    df_optin = pd.read_sql(f'''
    SELECT b.* FROM (SELECT a.PERSONEN_ID, OPTIN AS PERSONEN_OPTIN,
           ERFASSUNGSDATUM,
           Row_number()
             over (
               PARTITION BY a.PERSONEN_ID, ERFASSUNGSDATUM
               ORDER BY a.PERSONEN_ID, ERFASSUNGSDATUM DESC) AS rn
    FROM crm_sas_mart.personen_optin a INNER JOIN my_temp_table ON my_temp_table.personen_id = a.PERSONEN_ID) b WHERE rn = 1
    ''', cnxn_ora)
    
    df_optin.PERSONEN_ID = df_optin.PERSONEN_ID.astype('int')
    df_optin.PERSONEN_OPTIN = df_optin.PERSONEN_OPTIN.map({'J':1, 'N':0})
    df_optin.rename(columns={'PERSONEN_ID': 'personen_id'}, inplace=True)
    
    df_bams_reduced = df_bams_reduced.merge(df_optin[['personen_id', 'PERSONEN_OPTIN']], on=['personen_id'], how='left')
    df_bams_reduced.PERSONEN_OPTIN.fillna(99, inplace=True)
    df_bams_reduced.PERSONEN_OPTIN.value_counts(dropna=False)
    #df_bams_reduced.shape
    #*************Add previous BamS subscriptions*****************
    engine = create_engine('mssql://DEAXSMAPSQL02.itservices.asudc.net,6202/AboMart?trusted_connection=yes&driver=SQL+Server')
    df_bams_reduced.loc[:, ['personen_id', 'WE_GP_ID']].dropna(axis='index').to_sql('#PERSONS', con=engine, chunksize=200, method='multi', index=False, if_exists='replace')
    df_subscriptions = pd.read_sql(f'''select B.personen_id, B.WE_GP_ID, A.PK_AUFTRAGS_ID, A.PK_EXT_POS_ID, A.ABO_GUELTIG_BIS from AboMart.dbo.TB_AM_ABO_Kennzahlen AS A RIGHT JOIN #PERSONS AS B ON A.WE_GP_ID = B.WE_GP_ID WHERE A.OGR_ID = 6 AND A.ABO_KDAUFART_ID IN ('ZABO', 'LABO', 'ZLAB', 'ZWBZ', 'WBZA', 'LGES', 'ZPKO', 'ZPGE')''', engine)
    #df_subscriptions.rename(columns={'PERSONEN_ID': 'personen_id'}, inplace=True)
    df_subscriptions.personen_id = df_subscriptions.personen_id.astype('int')
    engine.dispose()
    
    df_subscriptions['Ansprachedatum'] = datetime.datetime.today() # to be improved
    df_subscriptions = df_subscriptions[df_subscriptions.Ansprachedatum > df_subscriptions.ABO_GUELTIG_BIS]
    df_subscriptions = df_subscriptions.groupby(by=['personen_id', 'Ansprachedatum']).agg({'WE_GP_ID' : 'count'}).rename(columns={'WE_GP_ID':'Subscriptions'}).reset_index(drop=False)
    df_subscriptions['GRP_Subscriptions'] = pd.cut(df_subscriptions.Subscriptions, bins = [0, 0.999, 1.99999, 2.99999, 3.99999, 4.99999, 5.99999, 999999], labels = [0, 1, 2, 3, 4 ,5 ,6])
    
    df_bams_reduced = df_bams_reduced.merge(df_subscriptions[['personen_id', 'Subscriptions', 'GRP_Subscriptions']], on=['personen_id'], how='left')
    #df_bams_reduced.shape
    #*************And another feature transformation*****
    df_bams_reduced['GRP_Alter'] = pd.cut(df_bams_reduced.BEST_ALTER, bins = [0, 20, 30, 40, 50, 60, 70, 80, 9999], labels = [20, 30, 40, 50, 60, 70, 80, 81])
    df_bams_reduced.GRP_Alter.value_counts()
    #***********Digital subscriptions from M/SD (SAP) via AboMart****************
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
    df_persons = df_bams_reduced.loc[:, ['personen_id', 'WE_GP_ID']].copy()
    df_persons['Ansprachedatum'] = datetime.datetime.today()
    
    # merge
    df_digital_subscriptions = df_digital[['WE_GP_ID', 'PK_AUFTRAGS_ID', 'PK_EXT_POS_ID', 'ABO_GUELTIG_BIS', 'Angebot_Digi', 'VERTRIEBS_ORG_MSD']].merge(df_persons, on=['WE_GP_ID'], how='inner')
    # subset with those who were addresses after subscription ended
    df_digital_subscriptions = df_digital_subscriptions[df_digital_subscriptions.Ansprachedatum > df_digital_subscriptions.ABO_GUELTIG_BIS]
    
    df_digital_subscriptions_agg_bild = df_digital_subscriptions[df_digital_subscriptions.VERTRIEBS_ORG_MSD == 'BGZS'].groupby(by=['personen_id', 'Ansprachedatum']).agg({'WE_GP_ID' : 'count'}).rename(columns={'WE_GP_ID':'ANZ_BILD_digi_MSD'}).reset_index(drop=False)
    df_digital_subscriptions_agg_welt = df_digital_subscriptions[df_digital_subscriptions.VERTRIEBS_ORG_MSD == 'ZGB'].groupby(by=['personen_id', 'Ansprachedatum']).agg({'WE_GP_ID' : 'count'}).rename(columns={'WE_GP_ID':'ANZ_WELT_digi_MSD'}).reset_index(drop=False)
    
    # new aggregated dataset
    df_digital_subscriptions_agg = df_digital_subscriptions_agg_bild[['personen_id', 'ANZ_BILD_digi_MSD']].merge(df_digital_subscriptions_agg_welt[['personen_id', 'ANZ_WELT_digi_MSD']], on=['personen_id'], how='outer').fillna(0) # fillna for occurance of zero
    
    df_bams_reduced = df_bams_reduced.merge(df_digital_subscriptions_agg, on=['personen_id'], how='left')
    #***************Digital subscriptions from CRM DWH (Oracle)****************
    df_oracle_subscription_mapping = pd.read_sql(f'''
    SELECT Personen_ID_D AS PERSONEN_ID_WE, Personen_ID_P AS personen_id
    FROM crm_sas_mart.REFERENZ_PRINT_DIGITAL
    ''', cnxn_ora)
    
    df_oracle_subscription_mapping.PERSONEN_ID = df_oracle_subscription_mapping.PERSONEN_ID.astype('int')
    df_oracle_subscription_mapping.PERSONEN_ID_WE = df_oracle_subscription_mapping.PERSONEN_ID_WE.astype('int')
    df_oracle_subscription_mapping.rename(columns={'PERSONEN_ID': 'personen_id'}, inplace=True)
    # erroneous mapping as only a few entries can be mapped
    df_part_a = df_bams_reduced[['personen_id', 'PK_AUFTRAGS_ID', 'ABO_GUELTIG_BIS']].merge(df_oracle_subscription_mapping, on=['personen_id'], how='left')
    
    # create table with PERSONEN_ID_WE
    Base = declarative_base()
    
    class TEMP_TABLE(Base):
        __tablename__ = "my_temp_table"
        PERSONEN_ID_WE = Column(Integer, primary_key=True)
    
    #engine = create_engine("oracle+cx_oracle://CRM_DATA_ANALYTICS:paw-QzurcxN@asbi02db04-vip.linux.asinfra.net:1521/?service_name=ASPROD_BISVC")
    engine = create_engine("oracle+cx_oracle://CRM_INDIVIDUAL:pithy-7Z*t2W4@35.157.157.241:1521/?service_name=ecrm")
    
    Base.metadata.drop_all(engine, tables=[TEMP_TABLE.__table__])
    
    Base.metadata.create_all(engine)
    connection = cx_Oracle.connect(user="CRM_INDIVIDUAL", password="pithy-7Z*t2W4",
                                   dsn="35.157.157.241:1521/ecrm",
                                   encoding="UTF-8")
    cursor = connection.cursor()
    
    data = df_part_a.loc[:, ['PERSONEN_ID_WE']].dropna(axis='index').astype('int64').drop_duplicates().values.tolist()
    
    cursor.executemany("insert into my_temp_table (PERSONEN_ID_WE) values (:1)", data)
    
    connection.commit()
    connection.close()
    
    df_test = pd.read_sql(f'SELECT COUNT(*) AS CNT FROM my_temp_table', engine)
    assert df_test.cnt.iloc[0] > 0 # test for row count larger zero
    
    engine.dispose()
    # workarounded and fast
    
    df_part_b = pd.read_sql('SELECT d.PERSONEN_ID_WE, d.vbeln_basis AS vbeln_basis_d, d.vbeln AS vbeln_d, d.abo_von AS abo_von_d, d.abo_bis AS abo_bis_d, d.aboauftrag_status as aboauftrag_status_d, d.material AS material_d, d.bundle AS bundle_d, e.vertriebs_org AS vertriebs_org_d, e.bezeichnung AS bezeichnung_d FROM crm_sas_mart.auftrag_abo_sc5 d INNER JOIN my_temp_table ON my_temp_table.PERSONEN_ID_WE = d.PERSONEN_ID_WE LEFT JOIN crm_sas_mart.lov_vertriebs_org e ON d.MATERIAL=e.MATERIAL', cnxn_ora)
    df_part_b.PERSONEN_ID_WE = df_part_b.PERSONEN_ID_WE.astype('int')
    df_full = df_part_a.merge(df_part_b, on='PERSONEN_ID_WE', how='inner')
    df_full.info()
    #
    df_full['Ansprachedatum'] = datetime.datetime.today()
    df_full = df_full[df_full.Ansprachedatum > df_full.ABO_BIS_D] # as in old script
    df_full = df_full[['personen_id', 'Ansprachedatum', 'VBELN_D', 'VERTRIEBS_ORG_D', 'PK_AUFTRAGS_ID']]
    
    df_full_agg_bild = df_full[df_full.VERTRIEBS_ORG_D == 'BD'].groupby(by=['personen_id', 'Ansprachedatum']).agg({'PK_AUFTRAGS_ID' : 'count'}).rename(columns={'PK_AUFTRAGS_ID':'ANZ_BILD_digi_SD'}).reset_index(drop=False)
    df_full_agg_welt = df_full[df_full.VERTRIEBS_ORG_D == 'ZGB'].groupby(by=['personen_id', 'Ansprachedatum']).agg({'PK_AUFTRAGS_ID' : 'count'}).rename(columns={'PK_AUFTRAGS_ID':'ANZ_WELT_digi_SD'}).reset_index(drop=False)
    df_full_agg_others = df_full[~df_full.VERTRIEBS_ORG_D.isin(['ZGB','BD',''])].groupby(by=['personen_id', 'Ansprachedatum']).agg({'PK_AUFTRAGS_ID' : 'count'}).rename(columns={'PK_AUFTRAGS_ID':'ANZ_SO_digi_SD'}).reset_index(drop=False)
    
    # new aggregated dataset
    df_full_agg = df_full_agg_bild.merge(df_full_agg_welt, on=['personen_id'], how='outer')
    df_full_agg = df_full_agg.merge(df_full_agg_others, on=['personen_id'], how='outer')
    df_bams_reduced = df_bams_reduced.merge(df_full_agg, on=['personen_id'], how='left')
    #df_bams_reduced.shape
    df_bams_reduced['ANZ_DIGI'] = df_bams_reduced.apply(lambda x: 1 if pd.notna(x.ANZ_WELT_digi_MSD) or pd.notna(x.ANZ_WELT_digi_SD) or pd.notna(x.ANZ_BILD_digi_SD) or pd.notna(x.ANZ_BILD_digi_MSD) or pd.notna(x.ANZ_SO_digi_SD) else 0, axis='columns')
    df_bams_reduced.to_pickle('data_inference_raw_final_v1.pkl', protocol = 4)
    df_bams_reduced.info()
    
    df_bams_reduced_inference_final = df_bams_reduced[['ANZ_SO_digi_SD','ANZ_BILD_digi_MSD','ANZ_BILD_digi_SD','ANZ_WELT_digi_SD','ANZ_WELT_digi_MSD', 'ANZ_DIGI', 'Kontakte', 'BEST_ALTER', 'Subscriptions', 'PERSONEN_OPTIN', 'WERBEWEG_GRP', 'ABODAUER']].copy()
    df_bams_reduced_inference_final.to_pickle('data_inference_final_final_v1.pkl', protocol = 4)
    df_bams_reduced[['personen_id']].to_pickle('data_inference_final_final_personen_v1.pkl', protocol = 4)

    return