# ---------------------- #
# USD PRE-RENDER SCRIPT
# ---------------------- #
from pxr import Usd
import os
from pathlib import Path

print('\n')
print('-------------------------')
print('HUSKGUI PRE-RENDER SCRIPT')
print('-------------------------')

# create output folders ("--make-output-path" Husk flag does not seems to work?)
print(' -Creating output folders for default Render Product')
render_products = [item for item in stage.GetPrimAtPath('/Render/Products').GetChildren() if item.GetTypeName()=='RenderProduct']
for item in render_products:
	product_name = item.GetAttribute('productName').Get(Usd.TimeCode(0))
	output_folder = os.path.dirname(product_name)
	os.makedirs(output_folder, exist_ok=True)

# set render status file (so that UI knows when a render started/stopped/finished)
print(' -Setting render status file')
tmpdir = Path(os.environ['HUSKGUI_TMP'])
statusfile = tmpdir / 'render_status.txt'
with open(statusfile, 'w') as f:
	f.write('rendering')

print('==================================================')
print('\n')
