from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
# from pandas.plotting import parallel_coordinates
# from math import pi
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

class KMeansClusterer:
    def __init__(self, factors_df, min_clusters=2, max_clusters=10, init_method='k-means++'):
        self.min_clusters = min_clusters
        self.max_clusters = max_clusters
        self.optimal_clusters = None
        self.factors_df = factors_df
        self.init_method = init_method  # Default is 'k-means++'

    def standardize_data(self):
        scaler = StandardScaler()
        standardized_data = scaler.fit_transform(self.factors_df)
        return pd.DataFrame(standardized_data, columns=self.factors_df.columns)

    def find_optimal_clusters(self):
        standardized_data = self.standardize_data()
        inertias = []
        cluster_range = range(self.min_clusters, self.max_clusters + 1)

        for k in cluster_range:
            kmeans = KMeans(n_clusters=k, random_state=0, init=self.init_method)
            kmeans.fit(standardized_data)
            inertias.append(kmeans.inertia_)

        elbow_point = self.min_clusters + elbow(elbow_values=inertias, threshold=0.01)
        self.optimal_clusters = elbow_point
        print(f"Number of optimal clusters: {elbow_point}")

    def perform_clustering(self):
        if self.optimal_clusters is None:
            self.find_optimal_clusters()
        
        standardized_data = self.standardize_data()
        kmeans = KMeans(n_clusters=self.optimal_clusters, random_state=0, init=self.init_method)
        kmeans.fit(standardized_data)

        clustered_df = self.factors_df.copy()
        clustered_df['Cluster'] = kmeans.labels_
        
        return clustered_df

    def visualize_clusters(self, clustered_df):
        pca = PCA(n_components=2)
        standardized_data = self.standardize_data()
        pca_result = pca.fit_transform(standardized_data)
        pca_df = pd.DataFrame(data=pca_result, columns=['PC1', 'PC2'])
        pca_df['Cluster'] = clustered_df['Cluster'].values

        plt.figure(figsize=(12, 8))
        sns.scatterplot(x='PC1', y='PC2', hue='Cluster', data=pca_df, palette="tab10", s=100)
        plt.title("Clusters in PCA Feature Space")
        plt.show()

    # Radial Chart
    def plot_radial_chart(self):
        kmeans = KMeans(n_clusters=self.optimal_clusters, random_state=0, init=self.init_method)
        standardized_data = self.standardize_data()
        kmeans.fit(standardized_data)
        centroids = pd.DataFrame(kmeans.cluster_centers_, columns=self.factors_df.columns)
        
        angles = np.linspace(0, 2 * np.pi, len(centroids.columns), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        for i, color in enumerate(plt.cm.tab10(np.linspace(0, 1, self.optimal_clusters))):
            values = centroids.loc[i].tolist()
            values += values[:1]
            ax.fill(angles, values, color=color, alpha=0.25)
            ax.plot(angles, values, color=color, linewidth=2, label=f'Cluster {i}')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(centroids.columns)
        ax.legend()
        
        plt.show()

    # Heatmap of Centroids
    def plot_heatmap_of_centroids(self):
        kmeans = KMeans(n_clusters=self.optimal_clusters, random_state=0, init=self.init_method)
        standardized_data = self.standardize_data()
        kmeans.fit(standardized_data)
        centroids = pd.DataFrame(kmeans.cluster_centers_, columns=self.factors_df.columns)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(centroids, annot=True, cmap='coolwarm')
        plt.title('Heatmap of Cluster Centroids')
        plt.show()

# Helper function to determine number of optimal clusters
def elbow(elbow_values, threshold=0.01):
    diff1 = np.diff(elbow_values)
    diff2 = np.diff(diff1)
    return np.argmin(diff2 <= threshold)

# The class  automatically defaults to 'k-means++' for initialization; can specify another method.
