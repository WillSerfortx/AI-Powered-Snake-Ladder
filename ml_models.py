"""Machine Learning Models - K-Means and Logistic Regression (No KNN)."""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from config import KMEANS_CLUSTERS, BOARD_SIZE
from board import Board


class MLModels:
    def __init__(self):
        self.kmeans_model = None
        self.lr_model = None
        self.scaler = StandardScaler()
        self.kmeans_scaler = StandardScaler()
        self.zone_map = {}       # {cell: zone_label} from K-Means
        self.win_prob_map = {}   # {cell: probability} from Logistic Regression

    def train_all(self, training_data, board):
        """Train K-Means and Logistic Regression models."""
        data = np.array(training_data)
        X = data[:, :-1]  # Features (5 columns)
        y = data[:, -1]   # Labels (won: 0 or 1)

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        print("\n--- Training ML Models ---")
        self._train_kmeans(board)
        self._train_logistic_regression(X_scaled, y, board)
        print("--- All Models Trained ---\n")

    def _train_kmeans(self, board):
        """Train K-Means to cluster board into 3 risk zones."""
        all_features = board.get_all_features()
        cell_numbers = [f[0] for f in all_features]
        feature_matrix = np.array([f[1:] for f in all_features])

        features_scaled = self.kmeans_scaler.fit_transform(feature_matrix)
        self.kmeans_model = KMeans(n_clusters=KMEANS_CLUSTERS, random_state=42, n_init=10)
        labels = self.kmeans_model.fit_predict(features_scaled)

        # Map clusters to zone names based on average snakes_ahead
        cluster_snake_avg = {}
        cluster_ladder_avg = {}
        for i in range(KMEANS_CLUSTERS):
            mask = labels == i
            cluster_snake_avg[i] = feature_matrix[mask, 2].mean()
            cluster_ladder_avg[i] = feature_matrix[mask, 3].mean()

        danger_cluster = max(cluster_snake_avg, key=cluster_snake_avg.get)
        remaining = [i for i in range(KMEANS_CLUSTERS) if i != danger_cluster]
        advantage_cluster = max(remaining, key=lambda x: cluster_ladder_avg[x])
        neutral_cluster = [i for i in remaining if i != advantage_cluster][0] if len(remaining) > 1 else remaining[0]

        cluster_to_zone = {
            danger_cluster: 'danger',
            advantage_cluster: 'advantage',
            neutral_cluster: 'neutral'
        }

        for cell_num, label in zip(cell_numbers, labels):
            self.zone_map[cell_num] = cluster_to_zone[label]

        print(f"  ✓ K-Means trained ({KMEANS_CLUSTERS} clusters)")

    def _train_logistic_regression(self, X, y, board):
        """Train Logistic Regression to predict win probability."""
        self.lr_model = LogisticRegression(random_state=42, max_iter=1000)
        self.lr_model.fit(X, y)

        # Predict win probability for all 100 cells
        for cell in range(1, BOARD_SIZE + 1):
            features = board.get_cell_features(cell)
            features_scaled = self.scaler.transform([features])
            prob = self.lr_model.predict_proba(features_scaled)[0][1]
            self.win_prob_map[cell] = round(prob, 3)

        print(f"  ✓ Logistic Regression trained")

    # --- Prediction Methods ---

    def predict_win_probability(self, cell, board):
        """Predict win probability (0-1) for a cell."""
        if cell in self.win_prob_map:
            return self.win_prob_map[cell]
        features = board.get_cell_features(cell)
        features_scaled = self.scaler.transform([features])
        prob = self.lr_model.predict_proba(features_scaled)[0][1]
        return round(prob, 3)

    def get_kmeans_zone(self, cell):
        """Get the K-Means cluster zone for a cell."""
        return self.zone_map.get(cell, 'neutral')


if __name__ == "__main__":
    from simulate import simulate_games

    board = Board()
    print("Simulating games...")
    data = simulate_games(board, num_games=5000)

    models = MLModels()
    models.train_all(data, board)

    print("\nSample predictions:")
    for cell in [10, 25, 50, 75, 90]:
        prob = models.predict_win_probability(cell, board)
        km_zone = models.get_kmeans_zone(cell)
        print(f"  Cell {cell}: K-Means={km_zone}, Win Prob={prob}")