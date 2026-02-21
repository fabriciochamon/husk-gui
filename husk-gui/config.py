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
