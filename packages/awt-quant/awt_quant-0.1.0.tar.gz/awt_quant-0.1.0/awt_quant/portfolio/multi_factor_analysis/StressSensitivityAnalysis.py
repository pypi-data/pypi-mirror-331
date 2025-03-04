import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance

class StressAnalysis:

    def __init__(self, localized_model, clustered_data):
        self.localized_model = localized_model
        self.clustered_data = clustered_data

    def noise_injection(self, cluster_id, noise_level=0.05):
        # Inject Gaussian noise into the data and evaluate model performance.
        cluster_data = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
        X = cluster_data.drop(columns=['Cluster'])
        y = self.localized_model.calculate_cluster_returns(cluster_id).mean(axis=1)
        
        # Inject noise
        noise = np.random.normal(0, noise_level, X.shape)
        X_noisy = X + noise
        
        model = LinearRegression()
        model.fit(X, y)
        y_pred_original = model.predict(X)
        y_pred_noisy = model.predict(X_noisy)
        
        mse_original = mean_squared_error(y, y_pred_original)
        mse_noisy = mean_squared_error(y, y_pred_noisy)
        
        return mse_original, mse_noisy

    def extreme_value_analysis(self, cluster_id, feature, extreme="max"):
        cluster_data = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
        X = cluster_data.drop(columns=['Cluster'])
        y = self.localized_model.calculate_cluster_returns(cluster_id).mean(axis=1)
        
        # set feature to extreme value
        if extreme == "max":
            X[feature] = X[feature].max()
        else:
            X[feature] = X[feature].min()
        
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        mse = mean_squared_error(y, y_pred)
        return mse
    
    def global_downturn(self, cluster_id, downturn_pct=0.1):
        cluster_data = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
        X = cluster_data.drop(columns=['Cluster'])
        y = self.localized_model.calculate_cluster_returns(cluster_id).mean(axis=1)
        
        # reduce all factors by the given percentage
        X_downturn = X * (1 - downturn_pct)
        
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X_downturn)
        
        mse = mean_squared_error(y, y_pred)
        return mse
    
    def rapid_inflation(self, cluster_id, inflation_factors, inflation_pct=0.2):
        cluster_data = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
        X = cluster_data.drop(columns=['Cluster'])
        y = self.localized_model.calculate_cluster_returns(cluster_id).mean(axis=1)
        
        # increase specified inflation factors by the given percentage
        for factor in inflation_factors:
            X[factor] = X[factor] * (1 + inflation_pct)
        
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        
        mse = mean_squared_error(y, y_pred)
        return mse
    

class SensitivityAnalysis:

    def __init__(self, localized_model, clustered_data):
        self.localized_model = localized_model
        self.clustered_data = clustered_data

    def feature_perturbation(self, cluster_id, feature, perturb_pct=0.05):
        """Perturb one feature and evaluate the change in model predictions."""
        cluster_data = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
        X = cluster_data.drop(columns=['Cluster'])
        y = self.localized_model.calculate_cluster_returns(cluster_id).mean(axis=1)
        
        # perturb the feature
        X_perturbed = X.copy()
        X_perturbed[feature] = X[feature] * (1 + perturb_pct)
        
        model = LinearRegression()
        model.fit(X, y)
        y_pred_original = model.predict(X)
        y_pred_perturbed = model.predict(X_perturbed)
        
        mse_original = mean_squared_error(y, y_pred_original)
        mse_perturbed = mean_squared_error(y, y_pred_perturbed)
        
        return mse_original, mse_perturbed

    def feature_importance_analysis(self, cluster_id):
        # use permutation importance to determine feature importance.
        cluster_data = self.clustered_data[self.clustered_data['Cluster'] == cluster_id]
        X = cluster_data.drop(columns=['Cluster'])
        y = self.localized_model.calculate_cluster_returns(cluster_id).mean(axis=1)
        
        model = LinearRegression()
        model.fit(X, y)
        
        result = permutation_importance(model, X, y, n_repeats=30, random_state=42)
        sorted_idx = result.importances_mean.argsort()
        
        feature_importances = pd.DataFrame({
            'Feature': X.columns[sorted_idx],
            'Importance': result.importances_mean[sorted_idx]
        })
        
        return feature_importances