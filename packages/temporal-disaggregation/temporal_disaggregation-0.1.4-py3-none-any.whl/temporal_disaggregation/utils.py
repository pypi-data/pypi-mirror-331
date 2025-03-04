from pathlib import Path
import pandas as pd

class DataFrameProcessor:
    """
    Class for processing Excel files and manipulating DataFrames.
    """

    def __init__(self, file_path, sheet_name=None, engine=None):
        """
        Initializes the class with the file path, sheet (optional), and engine (optional).

        Parameters:
            file_path (str | Path): Path to the Excel file.
            sheet_name (str, optional): Name of the sheet to import. If None, loads the first sheet.
            engine (str, optional): Engine to use for reading the file (e.g., 'openpyxl', 'xlrd').
        """
        self.file_path = Path(file_path)  # Convert the path to a Path object
        self.sheet_name = sheet_name  # Sheet name (can be None)
        self.engine = engine  # File reading engine (can be None)
        self.df = None  # Initialize DataFrame as None

    def import_excel(self, datetime_cols=None, datetime_format=None, return_df=True):
        """
        Imports an Excel file and stores it in a DataFrame.
        Optionally converts columns to datetime format with a specific format.

        Parameters:
            datetime_cols (list, optional): List of columns to convert to datetime format.
            datetime_format (str, optional): Date format (e.g., "%d/%m/%Y", "%Y-%m-%d").

        Returns:
            pd.DataFrame: DataFrame with the imported data, or None if an error occurs.
        """
        try:
            if not self.file_path.exists():
                print(f"Error: The file '{self.file_path.name}' was not found.")
                return None

            read_args = {"io": self.file_path}  # Mandatory argument: file path

            if self.sheet_name is not None:
                read_args["sheet_name"] = self.sheet_name  # Add sheet_name if specified

            if self.engine is not None:
                read_args["engine"] = self.engine  # Add engine if specified

            self.df = pd.read_excel(**read_args)

            # If there are columns to convert to datetime
            if datetime_cols:
                self.convert_columns_to_datetime(datetime_cols, datetime_format)

            print(f"File '{self.file_path.name}' successfully imported.")
            if return_df:
                return self.df  # Return the loaded DataFrame

        except ValueError:
            print(f"Error: The sheet '{self.sheet_name}' does not exist in the file '{self.file_path.name}'.")
        except Exception as e:
            print(f"An error occurred while importing the file '{self.file_path.name}': {e}")

    def convert_columns_to_datetime(self, columns, date_format=None):
        """
        Converts specified columns to datetime format.

        Parameters:
            columns (list): List of column names to convert to datetime.
            date_format (str, optional): Date format for conversion (e.g., "%d/%m/%Y", "%Y-%m-%d").
        """
        try:
            if self.df is None:
                print("🚨 Error: No file has been imported. Use 'import_excel()' first.")
                return

            for col in columns:
                if col in self.df.columns:
                    self.df[col] = pd.to_datetime(self.df[col], format=date_format, errors="coerce")
                    if date_format:
                        print(f"Column '{col}' converted to datetime format with the format '{date_format}'.")
                    else:
                        print(f"Column '{col}' converted to datetime format with automatic inference.")
                else:
                    print(f"Warning: The column '{col}' does not exist in the DataFrame.")
        except Exception as e:
            print(f"Error converting columns to datetime: {e}")

    def convert_to_long_format(self, value_col, id_vars, value_name_col, return_long_format=True):
        """
        Converts a wide-format DataFrame to long format while keeping identifier variables.

        Parameters:
            value_col (str): Name of the new column that will contain the transformed variables.
            id_vars (list): List of columns to keep as identifiers.
            value_name_col (str): Name of the new column that will contain the values.
            return_long_format (bool, optional): If True, returns the DataFrame in long format.
                                                 If False, returns the original DataFrame.
                                                 Default is True.

        Returns:
            pd.DataFrame: DataFrame in long format if return_long_format is True, 
                          otherwise, returns the original one.
        """
        try:
            # Check if the DataFrame has been imported
            if self.df is None:
                print("Error: No file has been imported. Use 'import_excel()' first.")
                return None

            # If the user wants the original DataFrame unchanged, return it directly
            if not return_long_format:
                return self.df

            # Validate that the provided columns exist in the DataFrame
            missing_cols = [col for col in id_vars if col not in self.df.columns]
            if missing_cols:
                print(f"Error: The following columns do not exist in the DataFrame: {missing_cols}")
                return None

            # Convert to long format using melt
            df_long = pd.melt(
                self.df,
                id_vars=id_vars,  # Columns to keep as identifiers
                var_name=value_col,  # Name of the column that will represent the variables
                value_name=value_name_col  # Name of the column that will store the values
            )

            print("Successful conversion to long format.")
            return df_long  # Return the DataFrame in long format

        except KeyError as e:
            print(f"🚨 Error: Expected columns were not found. {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


import pandas as pd

class TimeSeriesCompleter:
    """
    Class for completing missing values in a time series by adding missing 
    index and grain combinations and imputing missing values in specific columns 
    using interpolation.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the time series data.
    index_col : str
        Name of the index column (e.g., year).
    grain_col : str
        Name of the grain column (e.g., month or another grouping).
    value_col : str
        Name of the column containing values to be imputed.
    reference_col : str
        Name of the reference column to be imputed.
    interpolation_method : str, optional
        Interpolation method to use (default is 'linear'). Examples: 'linear', 'time', 'index'.
    """
    
    def __init__(self, df, index_col, grain_col, value_col, reference_col, interpolation_method='linear'):
        try:
            self.df = df.copy()  # Create a copy of the original DataFrame to avoid modifying it
            self.index_col = index_col
            self.grain_col = grain_col
            self.value_col = value_col
            self.reference_col = reference_col
            self.interpolation_method = interpolation_method
            self.df_full = pd.DataFrame()  # DataFrame to store the completed time series
        except Exception as e:
            print(f"Error initializing TimeSeriesCompleter: {e}")

    def complete_series(self):
        """
        Completes the time series by adding all possible combinations of index and grain, 
        and imputes missing values in the specified columns.

        Returns
        -------
        pd.DataFrame
            DataFrame with the completed and imputed time series.
        """
        try:
            self._create_full_index()
        except Exception as e:
            print(f"Error while creating the full index: {e}")
            return self.df_full
        
        try:
            self._impute_column(self.value_col)
            self._impute_column(self.reference_col)
        except Exception as e:
            print(f"🚨 Error imputing columns: {e}")
        
        return self.df_full

    def _create_full_index(self):
        """
        Creates a MultiIndex with all possible combinations of index and grain.
        """
        try:
            # Get all unique values for the index and grain
            all_indices = self.df[self.index_col].unique()
            all_grains = self.df[self.grain_col].unique()
            
            # Create a MultiIndex with all possible combinations
            full_index = pd.MultiIndex.from_product([all_indices, all_grains],
                                                    names=[self.index_col, self.grain_col])
            
            # Align the original DataFrame to the new index
            self.df_full = self.df.set_index([self.index_col, self.grain_col]).reindex(full_index).reset_index()
            
            # Sort by index and grain
            self.df_full.sort_values(by=[self.index_col, self.grain_col], inplace=True)
            self.df_full.reset_index(drop=True, inplace=True)
        except Exception as e:
            print(f"Error creating the full MultiIndex: {e}")
            raise

    def _impute_column(self, col_name):
        """
        Imputes missing values in a column. First, it fills missing initial values 
        with the average of the first two valid values. Then, it applies interpolation.

        Parameters
        ----------
        col_name : str
            Name of the column to be imputed.
        """
        try:
            if self.df_full[col_name].isnull().any():
                first_valid_idx = self.df_full[col_name].first_valid_index()
                if first_valid_idx is not None:
                    next_two_values = self.df_full[col_name].iloc[first_valid_idx:first_valid_idx + 2]
                    
                    if next_two_values.notnull().sum() >= 2:
                        avg_value = next_two_values.mean()
                        self.df_full.loc[:first_valid_idx - 1, col_name] = avg_value
                        print(f"Initial values in '{col_name}' imputed with average: {avg_value:.2f}")
                    else:
                        print(f"Not enough values in '{col_name}' to compute the initial average.")
        except Exception as e:
            print(f"Error imputing initial values in '{col_name}': {e}")
        
        try:
            # Apply interpolation
            self.df_full[col_name] = self.df_full[col_name].interpolate(method=self.interpolation_method)
            print(f"Interpolation applied to '{col_name}' using method '{self.interpolation_method}'")
        except Exception as e:
            print(f"Error during interpolation in '{col_name}': {e}")
            try:
                mean_value = self.df_full[col_name].mean()
                self.df_full[col_name].fillna(mean_value, inplace=True)
                print(f"Missing values in '{col_name}' filled with mean: {mean_value:.2f}")
            except Exception as e:
                print(f"Error filling missing values in '{col_name}' with mean: {e}")


class ExcelExporter:
    """
    Class for exporting DataFrames to Excel files with customized formatting.
    """

    def __init__(self, export_path, sheet_name="Data"):
        """
        Initializes the class with the export path and sheet name.

        Parameters:
            export_path (str | Path): Path where the Excel file will be saved.
            sheet_name (str, optional): Name of the sheet within the Excel file. Default is "Data".
        """
        self.export_path = Path(export_path)  # Convert the path into a Path object
        self.sheet_name = sheet_name  # Sheet name in Excel

    def export_to_excel(self, dataframe, datetime_cols=None):
        """
        Exports a DataFrame to an Excel file with customized formatting.

        Parameters:
            dataframe (pd.DataFrame): DataFrame to be exported to Excel.
            datetime_cols (list, optional): List of columns to format as 'YYYY-MM-DD' in Excel.

        Returns:
            bool: True if the export was successful, False if an error occurred.
        """
        try:
            # Apply formatting to datetime columns if specified
            if datetime_cols:
                dataframe = self.format_datetime_columns(dataframe, datetime_cols)

            with pd.ExcelWriter(self.export_path, engine="xlsxwriter") as writer:
                dataframe.to_excel(writer, index=False, sheet_name=self.sheet_name)

                # Apply formatting to the file
                self.apply_formatting(writer, dataframe, datetime_cols)

            print(f"File '{self.export_path.name}' successfully exported.")

        except PermissionError:
            print(f"🚨 Error: Unable to write to '{self.export_path.name}'. Close the file if it is open.")
            return False

        except Exception as e:
            print(f"An error occurred while exporting the file '{self.export_path.name}': {e}")
            return False

    def format_datetime_columns(self, dataframe, datetime_cols):
        """
        Converts datetime columns to 'YYYY-MM-DD' format to avoid time display in Excel.

        Parameters:
            dataframe (pd.DataFrame): DataFrame containing datetime columns.
            datetime_cols (list): List of columns to convert.

        Returns:
            pd.DataFrame: DataFrame with formatted datetime columns.
        """
        try:
            for col in datetime_cols:
                if col in dataframe.columns:
                    dataframe[col] = dataframe[col].dt.strftime("%Y-%m-%d")  # 🔹 Format YYYY-MM-DD
                    print(f"Column '{col}' converted to 'YYYY-MM-DD' format.")
                else:
                    print(f"Warning: Column '{col}' does not exist in the DataFrame.")
            return dataframe
        except Exception as e:
            print(f"Error formatting datetime columns: {e}")
            return dataframe

    def apply_formatting(self, writer, dataframe, datetime_cols):
        """
        Applies formatting to the Excel file: bold headers and column width adjustment.

        Parameters:
            writer (pd.ExcelWriter): Pandas writer object for Excel.
            dataframe (pd.DataFrame): Exported DataFrame, necessary for column formatting.
            datetime_cols (list): List of datetime columns to apply formatting in Excel.
        """
        try:
            workbook = writer.book
            worksheet = writer.sheets[self.sheet_name]

            # Bold header format with green background
            header_format = workbook.add_format({"bold": True, "font_color": "white", "bg_color": "green"})
            
            # Date format for Excel (YYYY-MM-DD)
            date_format = workbook.add_format({"num_format": "yyyy-mm-dd"})

            # Apply formatting to the header
            for col_num, value in enumerate(dataframe.columns.values):
                worksheet.write(0, col_num, value, header_format)

            # Adjust column width and apply date format if applicable
            for i, col in enumerate(dataframe.columns):
                column_length = dataframe[col].astype(str).str.len().max() + 2
                worksheet.set_column(i, i, column_length)

                # If the column is datetime, apply the date format in Excel
                if datetime_cols and col in datetime_cols:
                    worksheet.set_column(i, i, None, date_format)

        except Exception as e:
            print(f"Warning: Failed to apply formatting to the Excel file: {e}")
