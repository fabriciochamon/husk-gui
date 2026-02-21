import dearpygui.dearpygui as dpg
import dearpygui_extend as dpge
import os, sys, json, re, tempfile, webbrowser, subprocess
import husk, selectables, houdini_paths, config
from pathlib import Path
from datetime import datetime
from fileseq import FileSequence
import log

FFMPEG_AVAILABLE = False

render_resolutions = {
	'HD 720': [1280, 720],
	'HD 1080': [1920, 1080],
	'HD 2160 (4k)': [3840, 2160],
	'Square 512px': [512, 512],
	'Square 1k': [1024, 1024],
	'Square 2k': [2048, 2048],
	'Square 4k': [4096, 4096],
}

# sets render resolution from preset combo item
def set_render_preset(sender, app_data, user_data):
	global render_resolutions
	dpg.set_value('res_x', render_resolutions[app_data][0])
	dpg.set_value('res_y', render_resolutions[app_data][1])

# sets text input path to item chosen on a dpge file browser instance
def set_fb_path(sender, files, cancel_pressed, user_data):
	if not cancel_pressed and len(files):
		f = files[0]
		dpg.set_value(user_data, f)
		if user_data=='usd': usd_on_load()						

# what to do when choosing a new .usd file ? 
def usd_on_load(usd):
	flash_message(f'Loading file: {os.path.basename(usd)}')
	husk.inspect_usd(usd)

# fades flashed messages (runs inside dpg render loop)
def fade_info_box(fade_speed=0.8):
	info_box_color = dpg.get_item_configuration('info_box')['color']
	info_box_alpha = info_box_color[3]*255
	info_box_alpha -= fade_speed
	if info_box_alpha<=0: info_box_alpha=0
	info_box_color = [info_box_color[0]*255, info_box_color[1]*255, info_box_color[2]*255, info_box_alpha]
	dpg.configure_item('info_box', color=info_box_color)

# center dpg item inside its parent
def center_widget(item, parent, size_percent=0.8, set_size=False, offset=[0,0]):
	ModalWindow_ID = item
	MainWindow_width = dpg.get_item_width(parent)
	MainWindow_height = dpg.get_item_height(parent)*0.35
	ModalWindow_width = dpg.get_item_width(item)
	ModalWindow_height = dpg.get_item_height(item)
	if set_size: dpg.configure_item(ModalWindow_ID, width=MainWindow_width*size_percent, height=MainWindow_height*size_percent)		
	dpg.set_item_pos(ModalWindow_ID, [int((MainWindow_width/2 - ModalWindow_width/2))+offset[0], int((MainWindow_height/2 - ModalWindow_height/2))+offset[1]])

# pyinstaller: get path relative to tmp directory (extracted files), if running from binary
def get_path(relative_path):
	if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
		bundle_dir = Path(sys._MEIPASS)
	else:
		bundle_dir = Path(__file__).parent

	bundle_dir = str(bundle_dir).replace('\\', '/')
	resource_path = f'{bundle_dir}/{relative_path}'
	
	return resource_path

# loads a texture from "images" folder into dpg
def load_image(filename):
	ret = False
	filepath = get_path('./images/'+filename)
	if not dpg.does_item_exist(filepath):
		width, height, channels, data = dpg.load_image(filepath)
		with dpg.texture_registry():
			dpg.add_static_texture(width=width, height=height, default_value=data, tag=filename)
		ret = True
	return [width, height, channels]

# check if Packman is installed, if true return its repo path
def get_packman():
	repo = ''
	home = Path.home()
	packman_folder = home / '.packman'
	if packman_folder.exists():
		prefs = packman_folder / 'prefs.json'
		with prefs.open('r') as f:
			repo = json.load(f)['package_repo'].replace('\\', '/')
	return repo

# helper function to get a rjustified label
def get_label(label, chars=25):
	label += ' '
	return label.rjust(chars)
		
# quickly set item tooltips		
def set_tooltip(txt, delay=0):
	with dpg.tooltip(parent=dpg.last_item(), delay=delay):
		dpg.add_text(txt)

