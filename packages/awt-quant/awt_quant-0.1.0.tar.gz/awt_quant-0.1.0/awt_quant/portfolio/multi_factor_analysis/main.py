from .DataCollector import DataCollector
from .FactorConstructor import FactorConstructor
from .RandomForestFeatureSelector import RandomForestFeatureSelector
from .KMeansClusterer import KMeansClusterer
from .LocalizedModel import LocalizedModel
from .StressSensitivityAnalysis import SensitivityAnalysis,StressAnalysis
import pandas as pd

def run_multi_factor_analysis(symbols, start_date="2020-01-01", end_date="2022-01-01"):
    """
    Runs the Multi-Factor Analysis (MFA) pipeline.

    Args:
        symbols (list): List of stock tickers to analyze.
        start_date (str): Start date for collecting financial data.
        end_date (str): End date for collecting financial data.

    Returns:
        dict: Processed results including clustering, feature importance, 
              stress tests, and sensitivity analysis.
    """

    # ✅ Step 1: Data Collection
    print("📥 Collecting Price Data...")
    data_collector = DataCollector(symbols, start_date, end_date)
    price_data = data_collector.fetch_price_data()
    returns_data = data_collector.calculate_historical_returns(price_data)

    # ✅ Step 2: Factor Construction
    print("🛠 Constructing Factors...")
    factor_constructor = FactorConstructor(start_date, end_date)
    factors_df = factor_constructor.get_all_factors()

    # ✅ Step 3: Feature Selection
    print("📊 Selecting Important Features...")
    random_forest_selector = RandomForestFeatureSelector(factor_constructor, data_collector)
    feature_importances_df = random_forest_selector.feature_importance(factors_df)
    important_features = random_forest_selector.select_important_features(factors_df)

    print("🔍 High Multicollinearity Features:")
    high_vif_features = random_forest_selector.check_multicollinearity(factors_df)
    print(high_vif_features)

    print("🔗 Cointegration Results:")
    cointegration_results = random_forest_selector.check_cointegration(factors_df)

    # ✅ Step 4: Clustering
    print("🔬 Performing Clustering...")
    kmeans_clusterer = KMeansClusterer(factors_df[important_features])
    clustered_data = kmeans_clusterer.perform_clustering()
    kmeans_clusterer.plot_radial_chart()
    kmeans_clusterer.plot_heatmap_of_centroids()
    kmeans_clusterer.visualize_clusters(clustered_data)

    # ✅ Step 5: Localized Model Training
    print("📈 Training Localized Models...")
    returns_df = pd.DataFrame({ticker: df['Daily_Return'] for ticker, df in returns_data.items()})
    returns_df.index = pd.to_datetime(returns_df.index)
    clustered_data.index = pd.to_datetime(clustered_data.index)
    returns_df = returns_df.reindex(clustered_data.index).dropna()

    localized_model = LocalizedModel(clustered_data, returns_df)
    localized_model.train_all_clusters()

    # ✅ Step 6: Stress and Sensitivity Analysis
    print("⚠️ Running Stress & Sensitivity Analysis...")
    stress_analysis = StressAnalysis(localized_model, clustered_data)
    sensitivity_analysis = SensitivityAnalysis(localized_model, clustered_data)

    unique_clusters = clustered_data['Cluster'].unique()
    features = clustered_data.drop(columns=['Cluster']).columns

    stress_results = {}
    sensitivity_results = {}

    for cluster_id in unique_clusters:
        stress_results[cluster_id] = {
            "noise_injection": stress_analysis.noise_injection(cluster_id),
            "global_downturn": stress_analysis.global_downturn(cluster_id, downturn_pct=0.1),
        }

        for feature in features:
            stress_results[(cluster_id, feature)] = {
                "extreme_value": stress_analysis.extreme_value_analysis(cluster_id, feature, extreme="max"),
                "rapid_inflation": stress_analysis.rapid_inflation(cluster_id, [feature], inflation_pct=0.2),
            }

            sensitivity_results[(cluster_id, feature)] = {
                "feature_perturbation": sensitivity_analysis.feature_perturbation(cluster_id, feature),
                "feature_importance": sensitivity_analysis.feature_importance_analysis(cluster_id),
            }

    # ✅ Return results for further analysis
    return {
        "feature_importances": feature_importances_df,
        "clustering": clustered_data,
        "localized_model": localized_model,
        "stress_results": stress_results,
        "sensitivity_results": sensitivity_results
    }


if __name__ == "__main__":
    symbols = [
        "AAPL", "MSFT", "GOOGL", "RTX", "LMT", "BA", "FANG", "AMZN", "TSLA", "JPM", "GS", "JNJ", 
        "PFE", "PG", "KO", "SO", "DUK", "PLD", "T", "VZ", "CAT", "GE"
    ]
    results = run_multi_factor_analysis(symbols)
    print("✅ Multi-Factor Analysis Completed!")
