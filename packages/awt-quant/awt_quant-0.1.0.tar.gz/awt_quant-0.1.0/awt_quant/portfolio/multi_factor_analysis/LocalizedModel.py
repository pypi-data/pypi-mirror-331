from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import TimeSeriesSplit
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

class LocalizedModel:
    def __init__(self, clustered_data, returns_df):
        self.clustered_data = clustered_data
        self.returns_df = returns_df  
        self.results = {}
        
    def calculate_cluster_returns(self, cluster_id):
        cluster_assets = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
        if cluster_assets.empty:
            print(f"Warning: Cluster {cluster_id} has no valid target values.")
            return None
        return self.returns_df.loc[cluster_assets.index]  # using portfolio returns as the target
   
    def plot_residuals(self, y_test, y_pred, cluster_id):
        residuals = y_test - y_pred
        plt.figure(figsize=(12, 6))
        plt.scatter(y_test, residuals)
        plt.axhline(0, color='red', linestyle='--')
        plt.xlabel("Actual Returns")
        plt.ylabel("Residuals")
        plt.title(f"Residuals Plot for Cluster {cluster_id}")
        plt.show()
        
    def plot_coefficient_importance(self, factor_significance, cluster_id):
        plt.figure(figsize=(12, 6))
        sns.barplot(x="Coefficient", y="Factor", data=factor_significance.sort_values("Coefficient", ascending=False))
        plt.xlabel("Coefficient Value")
        plt.ylabel("Factor")
        plt.title(f"Coefficient Importance for Cluster {cluster_id}")
        plt.show()
   
    def train_model_for_cluster(self, cluster_id):
        print(f"Training model for Cluster {cluster_id}...")
        cluster_data = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
        cluster_returns = self.calculate_cluster_returns(cluster_id)
        
        if cluster_returns is None:
            print(f"Warning: No valid returns for Cluster {cluster_id}. Skipping this cluster.")
            return
        
        X = cluster_data.drop(columns=['Cluster'])
        # average returns across all assets in the cluster -> model is single-output; easier to interpret.
        y = cluster_returns.mean(axis=1)  

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"MSE for Cluster {cluster_id}: {mse}")
        print(f"R2 Score for Cluster {cluster_id}: {r2}")
        
        # Factor significance/significance 
        print(f"\nFactor Significance for Cluster {cluster_id}:")
        # df paris each factor with its corresponding coefficient
        factor_significance = pd.DataFrame({"Factor": X_train.columns, "Coefficient": model.coef_})
        print(factor_significance)   
        
        plt.figure(figsize=(12, 6))
        plt.scatter(y_test, y_pred)
        
        # ideal line
        min_val = np.min([np.min(y_test), np.min(y_pred)])
        max_val = np.max([np.max(y_test), np.max(y_pred)])
        ideal_line = np.linspace(min_val, max_val, 100)
        plt.plot(ideal_line, ideal_line, '--', color='red', label='Ideal Line')
        plt.legend()
        
        plt.xlabel("Actual Returns")
        plt.ylabel("Predicted Returns")
        plt.title(f"Actual vs Predicted Returns for Cluster {cluster_id}")
        plt.show()
        
        self.results[cluster_id] = {'MSE': mse, 'R2': r2, 'Factor Significance': factor_significance}
    
        self.plot_residuals(y_test, y_pred, cluster_id)
        self.plot_coefficient_importance(self.results[cluster_id]['Factor Significance'], cluster_id)
       
    def train_all_clusters(self):
        unique_clusters = self.clustered_data['Cluster'].unique()
        for cluster_id in unique_clusters:
            self.train_model_for_cluster(cluster_id)
            self.perform_time_series_cross_validation(cluster_id)
            cluster_returns = self.calculate_cluster_returns(cluster_id)
            if cluster_returns is not None:
                mean_returns = cluster_returns.values.mean()
                print(f"Mean Portfolio Returns for Cluster {cluster_id}: {mean_returns}")
                
    # def calculate_factor_loadings(self, cluster_id):
    #     cluster_data = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
    #     X = cluster_data.drop(['Cluster'], axis=1)
    #     y = self.returns_df.loc[X.index]
    #     model = LinearRegression()
    #     model.fit(X, y)
    #     factor_loadings = pd.DataFrame({'Factor': X.columns,'Loading': model.coef_})
    #     return factor_loadings
    
    # good in testing for any potential overfitting 
    def perform_time_series_cross_validation(self, cluster_id, n_splits=5):
        print(f"Performing Time Series Cross-Validation for Cluster {cluster_id}...")
        
        cluster_data = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
        cluster_returns = self.calculate_cluster_returns(cluster_id)
        
        if cluster_returns is None:
            print(f"Warning: No valid returns for Cluster {cluster_id}. Skipping this cluster.")
            return
        
        X = cluster_data.drop(columns=['Cluster'])
        y = cluster_returns.mean(axis=1)
        
        tscv = TimeSeriesSplit(n_splits=n_splits)
        mse_scores = []
        r2_scores = []
        
        for train_index, test_index in tscv.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            model = LinearRegression()
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            mse_scores.append(mse)
            r2_scores.append(r2)
            
        print(f"Mean Squared Errors for each split: {mse_scores}")
        print(f"R2 Scores for each split: {r2_scores}")
        print(f"Average MSE: {np.mean(mse_scores)}")
        print(f"Average R2: {np.mean(r2_scores)}")

