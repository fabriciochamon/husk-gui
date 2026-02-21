# ---------------------- #
# USD POST-RENDER SCRIPT
# ---------------------- #
from pxr import Usd
import os
from pathlib import Path

print('\n')
print('--------------------------')
print('HUSKGUI POST-RENDER SCRIPT')
print('--------------------------')

# set render status file (so that UI knows when a render started/stopped/finished)
print(' -Setting render status file')
tmpdir = Path(os.environ['HUSKGUI_TMP'])
statusfile = tmpdir / 'render_status.txt'
with open(statusfile, 'w') as f:
	f.write('finished')

print('==================================================')
print('\n')
