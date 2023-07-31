#%%[markdown]
# import libraries
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
import re

def no_accent_vietnamese(s):
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)
    return s

#%%[markdown]
# import weather data
df_raw = pd.read_csv('VN_weather_112011_3312023_raw.csv', index_col=0)
df = df_raw.copy()
df.info()

# %%[markdown]
# check null
df.isnull().sum()

# %%[markdown]
# view sample data
df = df.drop(df.columns[1:3], axis=1)
df.head()

# %%
# check unique values
for col_name in df.columns:
    print(f'{col_name}: \n{df[col_name].unique()}\n')
    
# %%
df = df.loc[:, ['Time', 'Forecast', 'Rain', 'Rain %', 'Cloud', 'Pressure', 'Wind', 'Gust', 'Dir', 'Date', 'Area']]

# %%[markdown]
# re-allocate columns to corresponding value and clean up
df['Temperature'] = df['Time'].str[6:].str.extract(pat=r'([\d.]+)')
df['Time'] = df['Time'].str[:6]

for col_name in df.columns[2:9]:
    df[col_name] = df[col_name].str.extract(pat=r'([\d.]+)')

# %%[markdown]
# correct columns name
df = df.loc[:, ['Time', 'Temperature', 'Rain', 'Forecast', 'Rain %', 'Cloud', 'Pressure', 'Wind', 'Gust', 'Dir', 'Date', 'Area']]

df.columns = ['Time', 'Temperature', 'Forecast Temperature', 'Forecast', 'Rain', 'Rain %', 'Cloud', 'Pressure', 'Wind', 'Gust', 'Date', 'Area']

# %%[markdown]
# view sample data
df.head()
df.isnull().sum()


# %%[markdown]
# export Cleaned-up data of VN Weather to csv
df.to_csv('VN_weather_2011_2023_clean.csv')

# %%[markdown]
# create weather data by month
df['Month_Year'] = pd.to_datetime(pd.Series(df['Date'])).dt.strftime('%m/%Y')
unique_areas = df['Area'].unique()
df_monthly = pd.DataFrame(None, columns=['Area', 'Date', 'Temperature', 'Rain', 'Rain_PCT', 'Cloud', 'Pressure', 'Wind', 'Gust'])
unique_month = df["Month_Year"].unique()

for a_area in unique_areas:
    for a_date in unique_month:
        mask = ((df['Area']==a_area) & (df['Month_Year']==a_date))
        a_temperature = df[mask]['Temperature'].astype('float').mean()
        a_rain = df[mask]['Rain'].astype('float').mean()
        a_rain_pct = df[mask]['Rain %'].astype('float').mean()
        a_cloud = df[mask]['Cloud'].astype('float').mean()
        a_pressure = df[mask]['Pressure'].astype('float').mean()
        a_wind = df[mask]['Wind'].astype('float').mean()
        a_gust = df[mask]['Gust'].astype('float').mean()
        
        df_temp = pd.DataFrame(None)
        df_temp = df_temp.assign( Area = [a_area],
                        Date = [a_date],
                        Temperature = [a_temperature],
                        Rain = [a_rain],
                        Rain_PCT = [a_rain_pct],
                        Cloud = [a_cloud],
                        Pressure = [a_pressure],
                        Wind = [a_wind],
                        Gust = [a_gust]
                        )
        df_monthly = pd.concat([df_monthly, df_temp])

df_monthly

df_monthly.to_csv('VN_weather_112011_3312023_monthly.csv')

# create weather data by year
df_monthly['Year'] = df_monthly['Date'].str[3:]
unique_areas = df_monthly['Area'].unique()
df_yearly = pd.DataFrame(None, columns=['Area', 'Date', 'Temperature', 'Rain', 'Rain_PCT', 'Cloud', 'Pressure', 'Wind', 'Gust'])
unique_year = df_monthly["Year"].unique()

