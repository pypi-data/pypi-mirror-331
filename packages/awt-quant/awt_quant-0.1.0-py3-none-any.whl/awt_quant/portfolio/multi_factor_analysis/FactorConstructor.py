import pandas as pd
# import numpy as np
import yfinance as yf

class FactorConstructor:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def calculate_HML(self, start_date, end_date):
        high_data = yf.download("^GSPC", start=start_date, end=end_date)['High']
        low_data = yf.download("^GSPC", start=start_date, end=end_date)['Low']
        hml = high_data - low_data
        return hml.dropna()

    def calculate_SMB(self, start_date, end_date):
        small_cap_data = yf.download("^RUT", start=start_date, end=end_date) # Russell 2000 Index, small-cap
        large_cap_data = yf.download("^GSPC", start=start_date, end=end_date) # S&P 500 
        small_cap_return = small_cap_data['Adj Close'].pct_change().dropna()
        large_cap_return = large_cap_data['Adj Close'].pct_change().dropna()
        smb = small_cap_return - large_cap_return
        return smb.dropna()

    def calculate_MKT(self, start_date, end_date):
        market_data = yf.download("^GSPC", start=start_date, end=end_date)
        mkt = market_data['Adj Close'].pct_change().dropna()
        return mkt

    def calculate_momentum(self, start_date, end_date):
        data = yf.download("^GSPC", start=start_date, end=end_date)
        daily_return = data['Adj Close'].pct_change().dropna()
        momentum = daily_return.rolling(window=20).mean().dropna()
        return momentum

    def calculate_volatility(self, start_date, end_date):
        data = yf.download("^GSPC", start=start_date, end=end_date)
        daily_return = data['Adj Close'].pct_change().dropna()
        volatility = daily_return.rolling(window=20).std().dropna()
        return volatility

    def get_all_factors(self):
        hml = self.calculate_HML(self.start_date, self.end_date)
        smb = self.calculate_SMB(self.start_date, self.end_date)
        mkt = self.calculate_MKT(self.start_date, self.end_date)
        momentum = self.calculate_momentum(self.start_date, self.end_date)
        volatility = self.calculate_volatility(self.start_date, self.end_date)
        
        factors_df = pd.concat([hml, smb, mkt, momentum, volatility], axis=1, keys=['HML', 'SMB', 'MKT', 'Momentum', 'Volatility']).dropna()
        return factors_df

# eg 
if __name__ == "__main__":
    start_date = "2020-01-01"
    end_date = "2021-01-01"
    constructor = FactorConstructor(start_date, end_date)
    
    hml_data = constructor.calculate_HML(start_date, end_date)
    smb_data = constructor.calculate_SMB(start_date, end_date)
    mkt_data = constructor.calculate_MKT(start_date, end_date)
    momentum_data = constructor.calculate_momentum(start_date, end_date)
    volatility_data = constructor.calculate_volatility(start_date, end_date)

    print("HML Data:")
    print(hml_data.head())
    print("SMB Data:")
    print(smb_data.head())
    print("MKT Data:")
    print(mkt_data.head())
    print("Momentum Data:")
    print(momentum_data.head())
    print("Volatility Data:")
    print(volatility_data.head())