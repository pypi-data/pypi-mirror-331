import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import GridSearchCV
from sklearn.neural_network import MLPRegressor


class Retropolarizer:
    """
    Class for retropolarizing a new data series based on an old data series,
    using different statistical and Machine Learning methods.

    Available methods:
    - 'proportion': Maintains a constant proportion between the series.
    - 'linear_regression': Fits a linear regression model.
    - 'polynomial_regression': Fits a polynomial regression model.
    - 'exponential_smoothing': Uses exponential smoothing to predict missing values.
    - 'mlp_regression': Neural network model (MLP Regressor).

    Attributes:
    - df: A copy of the original DataFrame with interpolated data.
    - new_col: Name of the column containing the new methodology.
    - old_col: Name of the column containing the old methodology.
    """

    def __init__(self, df, new_col, old_col):
        """
        Initializes the class with the DataFrame and relevant columns.

        Parameters:
        - df: pd.DataFrame -> DataFrame containing the data series.
        - new_col: str -> Name of the column with the new methodology.
        - old_col: str -> Name of the column with the old methodology.
        """
        try:
            # Create a copy of the DataFrame to avoid modifying the original
            self.df = df.copy()
            self.new_col = new_col
            self.old_col = old_col

        except Exception as e:
            print(f"Error initializing Retropolarizer: {e}")

    def _proportion(self, mask_retropolar):
        """
        Applies the proportion method to retropolarize values.

        Parameter:
        - mask_retropolar: pd.Series -> Mask of missing values in the new series.
        """
        try:
            # Compute the proportion between known values of both series
            proportions = self.df[self.new_col].dropna() / self.df[self.old_col].dropna()
            mean_proportion = np.mean(proportions)

            # Apply the proportion to the missing values
            self.df.loc[mask_retropolar, self.new_col] = mean_proportion * self.df.loc[mask_retropolar, self.old_col]

        except Exception as e:
            print(f"Error in _proportion: {e}")

    def _linear_regression(self, mask_retropolar):
        """
        Applies linear regression to retropolarize values.

        Parameter:
        - mask_retropolar: pd.Series -> Mask of missing values in the new series.
        """
        try:
            valid_data = self.df.dropna(subset=[self.new_col, self.old_col])

            if valid_data.empty:
                print("Not enough data to fit linear regression.")
                return

            X = valid_data[self.old_col].values.reshape(-1, 1)
            y = valid_data[self.new_col].values

            model = LinearRegression()
            model.fit(X, y)

            # Predict missing values
            if not self.df.loc[mask_retropolar, self.old_col].empty:
                self.df.loc[mask_retropolar, self.new_col] = model.predict(
                    self.df.loc[mask_retropolar, self.old_col].values.reshape(-1, 1)
                )

        except Exception as e:
            print(f"Error in _linear_regression: {e}")

    def _polynomial_regression(self, mask_retropolar):
        """
        Applies polynomial regression to retropolarize values.

        Parameter:
        - mask_retropolar: pd.Series -> Mask of missing values in the new series.
        """
        try:
            valid_data = self.df.dropna(subset=[self.new_col, self.old_col])

            if valid_data.empty:
                print("Not enough data to fit polynomial regression.")
                return

            X = valid_data[self.old_col].values.reshape(-1, 1)
            y = valid_data[self.new_col].values

            # Use GridSearch to find the best polynomial degree
            polynomial_model = make_pipeline(PolynomialFeatures(), LinearRegression())
            parameters = {'polynomialfeatures__degree': np.arange(1, 6)}
            grid_search = GridSearchCV(polynomial_model, parameters, cv=5)
            grid_search.fit(X, y)

            # Predict missing values
            if not self.df.loc[mask_retropolar, self.old_col].empty:
                self.df.loc[mask_retropolar, self.new_col] = grid_search.predict(
                    self.df.loc[mask_retropolar, self.old_col].values.reshape(-1, 1)
                )

        except Exception as e:
            print(f"Error in _polynomial_regression: {e}")

    def _exponential_smoothing(self, mask_retropolar, alpha=0.5):
        """
        Applies exponential smoothing to retropolarize values.

        Parameters:
        - mask_retropolar: pd.Series -> Mask of missing values in the new series.
        - alpha: float -> Smoothing parameter (0 < alpha ≤ 1).
        """
        try:
            valid_data = self.df.dropna(subset=[self.new_col])

            if valid_data.empty:
                print("Not enough data to apply exponential smoothing.")
                return

            smoothed_values = valid_data[self.new_col].ewm(alpha=alpha, adjust=False).mean()
            self.df.loc[mask_retropolar, self.new_col] = smoothed_values.iloc[-1]

        except Exception as e:
            print(f"Error in _exponential_smoothing: {e}")

    def _mlp_regression(self, mask_retropolar):
        """
        Applies regression using a neural network (MLP Regressor).

        Parameter:
        - mask_retropolar: pd.Series -> Mask of missing values in the new series.
        """
        try:
            valid_data = self.df.dropna(subset=[self.new_col, self.old_col])

            if valid_data.empty:
                print("Not enough data to train the neural network.")
                return

            X = valid_data[self.old_col].values.reshape(-1, 1)
            y = valid_data[self.new_col].values

            model = MLPRegressor(
                hidden_layer_sizes=(1000,), max_iter=10000, activation="tanh", alpha=0.001, random_state=0
            )
            model.fit(X, y)

            # Predict missing values
            if not self.df.loc[mask_retropolar, self.old_col].empty:
                self.df.loc[mask_retropolar, self.new_col] = model.predict(
                    self.df.loc[mask_retropolar, self.old_col].values.reshape(-1, 1)
                )

        except Exception as e:
            print(f"Error in _mlp_regression: {e}")

    def retropolarize(self, method='proportion'):
        """
        Executes retropolarization using the specified method.

        Parameter:
        - method: str -> Method to use ('proportion', 'linear_regression', 'polynomial_regression',
                          'exponential_smoothing', 'mlp_regression').

        Returns:
        - pd.Series -> Series with retropolarized values.
        """
        try:
            mask_retropolar = self.df[self.new_col].isna() & self.df[self.old_col].notna()

            methods = {
                'proportion': self._proportion,
                'linear_regression': self._linear_regression,
                'polynomial_regression': self._polynomial_regression,
                'exponential_smoothing': self._exponential_smoothing,
                'mlp_regression': self._mlp_regression
            }

            if method in methods:
                methods[method](mask_retropolar)
            else:
                print("⚠️ Unrecognized method.")

            return self.df[self.new_col]

        except Exception as e:
            print(f"Error in retropolarize: {e}")
