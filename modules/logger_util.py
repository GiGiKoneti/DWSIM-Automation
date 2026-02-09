import os
import pandas as pd

def save_results(data_list, filename="results.csv"):
    """
    Standardizes simulation output to a CSV format.
    Ensures directory integrity regardless of execution environment.
    """
    # Use path relative to the script execution directory
    base_dir = os.getcwd()
    target_dir = os.path.join(base_dir, "results")
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        
    df = pd.DataFrame(data_list)
    export_path = os.path.join(target_dir, filename)
    
    # Export with standardized precision settings
    df.to_csv(export_path, index=False, float_format="%.6f")
    
    print(f"Dataset persisted to: {os.path.relpath(export_path, base_dir)}")