# get available render delegates and draw buttons / icons
def redraw_delegates():
	dpg.hide_item('reload_delegates_btn')
	dpg.show_item('reload_delegates_loading')
	if 'render_delegate' in selectables.glb: del selectables.glb['render_delegate']

	flash_message('Reloading render delegates...', color=(255, 230, 0))

	grp = 'render_delegates'
	icon_size = 26
	dpg.delete_item(grp, children_only=True)
	delegates = husk.get_available_render_delegates()
	delegate_types_list = [item['brand'] for item in delegates]
	delegate_types_set = sorted(set(delegate_types_list))
	num_rows = max([delegate_types_list.count(item) for item in delegate_types_set])

	with dpg.table(parent=grp, header_row=False, policy=dpg.mvTable_SizingFixedFit):
		for delegate_type in delegate_types_set:
			dpg.add_table_column()

		with dpg.table_row():
			for delegate_type in delegate_types_set:
				texture_tag = f'logo_dl_{delegate_type.lower()}.png'
				dpg.add_image(texture_tag=texture_tag, width=icon_size, height=icon_size)

		delegate_index = 0
		for i in range(num_rows):
			with dpg.table_row():
				for delegate_type in delegate_types_set:
					delegates_from_type = [f'{item["label"]}' for item in delegates if item['brand']==delegate_type]
					delegates_names_from_type = [f'{item["name"]}' for item in delegates if item['brand']==delegate_type]
					if len(delegates_from_type)>i:
						btn_tag = f'delegate--{delegate_index}'
						dlg = [item for item in delegates if item['label']==delegates_from_type[i]][0]
						dpg.add_button(tag=btn_tag, label=delegates_from_type[i], user_data=['render_delegate', dlg, False], callback=selectables.set_item)
						set_tooltip(delegates_names_from_type[i], delay=0.5)
						dpg.bind_item_theme(btn_tag, 'toogle_OFF')
						delegate_index+=1
					else:
						dpg.add_text('')

	dpg.hide_item('reload_delegates_loading')
	dpg.show_item('reload_delegates_btn')

# loads all render delegate icons
def load_delegate_images():
	images_folder = get_path('./images')
	images = [item for item in os.listdir(images_folder) if item.startswith('logo_dl_')]
	for image in images: 
		load_image(image)

# flashes a status message (fades over time)
def flash_message(message='', color=(0, 191, 255)):
	dpg.set_value('info_box', message)
	dpg.split_frame()
	dpg.split_frame()
	update_flash_message_pos()
	dpg.configure_item('info_box', color=(color[0], color[1], color[2], 255))	

# set infobox pos bottom/right, relative to main viewport
def update_flash_message_pos():
	if os.name=='nt':
		dpg.set_item_pos('info_box', (dpg.get_viewport_width()-dpg.get_item_rect_size('info_box')[0]-30, dpg.get_viewport_height()-90))
	else:
		dpg.set_item_pos('info_box', (dpg.get_viewport_width()-dpg.get_item_rect_size('info_box')[0]-30, dpg.get_viewport_height()-50))

# what to do when a render starts ?
def render_started():
	dpg.set_value('render_progress', 0)
	dpg.configure_item('render_progress', overlay='0%')
	dpg.bind_item_theme('render_progress', 'progress_bar_theme_active')
	dpg.show_item('render_loading')
	dpg.set_value('render_status', 'Progress:')
			
# what to do when a render finishes ?
def render_finished():
	# ui updates
	#dpg.configure_item('log', tracked=False)
	dpg.bind_item_theme('render_progress', 'progress_bar_theme_inactive')
	dpg.set_value('render_progress', 1)
	dpg.configure_item('render_progress', overlay='Render Finished.')
	dpg.hide_item('render_loading')

	# update render status file 
	with open(config.statusfile, 'w') as f: f.write('stopped')			

# gets a dictionary with data from temp usdinfo file
def get_usd_info():
	usdinfo = None
	with open(config.usdinfofile, 'r') as f:
		usdinfo = json.load(f)
	return usdinfo

# open render output folder in native filebrowser
def open_render_output_folder():
	usdinfo = get_usd_info()
	if usdinfo:
		output = usdinfo['render_output'][0]
		webbrowser.open('file://' + os.path.dirname(output))

# open rendered sequence in houdini mplay binary
def open_render_in_mplay():
	usdinfo = get_usd_info()	
	if usdinfo:
		seq = FileSequence.findSequencesInList(usdinfo['render_output'])
		if len(seq): 
			seq=seq[0]

			seq_formatted = f'{seq.dirname()}{seq.basename()}*{seq.extension()}'
			
			# init env
			env = os.environ.copy()
			env['HOUDINI_DISABLE_OPENFX_DEFAULT_PATH'] = str(husk.HOUDINI_DISABLE_OPENFX_DEFAULT_PATH)
			packages_dir = dpg.get_value('packages_dir')
			if packages_dir.strip() != '':
				env['HOUDINI_PACKAGE_DIR'] = packages_dir

			mplay = houdini_paths.get_bin('mplay')
			cmd = f'"{mplay}" -p "{seq_formatted}"'
			flash_message(f'Launching render in Mplay...')
			proc = subprocess.run(cmd, env=env, start_new_session=True)

