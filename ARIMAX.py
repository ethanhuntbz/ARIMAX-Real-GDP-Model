import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

#I highly reccomend reading my white paper before looking at the code. There are a lot of nuances that are needed to understand some of the code, and it's fully explained there. 
#Citations for all features I learned within these libraries can be found in the white paper

# DATA Imported from excel. The data was in wide format, so it needed to be shaped to long format. Afterwards, we can extract the columns and expand to wide.
data = pd.read_excel(INSERT FILE PATH HERE)

# .melt() widens data. Id variables specify the entities (which, in our case, are countries), var name creates the year column, and value name creates the estimates (measurements such as GDP) column.
panel_data = pd.melt(data,
                     id_vars=["WEO Country Code", "ISO", "WEO Subject Code", "Country",
                              "Subject Descriptor", "Subject Notes", "Units", "Scale", 
                              "Country/Series-specific Notes"], 
                     var_name='Year', value_name='Estimates')

# Drop missing values and convert columns to numeric and drops missing observations. We can't shape to wide if this isn't the case. 
panel_data = panel_data.dropna(subset=['Estimates'])
panel_data['Estimates'] = pd.to_numeric(panel_data['Estimates'], errors='coerce')
panel_data['Year'] = pd.to_numeric(panel_data['Year'], errors='coerce')

# Pivot the data to wide format. It will separate measurements and put them in a format we can regress. I named the data reg because its the final regression data
reg = panel_data.pivot_table(index=["WEO Country Code", "ISO", "Country", "Year"], 
                             columns="WEO Subject Code", values="Estimates").reset_index()

# Used unique_values = reg['ISO'].unique() to find unique values. We then loop through them to create a neat print out for the user. 

country_codes = [
    'USA', 'GBR', 'AUT', 'BEL', 'DNK', 'FRA', 'DEU', 'SMR', 'ITA', 'LUX', 'NLD', 'NOR',
    'SWE', 'CHE', 'CAN', 'JPN', 'AND', 'FIN', 'GRC', 'ISL', 'IRL', 'MLT', 'PRT', 'ESP',
    'TUR', 'AUS', 'NZL', 'ZAF', 'ARG', 'BOL', 'BRA', 'CHL', 'COL', 'CRI', 'DOM', 'ECU',
    'SLV', 'GTM', 'HTI', 'HND', 'MEX', 'NIC', 'PAN', 'PRY', 'PER', 'URY', 'VEN', 'ATG',
    'BHS', 'ABW', 'BRB', 'DMA', 'GRD', 'GUY', 'BLZ', 'JAM', 'PRI', 'KNA', 'LCA', 'VCT',
    'SUR', 'TTO', 'BHR', 'CYP', 'IRN', 'IRQ', 'ISR', 'JOR', 'KWT', 'LBN', 'OMN', 'QAT',
    'SAU', 'SYR', 'ARE', 'EGY', 'YEM', 'WBG', 'AFG', 'BGD', 'BTN', 'BRN', 'MMR', 'KHM',
    'LKA', 'TWN', 'HKG', 'IND', 'IDN', 'TLS', 'KOR', 'LAO', 'MAC', 'MYS', 'MDV', 'NPL',
    'PAK', 'PLW', 'PHL', 'SGP', 'THA', 'VNM', 'DJI', 'DZA', 'AGO', 'BWA', 'BDI', 'CMR',
    'CPV', 'CAF', 'TCD', 'COM', 'COG', 'COD', 'BEN', 'GNQ', 'ERI', 'ETH', 'GAB', 'GMB',
    'GHA', 'GNB', 'GIN', 'CIV', 'KEN', 'LSO', 'LBR', 'LBY', 'MDG', 'MWI', 'MLI', 'MRT',
    'MUS', 'MAR', 'MOZ', 'NER', 'NGA', 'ZWE', 'RWA', 'STP', 'SYC', 'SEN', 'SLE', 'SOM',
    'NAM', 'SDN', 'SSD', 'SWZ', 'TZA', 'TGO', 'TUN', 'UGA', 'BFA', 'ZMB', 'SLB', 'FJI',
    'KIR', 'NRU', 'VUT', 'PNG', 'WSM', 'TON', 'MHL', 'FSM', 'TUV', 'ARM', 'AZE', 'BLR',
    'ALB', 'GEO', 'KAZ', 'KGZ', 'BGR', 'MDA', 'RUS', 'TJK', 'CHN', 'TKM', 'UKR', 'UZB',
    'CZE', 'SVK', 'EST', 'LVA', 'SRB', 'MNE', 'HUN', 'LTU', 'MNG', 'HRV', 'SVN', 'MKD',
    'BIH', 'POL', 'UVK', 'ROU'
]

