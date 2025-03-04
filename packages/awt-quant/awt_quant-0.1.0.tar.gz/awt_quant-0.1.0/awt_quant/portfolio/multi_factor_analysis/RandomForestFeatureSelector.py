from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.feature_selection import RFE
from sklearn.inspection import permutation_importance
from sklearn.utils import resample
import pandas as pd
# import numpy as np
from .FactorConstructor import FactorConstructor 
from .DataCollector import DataCollector  
# from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.vector_ar.vecm import coint_johansen
# import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

class RandomForestFeatureSelector:
    def __init__(self, factor_constructor, data_collector):
        self.factor_constructor = factor_constructor
        self.data_collector = data_collector 

    def fetch_factors(self):
        return self.factor_constructor.get_all_factors()
    
    def fetch_portfolio_returns(self):
        returns_data = self.data_collector.calculate_historical_returns(self.data_collector.fetch_price_data())
        portfolio_returns = pd.DataFrame({ticker: df['Daily_Return'] for ticker, df in returns_data.items()}).mean(axis=1)
        return portfolio_returns

    def check_multicollinearity(self, df):
        # calculate the variance inflation factor (VIF) for each factor
        # ranked from 1, where 1 denotes no correlation and g.t. 5 denotes high correlation
        vif_data = pd.DataFrame() 
        vif_data["feature"] = df.columns
        vif_values = []
        for i in range(len(df.columns)):
            x_var = df.columns[i]
            y_vars = df.columns.drop(x_var)           
            x = df[x_var]
            y = df[y_vars]
            model = LinearRegression()
            model.fit(y, x)           
            vif = 1 / (1 - model.score(y, x))
            vif_values.append(vif)
            
        vif_data["VIF"] = vif_values
        
        # features with a VIF greater than 5 are usually considered to have high multicollinearity
        high_vif_features = vif_data[vif_data["VIF"] > 5]["feature"].tolist()
        return high_vif_features # returns a list of factors are have high VIF scores => multicollinear factors

    def check_cointegration(self, df):
        johansen_test = coint_johansen(df, det_order=0, k_ar_diff=1)
        trace_stat = johansen_test.lr1
        trace_crit_vals = johansen_test.cvt[:, 1]  # 5% critical value
        eigen_stat = johansen_test.lr2
        eigen_crit_vals = johansen_test.cvm[:, 1]  # 5% critical value
        trace_significance = trace_stat > trace_crit_vals
        eigen_significance = eigen_stat > eigen_crit_vals
        results = {
            'Trace Statistics': trace_stat,
            '5% Critical Value (Trace)': trace_crit_vals,
            'Significance (Trace)': trace_significance,
            'Eigenvalue Statistics': eigen_stat,
            '5% Critical Value (Eigen)': eigen_crit_vals,
            'Significance (Eigen)': eigen_significance
        }   
        return results

    def feature_importance(self, df):
        X = df
        y = self.fetch_portfolio_returns().reindex(X.index).dropna()
        X = X.reindex(y.index)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        # predicting and evaluating the model on the test set
        y_pred = model.predict(X_test)
        # MSE is a measure of the average of the squares of the errors. 
        # it is a mesaure of the quality of an estimator, values closer to zero indicates low error rates.        
        mse = mean_squared_error(y_test, y_pred) 
        r2 = r2_score(y_test, y_pred)
        print(f"Mean Squared Error on test set: {mse}")
        print(f"R-squared on test set: {r2}")
        feature_importances = pd.DataFrame({'Feature': X.columns, 'Importance': model.feature_importances_})
        return feature_importances.sort_values('Importance', ascending=False)
    
    def select_important_features(self, df):
        X = df
        y = self.fetch_portfolio_returns().reindex(X.index).dropna()
        X = X.reindex(y.index)     
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        rfe = RFE(estimator=model, n_features_to_select=5)  # Selects top 5 factors. 
        fit = rfe.fit(X, y)
        important_features = [feat for feat, support in zip(X.columns, fit.support_) if support]
        return important_features

    
    # Might want to implement a logging feature to keep track of model's performance over time, and feature importances; model evaluation(?)

# Example 
if __name__ == "__main__":
    factor_constructor = FactorConstructor("2020-01-01", "2021-01-01")
    # hypothetical portfolio, with returns from specified tickers
    data_collector = DataCollector(["AAPL", "MSFT", "GOOGL", "RTX", "LMT", "FANG"], "2020-01-01", "2021-01-01")
    selector = RandomForestFeatureSelector(factor_constructor, data_collector)
    factors_df = selector.fetch_factors()
    print("fetched factors:")
    print(factors_df.head())
    
    # print("Stationarity Check:")
    # print(selector.check_stationarity(factors_df))
    # print("Outliers Check:")
    # selector.check_outliers(factors_df)
    # print("Missing Values Check:")
    # print(selector.check_missing_values(factors_df))
    # print("Sample Size Check:")
    # print(selector.check_sample_size(factors_df))
    
    portfolio_returns = selector.fetch_portfolio_returns()
    print("fetched portfolio returns:")
    print(portfolio_returns.head())
    
    high_vif_features = selector.check_multicollinearity(factors_df)
    print("factors with high multicollinearity:")
    print(high_vif_features)
    
    cointegration_results = selector.check_cointegration(factors_df)
    print("cointegration results:")
    for key, value in cointegration_results.items():
        print(f"{key}: {value}")
    
    # need to address assumption below 
    feature_importances = selector.feature_importance(factors_df)
    print("factor importances:")
    print(feature_importances)