#!/usr/bin/env python3
"""Restaurar una copia del setup con Coucou cerrado."""
import argparse
import csv
import os
from pathlib import Path
import subprocess
from configure import restore

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backup', type=Path)
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if not args.dry_run:
        if os.name == 'nt':
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq coucou*', '/FO', 'CSV', '/NH'],
                                    capture_output=True, text=True, check=True)
            running = any(row and row[0].lower() in {'coucou.exe', 'coucou-hook.exe'} for row in csv.reader(result.stdout.splitlines()))
        else:
            running = subprocess.run(['pgrep', '-u', str(os.getuid()), '-x', 'coucou'],
                                     stdout=subprocess.DEVNULL).returncode == 0
        if running:
            parser.error('Cierra Coucou desde su icono y espera a que sus relés terminen antes de restaurar.')
    paths = restore(args.home, args.backup, args.dry_run)
    print(('Restauraría' if args.dry_run else 'Restaurados') + f' {len(paths)} archivos.')

if __name__ == '__main__':
    main()
