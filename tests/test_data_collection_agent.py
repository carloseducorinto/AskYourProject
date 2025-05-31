import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
from pandas.testing import assert_frame_equal
import os

# Adjust the import path based on the project structure
# Assuming 'team1_agents' is a package in the root or accessible via PYTHONPATH
from team1_agents.data_collection_agent.agent import DataCollectionAgent

class TestDataCollectionAgent(unittest.TestCase):

    def setUp(self):
        """Setup common test data"""
        self.symbol = "TESTSYM"
        self.period = "1wk"
        self.interval = "1h"
        self.agent = DataCollectionAgent(symbol=self.symbol, period=self.period, interval=self.interval)

        # Sample DataFrame
        self.sample_data_dict = {
            'Open': [100, 102, 101],
            'High': [103, 104, 102],
            'Low': [99, 101, 100],
            'Close': [102, 103, 101],
            'Volume': [1000, 1200, 1100]
        }
        self.sample_df = pd.DataFrame(self.sample_data_dict)
        self.empty_df = pd.DataFrame()

    def test_agent_initialization(self):
        """Test if the agent is initialized correctly."""
        self.assertEqual(self.agent.symbol, self.symbol)
        self.assertEqual(self.agent.period, self.period)
        self.assertEqual(self.agent.interval, self.interval)
        print("Test Agent Initialization: PASSED")

    @patch('yfinance.Ticker')
    def test_fetch_data_success(self, MockTicker):
        """Test successful data fetching."""
        mock_ticker_instance = MockTicker.return_value
        mock_ticker_instance.history.return_value = self.sample_df

        fetched_data = self.agent.fetch_data()

        MockTicker.assert_called_once_with(self.symbol)
        mock_ticker_instance.history.assert_called_once_with(period=self.period, interval=self.interval)
        assert_frame_equal(fetched_data, self.sample_df)
        print("Test Fetch Data Success: PASSED")

    @patch('yfinance.Ticker')
    def test_fetch_data_api_error(self, MockTicker):
        """Test data fetching when yfinance API raises an error."""
        mock_ticker_instance = MockTicker.return_value
        mock_ticker_instance.history.side_effect = Exception("API Network Error")

        # Suppress print during this test for cleaner output
        with patch('builtins.print') as mock_print:
            fetched_data = self.agent.fetch_data()

        MockTicker.assert_called_once_with(self.symbol)
        mock_ticker_instance.history.assert_called_once_with(period=self.period, interval=self.interval)
        self.assertTrue(fetched_data.empty)
        # Check if the error message was printed (optional, but good to verify)
        mock_print.assert_any_call(f"An error occurred while trying to fetch data for {self.symbol} (Period: {self.period}, Interval: {self.interval}): API NetworkError")
        print("Test Fetch Data API Error: PASSED")

    @patch('yfinance.Ticker')
    def test_fetch_data_empty_response(self, MockTicker):
        """Test data fetching when yfinance returns an empty DataFrame."""
        mock_ticker_instance = MockTicker.return_value
        mock_ticker_instance.history.return_value = self.empty_df

        with patch('builtins.print') as mock_print: # Suppress print
            fetched_data = self.agent.fetch_data()

        MockTicker.assert_called_once_with(self.symbol)
        mock_ticker_instance.history.assert_called_once_with(period=self.period, interval=self.interval)
        self.assertTrue(fetched_data.empty)
        mock_print.assert_any_call(f"Warning: No data returned for symbol {self.symbol.upper()} with period {self.period} and interval {self.interval}. This could be due to an invalid symbol, delisted stock, or no data for the requested period/interval.")
        print("Test Fetch Data Empty Response: PASSED")

    @patch('os.makedirs') # Mock os.makedirs
    @patch('pandas.DataFrame.to_csv') # Mock the to_csv method
    def test_save_to_csv_success(self, mock_to_csv, mock_makedirs):
        """Test saving data to CSV successfully."""
        # Assume 'data' directory might or might not exist
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False # Simulate directory does not exist initially

            filename_prefix = "test_stock_data"
            expected_filename = f"{filename_prefix}_{self.symbol.upper()}_{self.period}_{self.interval}.csv"
            expected_filepath = os.path.join("data", expected_filename)

            returned_filepath = self.agent.save_to_csv(self.sample_df, filename_prefix=filename_prefix)

            mock_exists.assert_called_once_with("data") # Check if existence of 'data' dir was checked
            mock_makedirs.assert_called_once_with("data") # Check if 'data' dir creation was attempted
            mock_to_csv.assert_called_once_with(expected_filepath)
            self.assertEqual(returned_filepath, expected_filepath)
            print("Test Save to CSV Success: PASSED")

    @patch('os.makedirs')
    @patch('pandas.DataFrame.to_csv')
    def test_save_to_csv_empty_data(self, mock_to_csv, mock_makedirs):
        """Test saving when data is empty."""
        with patch('builtins.print') as mock_print: # Suppress print
            returned_filepath = self.agent.save_to_csv(self.empty_df, filename_prefix="test_empty")

        mock_makedirs.assert_not_called()
        mock_to_csv.assert_not_called()
        self.assertEqual(returned_filepath, "")
        mock_print.assert_any_call("Invalid or empty DataFrame provided. Nothing to save.")
        print("Test Save to CSV Empty Data: PASSED")

    @patch('os.makedirs')
    @patch('pandas.DataFrame.to_csv')
    def test_save_to_csv_os_error_creating_dir(self, mock_to_csv, mock_makedirs):
        """Test saving data to CSV when os.makedirs raises OSError."""
        mock_makedirs.side_effect = OSError("Cannot create directory")

        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False # Simulate directory does not exist initially
            with patch('builtins.print') as mock_print: # Suppress print
                returned_filepath = self.agent.save_to_csv(self.sample_df, filename_prefix="test_os_error")

        mock_exists.assert_called_once_with("data")
        mock_makedirs.assert_called_once_with("data")
        mock_to_csv.assert_not_called() # Should not be called if dir creation fails
        self.assertEqual(returned_filepath, "")
        mock_print.assert_any_call("Error creating directory ./data: Cannot create directory")
        print("Test Save to CSV OS Error: PASSED")


    @patch('builtins.print')
    def test_display_data_with_data(self, mock_print):
        """Test displaying data when DataFrame is not empty."""
        self.agent.display_data(self.sample_df)
        # Check if print was called (at least for the header message and then for data itself)
        self.assertTrue(mock_print.call_count >= 2)
        mock_print.assert_any_call(f"\nDisplaying data for {self.symbol.upper()} (Period: {self.period}, Interval: {self.interval}):")
        print("Test Display Data with Data: PASSED")

    @patch('builtins.print')
    def test_display_data_empty(self, mock_print):
        """Test displaying data when DataFrame is empty."""
        self.agent.display_data(self.empty_df)
        mock_print.assert_called_once_with("Invalid or empty DataFrame provided. Nothing to display.")
        print("Test Display Data Empty: PASSED")

if __name__ == '__main__':
    # This allows running the tests directly from this file
    unittest.main()
