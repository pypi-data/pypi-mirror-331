import os
import pandas as pd
import logging
import seaborn as sns
import matplotlib.pyplot as plt
import sys

# Configure logging to write to a file
logging.basicConfig(
    filename='prepmagma.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def compile_res(res_folder:str, out_file:str, vars:list|str):
    """combine all the res files, and write out given vars and the cols"""
    ress = []
    for file in os.listdir(res_folder):
        dftmp = pd.read_csv(os.path.join(res_folder, file), comment='#', delim_whitespace=True)
        dftmp[f"{file}_p"] = dftmp.iloc[:,-1]
        ress.append(dftmp)
    
    # Start with the first dataframe
    if ress:
        res = ress[0]
        # Merge with remaining dataframes using inner join on VARIABLE column
        for df in ress[1:]:
            res = pd.merge(res, df, on="VARIABLE", how="inner")
    else:
        logging.warning("No files were processed")
        return

    res_out = res.loc[res.VARIABLE.isin(vars), ["VARIABLE", *[col for col in res.columns if "_p" in col]]] if isinstance(vars, list) else res.loc[res.VARIABLE.str.contains(vars), ["VARIABLE", *[col for col in res.columns if "_p" in col]]]
    # VARIABLE to index
    res_out.set_index("VARIABLE", inplace=True)
    res_out.to_csv(out_file, index=True, sep='\t')
    return res_out

def heatmap(res_out:pd.DataFrame, out_file:str):
    plt.figure(figsize=(res_out.shape[1], res_out.shape[0]))
    sns.heatmap(res_out, annot=True, cmap='Greys', vmin=0.05)
    plt.savefig(out_file)
    plt.close()
