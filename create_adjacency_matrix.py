import pandas as pd
import numpy as np
from zkevm_top_contracts import contract_addresses

# Sample DataFrame
data_path = "/Users/jakubwarmuz/Desktop/priv/ETHMunich/parsed_sample_zkevm_0x.parquet"
tmp_df = pd.read_parquet(data_path, engine="fastparquet")
# tmp_df = pd.read_csv(
#     "/Users/jakubwarmuz/Desktop/priv/ETHMunich/parsed_sample_zkevm.csv"
# )
tmp_df.dropna(subset=["to", "from"], inplace=True)
tmp_df["from"] = tmp_df["from"].str.lower()
tmp_df["to"] = tmp_df["to"].str.lower()
addresses_to_remove = [x.lower() for x in contract_addresses]
tmp_df = tmp_df.loc[~tmp_df["from"].isin(addresses_to_remove)]
tmp_df = tmp_df.loc[~tmp_df["to"].isin(addresses_to_remove)]

# sample_size = 10000
# df = tmp_df.sample(n=sample_size)
df = tmp_df.copy(deep=True)


def create_adjacency_matrix(df, return_type="numpy"):
    # Get unique addresses
    addresses = pd.concat([df["from"], df["to"]]).unique()
    ordered_addresses = []

    # Create an empty matrix
    matrix = np.zeros((len(addresses), len(addresses)), dtype=int)

    # Populate the matrix
    for _, row in df.iterrows():
        ordered_addresses.append(row["from"])
        i = np.where(addresses == row["from"])[0][0]
        j = np.where(addresses == row["to"])[0][0]
        matrix[
            i, j
        ] = 1  # Set to 1 if there's a connection. Change to += 1 if you want to count multiple connections.

    # Convert to DataFrame for better visualization
    if return_type == "pandas":
        return (
            pd.DataFrame(matrix, index=addresses, columns=addresses),
            ordered_addresses,
        )

    elif return_type == "numpy":
        return matrix, ordered_addresses

    else:
        print("No return type specified, returning numpy matrix")

    return matrix


sample_size = "ALL_0X"
SAVE_PATH = f"adj_matrix_{sample_size}_sample.npy"
USERS_PATH = f"user_addresses_{sample_size}_sample.npy"
adj_matrix, addys = create_adjacency_matrix(df)
np.save(SAVE_PATH, adj_matrix)
np.save(USERS_PATH, addys)
