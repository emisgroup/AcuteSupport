import os, sys, subprocess

product_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
shared_script = os.path.abspath(os.path.join(product_dir, '..', 'shared', 'scripts', 'run_full_report.py'))

if __name__ == '__main__':
    result = subprocess.run([sys.executable, shared_script], cwd=product_dir)
    sys.exit(result.returncode)
