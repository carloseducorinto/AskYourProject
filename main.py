from team1_agents.data_collection_agent.agent import DataCollectionAgent
import pandas as pd

def run_demonstration():
    """
    Demonstrates the usage of the DataCollectionAgent.
    """
    print("Starting DataCollectionAgent demonstration...")

    # --- Parameters for the agent ---
    symbol_to_test = "MSFT"
    period_to_test = "1mo"
    interval_to_test = "1d"
    csv_filename_prefix = "demonstration_stock_data"

    print(f"\n1. Instantiating DataCollectionAgent for symbol: {symbol_to_test}, period: {period_to_test}, interval: {interval_to_test}")
    agent = DataCollectionAgent(symbol=symbol_to_test, period=period_to_test, interval=interval_to_test)

    print(f"\n2. Fetching data for {symbol_to_test}...")
    try:
        stock_data = agent.fetch_data()
    except Exception as e:
        print(f"An unexpected error occurred in the main script during fetch_data: {e}")
        stock_data = pd.DataFrame() # Ensure stock_data is an empty DataFrame

    if not isinstance(stock_data, pd.DataFrame) or stock_data.empty:
        print(f"Data fetching for {symbol_to_test} failed or returned no data. Skipping display and save.")
    else:
        print(f"Data for {symbol_to_test} fetched successfully.")

        print("\n3. Displaying data (head):")
        agent.display_data(stock_data)

        print("\n4. Saving data to CSV...")
        # The agent's save_to_csv method will save it in a 'data/' subdirectory.
        filepath = agent.save_to_csv(data=stock_data, filename_prefix=csv_filename_prefix)
        if filepath:
            print(f"Data for {symbol_to_test} saved successfully to: {filepath}")
        else:
            print(f"Failed to save data for {symbol_to_test}.")

    print("\nDemonstration finished.")

if __name__ == "__main__":
    run_demonstration()

    # Example of how to test with a potentially problematic symbol directly in main
    # print("\n--- Testing with a non-existent symbol ---")
    # agent_error_test = DataCollectionAgent(symbol="NONEXISTENTICKERXYZ123", period="1d", interval="1d")
    # error_data = agent_error_test.fetch_data()
    # if error_data.empty:
    #     print("Correctly handled non-existent symbol: No data fetched.")
    # agent_error_test.display_data(error_data)
    # agent_error_test.save_to_csv(error_data)
    # print("--- End of non-existent symbol test ---\n")
