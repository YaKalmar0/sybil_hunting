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

HTTPS_RPC_PROVIDER_ZKEVM_1 = os.environ.get("HTTPS_RPC_PROVIDER_ZKEVM1")
HTTPS_RPC_PROVIDER_ZKEVM_2 = os.environ.get("HTTPS_RPC_PROVIDER_ZKEVM2")
HTTPS_RPC_PROVIDER_ZKEVM_3 = os.environ.get("HTTPS_RPC_PROVIDER_ZKEVM3")
HTTPS_RPC_PROVIDER_ZKEVM_4 = os.environ.get("HTTPS_RPC_PROVIDER_ZKEVM4")
HTTPS_RPC_PROVIDER_ZKEVM_5 = os.environ.get("HTTPS_RPC_PROVIDER_ZKEVM5")


HTTPS_PROVIDER_LIST = [
    HTTPS_RPC_PROVIDER_ZKEVM_1,
    HTTPS_RPC_PROVIDER_ZKEVM_2,
    HTTPS_RPC_PROVIDER_ZKEVM_3,
    HTTPS_RPC_PROVIDER_ZKEVM_4,
    HTTPS_RPC_PROVIDER_ZKEVM_5,
    # "https://zkevm-rpc.com",
    # "https://rpc.ankr.com/polygon_zkevm",
    # "https://polygonzkevm-mainnet.g.alchemy.com/v2/demo",
]

HTTPS_IDX = 0


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
            print("SAVING")
            df = pd.DataFrame(transactions)
            df["gasPrice"] = df["gasPrice"].astype(np.int64)
            df["gas"] = df["gas"].astype(np.int64)
            df["value"] = df["value"].astype(np.int64)
            if not os.path.isfile(f"zkevm_txs/{start}_{end}.parquet"):
                df.to_parquet(f"zkevm_txs/{start}_{end}.parquet", engine="fastparquet")
            else:
                df.to_parquet(
                    f"zkevm_txs/{start}_{end}.parquet",
                    engine="fastparquet",
                    append=True,
                )
            transactions = []

    # df.to_parquet(f"zkevm_txs/{start}_{end}.parquet", engine="fastparquet", append=True)
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
    start = 3000000
    end = 4000000
    get_transactions_concurrently(start, end, MAX_WORKERS, HTTPS_PROVIDER_LIST)