for a_area in unique_areas:
    for a_date in unique_year:
        mask = ((df_monthly['Area']==a_area) & (df_monthly['Year']==a_date))
        a_temperature = df_monthly[mask]['Temperature'].astype('float').mean()
        a_rain = df_monthly[mask]['Rain'].astype('float').mean()
        a_rain_pct = df_monthly[mask]['Rain_PCT'].astype('float').mean()
        a_cloud = df_monthly[mask]['Cloud'].astype('float').mean()
        a_pressure = df_monthly[mask]['Pressure'].astype('float').mean()
        a_wind = df_monthly[mask]['Wind'].astype('float').mean()
        a_gust = df_monthly[mask]['Gust'].astype('float').mean()
        
        df_temp = pd.DataFrame(None)
        df_temp = df_temp.assign( Area = [a_area],
                        Date = [a_date],
                        Temperature = [a_temperature],
                        Rain = [a_rain],
                        Rain_PCT = [a_rain_pct],
                        Cloud = [a_cloud],
                        Pressure = [a_pressure],
                        Wind = [a_wind],
                        Gust = [a_gust]
                        )
        df_yearly = pd.concat([df_yearly, df_temp])

df_yearly

# %%
df_yearly.to_csv('VN_weather_112011_3312023_yearly.csv')

# %%[markdown]
# import PM 2.5 data
df_25_raw = pd.read_csv('VN_PM25_raw.csv')
df_25_raw.info()

# %%[markdown]
# check null
df_25_raw.isnull().sum()

# %%[markdown]
# drop null rows
df_25_raw = df_25_raw.dropna(subset='Exposure Id')

# %%[markdown]
# check null again
df_25_raw.isnull().sum()

# %%[markdown]
# drops 2 null columns
df_25_raw = df_25_raw.drop(columns=['Unnamed: 0', 'Exposure Lower', 'Exposure Upper'])

# %%[markdown]
# clean up
for col_name in df_25_raw.columns:
    df_25_raw[col_name] = df_25_raw[col_name].astype('string').str.strip('="')

# %%
df_25_raw.head()

# %%[markdown]
# analyse
for col_name in df_25_raw.columns:
    print(df_25_raw[col_name].value_counts())

# %%[markdown]
# export cleaned-up data of PM2.5 to csv
df_25_raw.to_csv(f'VN_PM_25.csv')

# %%
df_monthly
# %%
df_yearly

# %%
df_humidity = pd.read_csv('VN_weather_summary_with_humidity_yearly.csv', index_col=0)
df_pm25 = pd.read_csv('VN_PM_25_clean.csv', index_col=0)

for col_name in df_humidity.columns[1:8]:
    df_humidity[col_name] = df_humidity[col_name].str.extract(pat=r'([\d.]+)')

df_humidity['Area'] = df_humidity['Area'].str.lower().str.replace('ho-chi-minh-city', 'ho-chi-minh')
df_pm25['Year'] = df_pm25['Year'].astype('int')
df_pm25['City'] = df_pm25['City'].str.lower().str.replace(' ', '-').str.replace('hanoi', 'ha-noi').str.replace('ho-chi-minh-city', 'ho-chi-minh').str.replace('phan-rang---thap-cham', 'phan-rang').str.replace('dalat', 'da-lat').str.replace('tra-vinh-city', 'tra-vinh')
df_pm25['City'] = df_pm25['City'].apply(no_accent_vietnamese)
df_pm25['City'].unique()
df_humidity['Area'].unique()

df_VN_yearly = pd.merge(left = df_humidity, right=df_pm25, how='inner', left_on=['Area', 'Year'], right_on=['City', 'Year'])

df_VN_yearly = df_VN_yearly.loc[:, ['Year', 'Max', 'Min', 'Wind', 'Rain', 'Humidity', 'Cloud', 'Pressure', 'Exposure Mean', 'Area']]

df_VN_yearly.columns = df_VN_yearly.columns.str.replace('Max', 'Temp Max').str.replace('Min', 'Temp Min')