count = 0
for i in range(0, len(country_codes)):
    count = count + 1
    print(country_codes[i], end=" ")

    if count % 25 == 0:
        print(country_codes[i], end=" ")
        print() 

print("")
print("")
choice = input("Enter the country code for the country you would like to forecast: ")

# This filters the dataset so we can forecast by the user's choice.
reg = reg[reg['ISO'] == choice]

# Remove projections beyond 2024. The IMF included their own projections along with the measurements for previous years.
reg = reg[reg['Year'] <= 2024]

# Set index to Year. We want python to know the time increments we are using.
reg = reg.set_index("Year")

# An Augmented Dickey-Fuller test tells us if our data is stationary. This is important to determine the amount of differencing. This is the "d" term in ARIMAX
#This code allows the user to pick their level of differencing.. 

adf = adfuller(reg['NGDP_R'])
print('ADF Statistic: %f' % adf[0])
print('p-value: %f' % adf[1])

ans = input("Do you want to difference the data? Y/N: ")
if ans == "Y":
    reg['NGDP_R_diff'] = reg['NGDP_R'].diff()

    adf = adfuller(reg['NGDP_R_diff'].dropna())
    print('ADF Statistic: %f' % adf[0])
    print('p-value: %f' % adf[1])

    ans2 = input("Do you want to difference the data again? Y/N: ")

    if ans2 == "Y":
        reg['NGDP_R_diff'] = reg['NGDP_R_diff'].diff()

        adf = adfuller(reg['NGDP_R_diff'].dropna())
        print('ADF Statistic: %f' % adf[0])
        print('p-value: %f' % adf[1])
        d = 2
    else:
        d = 1
else:
    d = 0

# These plots determine our Autoregressive/AR(p) and Moving Average/MA(q) terms. The user will interpret the plots to determine these.
plot_pacf(reg['NGDP_R'].dropna(), lags=20)
plt.show()

plot_acf(reg['NGDP_R'].dropna(), lags=20)
plt.show()

p = int(input("Enter the number of AR terms: "))
q = int(input("Enter the number of MA terms: "))

exog_vars = ['PCPI', 'TM_RPCH', 'TX_RPCH', 'LUR', 'LP', 'GGR']

# Drop null values in exogenous variables
reg = reg.dropna(subset=['NGDP_R'] + exog_vars)

# We want to split the data into training and testing sets. 
train_size = int(len(reg) * 0.8)  
train, test = reg.iloc[:train_size], reg.iloc[train_size:]

# Train SARIMAX model using only the training data (80% of the data)
model = SARIMAX(train["NGDP_R"], exog=train[exog_vars], order=(p, d, q))  
model_fit = model.fit()

# Forecast using the test set's exogenous variables
forecast = model_fit.forecast(steps=len(test), exog=test[exog_vars])  

# Ploting the data
plt.figure(figsize=(14,7))
plt.plot(train.index, train["NGDP_R"], label='Train Data', color='blue')  
plt.plot(test.index, test["NGDP_R"], label='Test Data', color='green')  
plt.plot(test.index, forecast, label='Forecast (Test Set)', color='orange') 

plt.title('SARIMAX Forecast with Train and Test Data')
plt.xlabel('Year')
plt.ylabel('Real GDP (NGDP_R)')
plt.legend()
plt.show()
