import pandas as pd
import os

dfs = []
parquets_dir = "zkevm_txs"  # "zkevm_txs", "arb_txs"
for filename in os.listdir(parquets_dir):
    file_path = os.path.join(parquets_dir, filename)
    if os.path.isfile(file_path):
        try:
            df = pd.read_parquet(file_path)
            dfs.append(df)
        except:
            try:
                df = pd.read_parquet(file_path, engine="fastparquet")
                dfs.append(df)
            except:
                print(file_path)
final = pd.concat(dfs)
# final.drop(columns=["type"], inplace=True)  # saving errors, drop for now
final = final[["from", "to", "value"]]
print("before:", len(final))
# final = final.loc[final["input"] == "0x"]
print("after:", len(final))
# final.to_csv("parsed_sample_zkevm.csv", index=False)
try:
    final.to_parquet(
        "parsed_sample_zkevm.parquet", engine="fastparquet", index=False, append=False
    )
except:
    final.to_parquet(
        "parsed_sample_zkevm.parquet", engine="pyarrow", index=False, append=False
    )