df_VN_yearly.to_csv('VN_pm25_humidity_2009_2019_yearly.csv')

# %%
df_pm25_hcm = pd.read_csv('ho-chi minh city us consulate, vietnam-air-quality.csv')
mask = df_pm25_hcm['date'].str[:4] == '2020'
df_pm25_hcm.info()
pm25_hcm_2020 = df_pm25_hcm[mask]
df_pm25_hcm['date'] = pd.to_datetime(df_pm25_hcm['date']).dt.strftime('%m/%d/%Y')
pm25_hcm_2020.head()


# %%
df.head()
df_hcm_meteorological = df[(df['Area'] == 'ho-chi-minh') & (df['Date'].str[-4:] == '2020')]

df_hcm_meteorological.info()

# %%
df_hcm_meteorological.head()

df_hcm = df_hcm_meteorological.groupby('Date').agg(['mean', 'min', 'max']).reset_index()
df_hcm = pd.merge(left=df_pm25_hcm, right=df_hcm, how='inner', left_on='date', right_on='Date')

col_name = ['date', 'pm25', 'Date', 'Temperature_mean', 'Temperature_min',
       'Temperature_max', 'Forecast Temperature_mean',
       'Forecast Temperature_min', 'Forecast Temperature_max',
       'Rain_mean', 'Rain_min', 'Rain_max', 'Rain %_mean',
       'Rain %_min', 'Rain %_max', 'Cloud_mean', 'Cloud_min',
       'Cloud_max', 'Pressure_mean', 'Pressure_min', 'Pressure_max',
       'Wind_mean', 'Wind_min', 'Wind_max', 'Gust_mean', 'Gust_min',
       'Gust_max']

df_hcm.columns = col_name

col_name = df_hcm.columns[:2].to_list() + df_hcm.columns[3:].to_list()
df_hcm = df_hcm[col_name]

df_hcm.to_csv('VN_HCM_2020.csv')

# %%
df_pm25 = pd.read_csv('VN_PM_25_clean.csv', index_col=0)
df_yearly = pd.read_csv('VN_weather_112011_3312023_yearly_clean.csv', index_col=0)

df_pm25['City'] = df_pm25['City'].apply(no_accent_vietnamese).str.lower().str.replace(' ', '-').str.replace('hanoi', 'ha-noi').str.replace('ho-chi-minh-city', 'ho-chi-minh').str.replace('phan-rang---thap-cham', 'phan-rang').str.replace('dalat', 'da-lat').str.replace('tra-vinh-city', 'tra-vinh').str.replace('chaudok-city', 'chau-doc').str.replace('haiphong', 'hai-phong').str.replace('quang-minh', 'quang-ninh').str.replace('pleiku', 'play-cu')
df_pm25['City'].unique()

# %%
df_pm25['Year'] = df_pm25['Year'].astype('int')

# %%
df_pm25_use = df_pm25.loc[:, ['City', 'Year', 'Exposure Mean']]
df_pm25_use

# %%
df_yearly_pm25 = pd.merge(left=df_yearly, right=df_pm25_use, right_on=['City', 'Year'], left_on=['Area', 'Date'], how='inner').drop(columns=['City', 'Year', 'Rain_PCT']).dropna(axis=0)

# %%
df_yearly_pm25.to_csv('VN_yearly_pm25.csv')

# %%
df_population = pd.read_csv('VN_population.csv', index_col=0)
df_yearly_pm25 = pd.read_csv('VN_yearly_pm25.csv', index_col=0)

# %%

df_yearly_pm25_population = pd.merge(left=df_yearly_pm25, right=df_population, left_on=['Area', 'Date'], right_on=['Area', 'Year'], how='inner')

# %%
df_yearly_pm25_population

# %%
df_yearly_pm25_population.drop(columns=['Year']).to_csv('VN_yearly_pm25_population.csv')

# %%
