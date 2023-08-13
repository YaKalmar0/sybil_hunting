import pandas as pd
import requests
from tqdm import tqdm
import time
import os

# Read the CSV file
addresses_df = pd.read_csv('eliminatedSybilAttackers.csv')
addresses = addresses_df['address'].tolist()  # Assuming the column name is 'address'

# Base URL for the arbiscan API
base_url = "https://api.arbiscan.io/api"

# List to store all non-normal transactions
all_transactions = []

# Iterate over each address
for address in tqdm(addresses_df['address']):
    
    # Define the parameters for the API call
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": "YOURAPIKEY"  # Replace with your API key
    }

    MAX_RETRIES = 3  # Define a maximum number of retries to avoid infinite loops

    for _ in range(MAX_RETRIES):
        # Make the API call
        response = requests.get(base_url, params=params)

        # Check if the response was successful and is JSON
        if response.status_code == 200 and 'application/json' in response.headers['Content-Type']:
            try:
                data = response.json()
                
                # Check if 'result' is a list and not a string
                if isinstance(data['result'], list):
                    # Filter out normal transactions
                    non_normal_transactions = [tx for tx in data['result'] if tx['isError'] == '1' or tx['contractAddress'] != '']
                    all_transactions.extend(non_normal_transactions)
                    break  # Exit the loop if successful
                else:
                    print(f"Unexpected response for address {address}: {data['result']}")
                    break  # Exit the loop if there's an unexpected response
            except ValueError:
                print(f"Failed to parse JSON response for address {address}. Response content: {response.text}")
                break  # Exit the loop if there's a JSON parsing error
        elif "Just a moment..." in response.text:
            time.sleep(1)  # Sleep for 1 second
        else:
            print(f"Unexpected response status or content type for address {address}.")
            break  # Exit the loop if there's an unexpected response status or content type


    if len(all_transactions) > 50:
        print("Saving to parquet file")
        transactions_df = pd.DataFrame(all_transactions)
        if not os.path.isfile('arbi_trx_sybils.parquet'):
            transactions_df.to_parquet('arbi_trx_sybils.parquet', engine='fastparquet')
        else:
            transactions_df.to_parquet('arbi_trx_sybils.parquet', engine='fastparquet', append=True)
        print("Saved to parquet file")
        all_transactions = []


# Convert the list of transactions to a DataFrame
transactions_df = pd.DataFrame(all_transactions)

# Save the DataFrame to a parquet file
transactions_df.to_parquet('arbi_trx_sybils.parquet', engine='fastparquet', append=True)

