import os
import sys
import platform
import itertools
import yaml
import logging
from multiprocessing import Pool, cpu_count
from modules.dwsim_engine import DWSIMEngine
from modules.reactor_logic import run_pfr_calculation
from modules.column_logic import run_column_calculation
from modules.logger_util import save_results
from modules.plotting_util import generate_plots

# --- Architecture & Environment Protection ---
if platform.machine() == "arm64" and "ARCH_CHECK" not in os.environ:
    os.environ["ARCH_CHECK"] = "1"
    os.execv('/usr/bin/arch', ['arch', '-x86_64', sys.executable] + sys.argv)

def setup_logging(config):
    """Configures professional tiered logging."""
    log_path = config['system']['log_file']
    log_dir = os.path.dirname(log_path)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("DWSIM_Automation")

def run_pfr_case(args):
    """Wrapper for parallel reactor execution."""
    vol, temp, config_path = args
    engine = DWSIMEngine(config_path)
    fs = engine.create_flowsheet()
    res = run_pfr_calculation(engine.automation, fs, vol, temp)
    return {
        "Unit": "PFR", 
        "Reactor_Vol_m3": vol, 
        "Feed_Temp_K": temp,
        "Solved": res["success"], 
        "KPI_Value": res["conversion"],
        "Outlet_B_Flow": res["outlet_B_flow"], 
        "Outlet_Temp": res["outlet_temp"],
        "Heat_Duty_kW": res["heat_duty"], 
        "Error": res["error"]
    }

def run_col_case(args):
    """Wrapper for parallel column execution."""
    stages, reflux, config_path = args
    engine = DWSIMEngine(config_path)
    fs = engine.create_flowsheet()
    res = run_column_calculation(engine.automation, fs, stages, reflux)
    return {
        "Unit": "Column", 
        "Column_Stages": stages, 
        "Reflux_Ratio": reflux,
        "Solved": res["success"], 
        "KPI_Value": res["purity"],
        "Condenser_Duty_kW": res["condenser_duty"], 
        "Reboiler_Duty_kW": res["reboiler_duty"],
        "Feed_Stage": res["feed_stage"], 
        "Error": res["error"]
    }

def main():
    config_path = "config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    logger = setup_logging(config)
    logger.info("Initializing Senior-Level Multi-Core Screening Sweep...")
    
    dataset = []
    parallel = config['system'].get('parallel_execution', False)
    workers = cpu_count() if parallel else 1
    
    # 1. Reactor Phase
    logger.info(f"Phase I: Kinetic Reactor Sweep (Workers: {workers})")
    pfr_params = config['sweep_params']['pfr']
    pfr_configs = [(v, t, config_path) for v, t in itertools.product(pfr_params['volumes'], pfr_params['temperatures'])]
    
    if parallel:
        with Pool(workers) as pool:
            dataset.extend(pool.map(run_pfr_case, pfr_configs))
    else:
        dataset.extend([run_pfr_case(cfg) for cfg in pfr_configs])

    # 2. Separation Phase
    logger.info(f"Phase II: Multistage Separation Sweep (Workers: {workers})")
    col_params = config['sweep_params']['column']
    col_configs = [(s, r, config_path) for s, r in itertools.product(col_params['stages'], col_params['reflux_ratios'])]
    
    if parallel:
        with Pool(workers) as pool:
            dataset.extend(pool.map(run_col_case, col_configs))
    else:
        dataset.extend([run_col_case(cfg) for cfg in col_configs])

    # Persist and Plot
    save_results(dataset)
    generate_plots()
    
    logger.info("Simulation matrix execution complete. Audit results available in results/results.csv")

if __name__ == "__main__":
    main()