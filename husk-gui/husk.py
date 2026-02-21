import dearpygui.dearpygui as dpg
import subprocess, os, re
from pathlib import Path
import tempfile, json
import utils, selectables, log, config
from fileseq import FileSequence
import houdini_paths

# GLOBAL VARS
HOUDINI_DISABLE_OPENFX_DEFAULT_PATH = 1

# starting from Houdini 21.0.170, husk accepts the --gpu flag, to make gpu based render delegates available
# this function handles where this is usable for the render command based on currently selected houdini version
def get_gpu_flag():
	gpu_flag='' 
	houdini_version = dpg.get_value('houdini_version')
	major,minor,build = (int(houdini_version.split('.')[0]), int(houdini_version.split('.')[1]), int(houdini_version.split('.')[2]))
	if major >= 21 and build >= 170: gpu_flag='--gpu'
	return gpu_flag

# using husk, reads available render delegates (based on houdini version combo)
def get_available_render_delegates():
	delegates = []
	packages_dir = dpg.get_value('packages_dir')
	houdini_version = dpg.get_value('houdini_version')
	husk = houdini_paths.get_bin('husk')
	env = os.environ.copy()
	env['HOUDINI_DISABLE_OPENFX_DEFAULT_PATH'] = str(HOUDINI_DISABLE_OPENFX_DEFAULT_PATH)
	if packages_dir.strip() != '':
		env['HOUDINI_PACKAGE_DIR'] = packages_dir

	gpu_flag=get_gpu_flag()

	cmd = f'{husk} --list-renderers {gpu_flag}'
	proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
	out = proc.stderr
	pattern = re.compile(r' - (.*)')
	for line in out.split('\n'):
		if pattern.match(line):
			delegate_str = pattern.match(line).groups()[0]
			name  = delegate_str[0: delegate_str.index('(')].strip()
			label = delegate_str[delegate_str.index('(')+1:].strip().replace(')', '')
			
			brands = {
				'karma': 'Karma',
				'gl': 'Houdini',
				'renderman': 'Renderman',
				'arnold': 'Arnold',
				'redshift': 'Redshift',
			}

			for k,v in brands.items():
				if k in label.lower(): brand = v
			
			delegate = {
				'name': name, 
				'label': label,
				'brand': brand,
			}

			if not 'unsupported' in label:				
				delegates.append(delegate)

	return delegates

# main render command
def render():
	usd = dpg.get_value('usd')

	# is .usd file defined?
	if os.path.isfile(usd):

		# is render delegate defined?
		if 'render_delegate' in selectables.glb.keys():

			# init UI (progress bar, etc)
			utils.render_started()
			
			# get husk bin
			husk = houdini_paths.get_bin('husk')

			# init env
			env = os.environ.copy()
			env['HUSKGUI_TMP'] = str(config.tmpdir)
			env['HOUDINI_DISABLE_OPENFX_DEFAULT_PATH'] = str(HOUDINI_DISABLE_OPENFX_DEFAULT_PATH)
			packages_dir = dpg.get_value('packages_dir')
			if packages_dir.strip() != '':
				env['HOUDINI_PACKAGE_DIR'] = packages_dir

			# build command
			delegate = selectables.glb['render_delegate']['name']
			fstart = int(dpg.get_value('framerange_start'))
			fend = int(dpg.get_value('framerange_end'))
			nframes = fend-fstart+1
			framerange = f'-f {fstart} -n {nframes}' if dpg.get_value('override_framerange') else ''
			render_res = dpg.get_value('res_x') + ' ' + dpg.get_value('res_y')
			mplay = f'--mplay-monitor \"{dpg.get_value("mplay_aovs")}\"' if dpg.get_value('mplay_monitor') else ''
			gpu_flag = ''#get_gpu_flag()

			# pre/post render scripts paths
			pre_render_script = utils.get_path('pre_render.py')
			post_render_script = utils.get_path('post_render.py')

			cmd = f'"{husk}" -R {delegate} -f {fstart} -n {nframes} -r {render_res} {mplay} {gpu_flag} -Va1 --prerender-script "{pre_render_script}" --postrender-script "{post_render_script}" --stdout "{config.logfile}" {usd}'
			utils.flash_message(f'RENDERING {os.path.basename(usd)}', color=(111, 235, 2))

			print(f'Render commmand received:\n\n{cmd}')
			
			# run in subprocess
			proc = subprocess.run(cmd, env=env, start_new_session=True)

		else:
			utils.flash_message(f'Please choose a render delegate!', color=(255, 200, 3))

	else:
		utils.flash_message(f'No .usd file selected!', color=(255,0,0))
		
# to avoid installing usd python bindings, this simply uses husk with a pre-render script (usd_inspection.py)
# fetches info from selected .usd, saves data into a temp .json file, and makes it available for the UI
def inspect_usd(usd):
	dpg.show_item('usd_loading')

	husk = houdini_paths.get_bin('husk')
	env = os.environ.copy()
	env['HUSKGUI_TMP'] = str(config.tmpdir)
	usd_inspection_script = utils.get_path('usd_inspection.py')
	cmd = f'"{husk}" --prerender-script "{usd_inspection_script}" {usd}'
	proc = subprocess.run(cmd, env=env)
	
	# load temp .json with usd info
	tmpdir = Path(tempfile.gettempdir())
	tmpfile = tmpdir / 'huskgui_usdinfo.json'

	usdinfo = None
	with open(config.usdinfofile, 'r') as f:
		usdinfo = json.load(f)

	if usdinfo:
		
		# resolution
		dpg.set_value('res_x', usdinfo['render_resolution'][0])
		dpg.set_value('res_y', usdinfo['render_resolution'][1])

		# framerange
		seq = FileSequence.findSequencesInList(usdinfo['render_output'])
		if len(seq): 
			seq=seq[0]
			dpg.set_value('framerange_start', seq.start())
			dpg.set_value('framerange_end', seq.end())
		else:
			dpg.set_value('framerange_start', 1)
			dpg.set_value('framerange_end', 1)

	dpg.hide_item('usd_loading')