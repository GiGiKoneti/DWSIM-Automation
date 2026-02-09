import os
import pandas as pd
import matplotlib.pyplot as plt

# Use a professional style if available, else default
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('ggplot')

def generate_plots(csv_path="results/results.csv"):
    """
    Standard visualization suite for DWSIM screening data.
    Generates high-resolution PNGs for reactor and column trends.
    """
    if not os.path.exists(csv_path):
        return

    df = pd.read_csv(csv_path)
    if df.empty:
        return

    output_dir = os.path.dirname(csv_path)
    
    _plot_reactor_trends(df, output_dir)
    _plot_column_trends(df, output_dir)

def _plot_reactor_trends(df, output_dir):
    data = df[df['Unit'] == 'PFR']
    if data.empty:
        return

    plt.figure(figsize=(10, 6))
    for temp in sorted(data['Param_2'].unique()):
        subset = data[data['Param_2'] == temp]
        plt.plot(subset['Param_1'], subset['KPI_Value'], marker='o', linewidth=2, label=f'{temp} K')
    
    plt.title('Isothermal Kinetic Reactor: Conversion vs. Volume', fontsize=14, fontweight='bold')
    plt.xlabel('Reactor Volume (m³)', fontsize=12)
    plt.ylabel('Conversion (%)', fontsize=12)
    plt.legend(title="Feed Temperature")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pfr_trends.png'), dpi=300)
    plt.close()

def _plot_column_trends(df, output_dir):
    data = df[df['Unit'] == 'Column']
    if data.empty:
        return

    plt.figure(figsize=(10, 6))
    for stages in sorted(data['Param_1'].unique()):
        subset = data[data['Param_1'] == stages]
        plt.plot(subset['Param_2'], subset['KPI_Value'], marker='s', linewidth=2, label=f'{int(stages)} Stages')
    
    plt.title('Ethanol Fractionation: Purity vs. Reflux Ratio', fontsize=14, fontweight='bold')
    plt.xlabel('Reflux Ratio (R)', fontsize=12)
    plt.ylabel('Distillate Purity (vol %)', fontsize=12)
    plt.legend(title="Total Stages")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'column_trends.png'), dpi=300)
    plt.close()
