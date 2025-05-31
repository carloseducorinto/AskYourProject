import yfinance as yf
import pandas as pd
import os

class DataCollectionAgent:
    """
    Agent responsible for collecting stock data using yfinance.

    Note on API Keys:
    The current implementation uses yfinance, which generally does not require an API key
    for public historical data. However, if this agent were to be adapted for other
    data providers that do require API keys, a recommended approach for managing them
    would be through environment variables. For example:

    import os
    api_key = os.getenv('YOUR_DATA_PROVIDER_API_KEY')

    This keeps keys out of the codebase and allows for secure configuration.
    """
    def __init__(self, symbol: str, period: str = "1mo", interval: str = "1d"):
        """
        Initializes the DataCollectionAgent.

        Args:
            symbol (str): The stock symbol (e.g., "AAPL").
            period (str, optional): The period for which to fetch data (e.g., "1mo", "1y"). Defaults to "1mo".
            interval (str, optional): The data interval (e.g., "1d", "1wk"). Defaults to "1d".
        """
        self.symbol = symbol
        self.period = period
        self.interval = interval

    def fetch_data(self) -> pd.DataFrame:
        """
        Fetches historical stock data using yfinance.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the historical stock data.
                          Returns an empty DataFrame if an error occurs.
        """
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(period=self.period, interval=self.interval)
            if data.empty:
                print(f"Warning: No data returned for symbol {self.symbol} with period {self.period} and interval {self.interval}. This could be due to an invalid symbol, delisted stock, or no data for the requested period/interval.")
            return data
        except Exception as e:
            print(f"An error occurred while trying to fetch data for {self.symbol} (Period: {self.period}, Interval: {self.interval}): {e}")
            return pd.DataFrame() # Return empty DataFrame on error

    def save_to_csv(self, data: pd.DataFrame, filename_prefix: str = "stock_data") -> str:
        """
        Saves the given DataFrame to a CSV file.

        The filename will be in the format: <filename_prefix>_<symbol>_<period>_<interval>.csv

        Args:
            data (pd.DataFrame): The DataFrame to save.
            filename_prefix (str, optional): Prefix for the CSV filename. Defaults to "stock_data".

        Returns:
            str: The filename of the saved CSV file. Returns an empty string if data is empty or an error occurs.
        """
        if not isinstance(data, pd.DataFrame) or data.empty:
            print("Invalid or empty DataFrame provided. Nothing to save.")
            return ""

        # Ensure the data directory exists
        data_dir = "data"
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir)
                print(f"Created directory: ./{data_dir}")
            except OSError as e:
                print(f"Error creating directory ./{data_dir}: {e}")
                return ""

        filename = f"{filename_prefix}_{self.symbol.upper()}_{self.period}_{self.interval}.csv"
        filepath = os.path.join(data_dir, filename)

        try:
            data.to_csv(filepath)
            print(f"Data saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"Error saving data to CSV {filepath}: {e}")
            return ""

    def display_data(self, data: pd.DataFrame):
        """
        Prints the head of the DataFrame to the console.

        Args:
            data (pd.DataFrame): The DataFrame to display.
        """
        if not isinstance(data, pd.DataFrame) or data.empty:
            print("Invalid or empty DataFrame provided. Nothing to display.")
            return
        print(f"\nDisplaying data for {self.symbol.upper()} (Period: {self.period}, Interval: {self.interval}):")
        print(data.head())

if __name__ == '__main__':
    # Example Usage:
    # 1. Create an agent for Apple Inc. for the last 1 month with daily interval
    agent_aapl = DataCollectionAgent(symbol="AAPL", period="1mo", interval="1d")

    # 2. Fetch data
    aapl_data = agent_aapl.fetch_data()

    # 3. Display fetched data
    agent_aapl.display_data(aapl_data)

    # 4. Save data to CSV
    # The CSV will be saved in a 'data' subdirectory.
    # Make sure the 'data' directory can be created or exists.
    if not aapl_data.empty:
        aapl_csv_file = agent_aapl.save_to_csv(aapl_data, filename_prefix="aapl_stock_data")
        if aapl_csv_file:
            print(f"AAPL data saved to: {aapl_csv_file}")
        else:
            print("Failed to save AAPL data.")

    print("-" * 50)

    # Example for a non-existent symbol or a symbol with issues
    agent_error = DataCollectionAgent(symbol="NONEXISTENTICKER123", period="1d", interval="1d")
    error_data = agent_error.fetch_data()
    agent_error.display_data(error_data) # Should indicate data is empty
    error_csv_file = agent_error.save_to_csv(error_data) # Should indicate nothing to save
    if error_csv_file:
        print(f"Error data saved to: {error_csv_file}")
    else:
        print("No data to save for NONEXISTENTICKER123, as expected.")

    print("-" * 50)

    # Example for a different stock and period
    agent_msft = DataCollectionAgent(symbol="MSFT", period="3mo", interval="1wk")
    msft_data = agent_msft.fetch_data()
    agent_msft.display_data(msft_data)
    if not msft_data.empty:
        msft_csv_file = agent_msft.save_to_csv(msft_data, filename_prefix="msft_stock_data")
        if msft_csv_file:
            print(f"MSFT data saved to: {msft_csv_file}")
        else:
            print("Failed to save MSFT data.")

    # Note: Running this script directly will attempt to fetch live data and save files.
    # In a real application, you might integrate this agent into a larger workflow.
    # Ensure yfinance and pandas are installed (pip install yfinance pandas).
    # The save_to_csv method will create a 'data' subdirectory in the current working directory
    # if it doesn't exist.
    # If running in a restricted environment, file I/O might fail.
    # The main execution block is for demonstration; tests should be separate.
