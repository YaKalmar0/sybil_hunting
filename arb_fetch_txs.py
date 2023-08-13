import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from dotenv import load_dotenv, find_dotenv
from web3 import Web3
import os, sys
import time
from tqdm import tqdm
import multiprocessing as mp
import numpy as np

MAX_WORKERS = mp.cpu_count() - 1

REQUESTS_PER_SECOND = 180  # Adjust this based on your rate limit
DELAY = 1.0 / REQUESTS_PER_SECOND

load_dotenv(find_dotenv())

HTTPS_RPC_PROVIDER_arb = os.environ.get("HTTPS_RPC_PROVIDER_arb")


HTTPS_PROVIDER_LIST = [
    HTTPS_RPC_PROVIDER_arb,
    # "https://arb-rpc.com",
    # "https://rpc.ankr.com/polygon_arb",
    # "https://polygonarb-mainnet.g.alchemy.com/v2/demo",
]


def get_transactions_chunk(start, end, rpc_endpoint):
    # Connect to the provided RPC endpoint
    web3 = Web3(Web3.HTTPProvider(rpc_endpoint))
    transactions = []
    for x in tqdm(range(start, end)):
        try:
            block = web3.eth.getBlock(x, True)
        except:
            time.sleep(DELAY)
            block = web3.eth.getBlock(x, True)
        if len(block.transactions) > 0:
            for transaction in block.transactions:
                transactions.append(
                    {
                        "nonce": transaction["nonce"],
                        "gasPrice": transaction["gasPrice"],
                        "gas": transaction["gas"],
                        "to": transaction["to"],
                        "value": transaction["value"],
                        "input": transaction["input"],
                        "hash": transaction["hash"].hex(),
                        "from": transaction["from"],
                        "blockNumber": transaction["blockNumber"],
                        "transactionIndex": transaction["transactionIndex"],
                        "type": transaction["type"],
                    }
                )

        if len(transactions) % 50 == 0 and len(transactions) > 0:
            df = pd.DataFrame(transactions)
            # df["gasPrice"] = df["gasPrice"].astype(np.int64)
            # df["gas"] = df["gas"].astype(np.int64)
            # df["value"] = df["value"].astype(np.int64)
            df["gasPrice"] /= 1e8
            df["gas"] /= 1e8
            df["value"] /= 1e8
            if not os.path.isfile(f"arb_txs/{start}_{end}.parquet"):
                try:
                    df.to_parquet(
                        f"arb_txs/{start}_{end}.parquet", engine="fastparquet"
                    )
                except:
                    try:
                        df.to_parquet(
                            f"arb_txs/{start}_{end}.parquet", engine="pyarrow"
                        )
                    except:
                        print(
                            f"Failed to save {df['blockNumber'].min()}_{df['blockNumber'].max()}"
                        )
            else:
                try:
                    df.to_parquet(
                        f"arb_txs/{start}_{end}.parquet",
                        engine="fastparquet",
                        append=True,
                    )
                except:
                    try:
                        df.to_parquet(
                            f"arb_txs/{start}_{end}.parquet",
                            engine="pyarrow",
                            append=True,
                        )
                    except:
                        print(
                            f"Failed to save {df['blockNumber'].min()}_{df['blockNumber'].max()}"
                        )
            transactions = []

    # df.to_parquet(f"arb_txs/{start}_{end}.parquet", engine="fastparquet", append=True)
    print(
        f"Finished searching blocks {start} through {end} and found {len(df)} transactions"
    )


def get_transactions_concurrently(start, end, num_processes, rpc_endpoints):
    # Calculate the number of blocks each process should handle
    chunk_size = (end - start) // num_processes

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [
            executor.submit(
                get_transactions_chunk,
                start + i * chunk_size,
                start + (i + 1) * chunk_size,
                rpc_endpoints[i % len(rpc_endpoints)],
            )
            for i in range(num_processes)
        ]

        # Wait for all futures to complete
        for future in futures:
            future.result()


# Example usage
if __name__ == "__main__":
    start = 13168652
    end = 15951301
    MAX_WORKERS = 5
    get_transactions_concurrently(start, end, MAX_WORKERS, HTTPS_PROVIDER_LIST)
