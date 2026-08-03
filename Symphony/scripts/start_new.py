"""
Start New Script

Moves all files from:
 - outputs/charts/ -> outputs/Archived/charts/
 - outputs/reports/ -> outputs/Archived/reports/
 - outputs/tables/ -> outputs/Archived/tables/
 - data/processed/ -> data/archive/

Renames any target files that clash by appending a timestamp (_YYYYMMDD_HHMMSS).
"""
import os
import shutil
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')
ARCHIVED_DIR = os.path.join(OUTPUTS_DIR, 'Archived')

DATA_PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
DATA_ARCHIVE_DIR = os.path.join(BASE_DIR, 'data', 'archive')

SUBFOLDERS = ['charts', 'reports', 'tables']

def move_files_with_timestamp_collision(src_dir, dst_dir, rel_name_prefix=""):
    os.makedirs(dst_dir, exist_ok=True)
    if not os.path.exists(src_dir):
        return 0

    moved_count = 0
    for fname in os.listdir(src_dir):
        src_file = os.path.join(src_dir, fname)
        if os.path.isdir(src_file):
            continue

        dst_file = os.path.join(dst_dir, fname)
        if os.path.exists(dst_file):
            name, ext = os.path.splitext(fname)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_fname = f"{name}_{timestamp}{ext}"
            dst_file = os.path.join(dst_dir, new_fname)

        shutil.move(src_file, dst_file)
        rel_src = os.path.join(rel_name_prefix, fname) if rel_name_prefix else fname
        rel_dst = os.path.relpath(dst_file, BASE_DIR)
        print(f"Archived: {rel_src} -> {rel_dst}")
        moved_count += 1

    return moved_count

def start_new():
    total_moved = 0
    
    # 1. Archive outputs subfolders
    for sub in SUBFOLDERS:
        src = os.path.join(OUTPUTS_DIR, sub)
        dst = os.path.join(ARCHIVED_DIR, sub)
        total_moved += move_files_with_timestamp_collision(src, dst, rel_name_prefix=f"outputs/{sub}")

    # 2. Archive data/processed files
    total_moved += move_files_with_timestamp_collision(DATA_PROCESSED_DIR, DATA_ARCHIVE_DIR, rel_name_prefix="data/processed")

    print(f"Completed 'Start New'. Total files archived: {total_moved}")

if __name__ == '__main__':
    start_new()