# creates a video using hoiiotool and ffmpeg
def create_video_from_render_output():
	
	# ctrl + click does not force ffmpeg overwrite, and opens the video output folder instead of the video file
	ctrl_clicked = dpg.is_key_down(dpg.mvKey_ModCtrl)

	# exits if ffmpeg not available
	if not is_ffmpeg_installed(): 
		flash_message(f'ffmpeg not available in path! Skipping video creation.', color=(255,0,0))
		return 

	usdinfo = get_usd_info()	
	if usdinfo:
		seq = FileSequence.findSequencesInList(usdinfo['render_output'])
		if len(seq): 
			
			dpg.show_item('render_loading')

			output_dir = config.tmpdir / 'tmp_hoiiotool'

			# make in/out sequence paths
			seq_in =seq[0]
			seq_out=seq[0].copy()
			seq_out.setExtension('png')
			seq_out.setDirname(output_dir)

			# make video file path
			seq_tmp = seq_out.copy()
			seq_tmp.setExtension = 'mp4'
			basename = seq_tmp.basename()
			video_file = output_dir / 'video' / basename[0:-1] / f'{basename}mp4'

			if not video_file.exists() or not ctrl_clicked:

				flash_message(f'Creating video...')

				os.makedirs(output_dir, exist_ok=True)
				dpg.set_value('render_progress', 0)
				dpg.configure_item('render_progress', overlay=f'0% [hoiiotool: converting images]')
				dpg.bind_item_theme('render_progress', 'progress_bar_theme_active')

				log.append('\n--- hoiiotool: Converting ACEScg -> sRGB ---\n\n')
				
				# init env
				env = os.environ.copy()
				env['HOUDINI_DISABLE_OPENFX_DEFAULT_PATH'] = str(husk.HOUDINI_DISABLE_OPENFX_DEFAULT_PATH)
				packages_dir = dpg.get_value('packages_dir')
				if packages_dir.strip() != '':
					env['HOUDINI_PACKAGE_DIR'] = packages_dir

				# hoiiotool converts betwen colorspaces (Acescg -> sRGB)
				hoiiotool = houdini_paths.get_bin('hoiiotool')
				cmd = f'"{hoiiotool}" -v --frames {seq_in.frameRange()} -i "{seq_in}" -colorconvert "ACES - ACEScg" "Output - sRGB" -o "{seq_out}"'
				proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, bufsize=1, start_new_session=True)

				# regex update progressbar
				pattern = f'{seq_out.dirname()}{seq_out.basename()}'
				pattern = re.compile(re.escape(pattern)+r'(\d+)'+seq_out.extension())
				num_converted_frames = 0
				for line in proc.stdout:
					match = pattern.search(line)
					if match:
						log.append(line)
						num_converted_frames+=1
						perc = float(num_converted_frames)/len(seq_out)*0.9
						dpg.set_value('render_progress', perc)
						dpg.configure_item('render_progress', overlay=f'{int(perc*100)}% [hoiiotool: converting images]')
				proc.wait()
				
				log.append('\n\n--- ffmpeg: creating video ---\n\n')
				
				# ffmpeg creates video from converted sequence
				dpg.configure_item('render_progress', overlay=f'{perc*100}% [ffmpeg: creating video]')
				os.makedirs(video_file.parent, exist_ok=True)
				padding = f'%0{seq_out.zfill()}d'
				overwrite_flag = '-y' if not ctrl_clicked else '-n'
				cmd = f'ffmpeg -loglevel quiet -stats {overwrite_flag} -i {seq_out.dirname()}{seq_out.basename()}{padding}{seq_out.extension()} {video_file}'
				proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env, bufsize=1, start_new_session=True)

				for line in proc.stdout:
					dpg.set_value('log', dpg.get_value('log')+line+'\n')
					log.auto_scroll_log(dpg.get_value('log'))

				log.append('Done.')
				dpg.configure_item('render_progress', overlay=f'Conversion finished.')
				dpg.set_value('render_progress', 1)
				dpg.bind_item_theme('render_progress', 'progress_bar_theme_inactive')

			# opens video or output folder
			target = video_file if not ctrl_clicked else video_file.parent
			webbrowser.open('file://' + str(target))

			dpg.hide_item('render_loading')
			
# check if ffmpeg is installed
def is_ffmpeg_installed():
	global FFMPEG_AVAILABLE

	if not FFMPEG_AVAILABLE:
		ffmpeg_installed = False
		try:
			out = subprocess.check_output('ffmpeg -version'.split())
			out = out.decode()
			if out.startswith('ffmpeg version'):
				ffmpeg_installed = True
		except:
			pass
		
		FFMPEG_AVAILABLE = ffmpeg_installed

	return FFMPEG_AVAILABLE

	