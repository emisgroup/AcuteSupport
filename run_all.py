import os
import sys
import subprocess
import argparse

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS = ['Symphony', 'Meds', 'OCM']

def run_product(product_name, action='report'):
    p_dir = os.path.join(ROOT_DIR, product_name)
    if not os.path.exists(p_dir):
        print(f"Error: Product directory '{product_name}' does not exist.")
        return False
    
    script_name = 'run_full_report.py' if action == 'report' else 'start_new.py'
    target_script = os.path.join(ROOT_DIR, 'shared', 'scripts', script_name)
    
    banner = '=' * 50
    print("\n" + banner)
    print(f" Running {action.upper()} for product: {product_name}")
    print(banner)
    res = subprocess.run([sys.executable, target_script], cwd=p_dir)
    return res.returncode == 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AcuteSupport Multi-Product Report Orchestrator')
    parser.add_argument('--product', choices=PRODUCTS, help='Run report for a specific product')
    parser.add_argument('--all', action='store_true', help='Run report for all products sequentially')
    parser.add_argument('--action', choices=['report', 'start_new'], default='report', help='Action to perform: report or start_new')
    
    args = parser.parse_args()
    
    if args.product:
        run_product(args.product, args.action)
    elif args.all:
        for p in PRODUCTS:
            run_product(p, args.action)
    else:
        print('Usage: python run_all.py --product <Symphony|Meds|OCM> OR python run_all.py --all')
