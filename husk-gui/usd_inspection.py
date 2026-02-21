from pxr import Usd
from pathlib import Path
import tempfile, json, os

# this module reads useful info from a .usd file when it gets loaded into UI (via filebrowser or drag'n'drop)
# this is ran as a pre-render script in husk, hence USD python modules are available from the houdini install
usdinfo = {}

# get default render settings / render product from scene
render_product = [item for item in stage.GetPrimAtPath('/Render/Products').GetChildren() if item.GetTypeName()=='RenderProduct'][0]
render_settings = stage.GetPrimAtPath('/Render/rendersettings')

usdinfo['render_resolution'] = list(render_settings.GetAttribute('resolution').Get())
usdinfo['render_output'] = [render_product.GetAttribute('productName').Get(timesample) for timesample in render_product.GetAttribute('productName').GetTimeSamples()]

# saves to temp .json file, so it is persisted and available for UI / other proccesses
tmpdir = Path(os.environ['HUSKGUI_TMP'])
tmpfile = tmpdir / 'usdinfo.json'

with open(tmpfile, 'w') as f:
	json.dump(usdinfo, f, indent=4)
