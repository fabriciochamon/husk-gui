from pathlib import Path
import tempfile

# huskgui temp folder
tmpdir = Path(tempfile.gettempdir()) / 'huskgui'

# huskgui temp files
usdinfofile = tmpdir / 'usdinfo.json'
statusfile  = tmpdir / 'render_status.txt'
logfile     = tmpdir / 'render_log.txt'

# usd settings
usd_allowed_ext = ('.usd', '.usda', '.usdc')

# houdini settings
houdini_disable_openfx_default_path = 1 # can fix errors regarding .ofx not being loaded upon husk start

# presets
preset_render_resolutions = {
	'HD 720': [1280, 720],
	'HD 1080': [1920, 1080],
	'HD 2160 (4k)': [3840, 2160],
	'Square 512px': [512, 512],
	'Square 1k': [1024, 1024],
	'Square 2k': [2048, 2048],
	'Square 4k': [4096, 4096],
}
