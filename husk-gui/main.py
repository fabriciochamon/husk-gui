import dearpygui.dearpygui as dpg
import dearpygui_extend as dpge
import DearPyGui_DragAndDrop as dpg_dnd
import log, config
import utils, husk, houdini_paths

dpg.create_context()
dpg.create_viewport(title='Husk GUI', width=800, height=750)

# theme must be imported after dpg context is initialized
import theme

#-- external drag'n'drop support (windows only!)--#
dpg_dnd.initialize()

def drop(data, keys):
	f = data[0]
	if f.endswith(config.usd_allowed_ext): 
		dpg.set_value('usd', f)
		dpg.hide_item('logousd')
		utils.usd_on_load(f)
	dpg.hide_item('logononsupported')

def drag_enter(data, keys):
	f = data[0]
	if f.endswith(config.usd_allowed_ext):
		dpg.show_item('logousd')
		utils.center_widget('logousd', 'main_win')
	else:
		dpg.show_item('logononsupported')
		utils.center_widget('logononsupported', 'main_win')	
	
def drag_leave():
	dpg.hide_item('logousd')
	dpg.hide_item('logononsupported')
#-- external drag'n'drop support (windows only!)--#

# main UI
with dpg.window(tag='main_win') as mainwin:

	with dpg.collapsing_header(label='Settings', default_open=True):
		dpg.bind_item_theme(dpg.last_item(), 'section_header_theme')

		with dpg.table(width=-1, header_row=False, policy=dpg.mvTable_SizingStretchProp):
			dpg.add_table_column()
			dpg.add_table_column()
			dpg.add_table_column()

			# usd file
			with dpg.table_row():
				with dpg.group(horizontal=True):
					dpg.add_text(utils.get_label('USD file:'))
					dpg.add_loading_indicator(tag='usd_loading', color=(0, 191, 255), radius=1, speed=5, show=False)
				dpg.add_input_text(tag='usd', hint='Load file or drag .usd into window...', width=-1)
				dpge.add_file_browser(
					label=dpge.file_browser.ICON_FILE,
					pos=[10,30],
					width=650,
					height=500,
					show_as_window=True, 
					show_ok_cancel=True, 
					allow_multi_selection=False, 
					collapse_sequences=True,
					filetype_filter=[{'label': 'Universal Scene Description', 'formats': [item.replace('.', '') for item in list(config.usd_allowed_ext)]}],
					callback=utils.set_fb_path,
					user_data='usd')

			# houdini version to launch husk from
			with dpg.table_row():
				dpg.add_text(utils.get_label('Houdini (Husk) version:'))
				dpg.add_combo(tag='houdini_version', fit_width=True, items=houdini_paths.get_houdini_installed_versions(), default_value=houdini_paths.get_houdini_installed_versions()[0], callback=utils.redraw_delegates)
				utils.set_tooltip('Where to find the "husk" executable')
				dpg.add_spacer(width=-1)

			# override packages dir
			with dpg.table_row():
				dpg.add_text(utils.get_label('Override packages dir:'))
				dpg.add_input_text(tag='packages_dir', default_value=utils.get_packman(), hint='override default packages...', width=-1)
				dpge.add_file_browser(
					label=dpge.file_browser.ICON_FOLDER,
					pos=[10,30],
					width=650,
					height=500,
					dirs_only=True,
					show_as_window=True, 
					show_ok_cancel=True, 
					allow_multi_selection=False, 
					collapse_sequences=True,
					show_hidden_files=True,
					callback=utils.set_fb_path,
					user_data='packages_dir')

			# render delegates
			with dpg.table_row():
				dpg.add_text(utils.get_label('Render delegate:'))
				with dpg.group(horizontal=True):
					utils.load_image('icon_reload.png')
					dpg.add_image_button(texture_tag='icon_reload.png', tag='reload_delegates_btn', tint_color=(255, 230, 0), callback=utils.redraw_delegates)
					utils.set_tooltip('Reload render delegates.\n(Available delegates can change based on Houdini version and loaded packages)', delay=0.2)
					dpg.add_loading_indicator(tag='reload_delegates_loading', color=(255, 230, 0), radius=1, speed=5, show=False)
					dpg.bind_item_theme('reload_delegates_btn', 'transparent_button_theme')
					dpg.add_group(tag='render_delegates', horizontal=True)
				dpg.add_spacer(width=-1)

			# frame range
			with dpg.table_row():
				dpg.add_text(utils.get_label('Frame range:'))
				with dpg.group(horizontal=True):
					dpg.add_input_text(tag='framerange_start', default_value='1', width=50, no_spaces=True, decimal=True)
					dpg.add_text('to')
					dpg.add_input_text(tag='framerange_end', default_value='1', width=50, no_spaces=True, decimal=True)
				dpg.add_spacer(width=-1)

			# render resolution
			with dpg.table_row():
				dpg.add_text(utils.get_label('Render resolution:'))
				with dpg.group(horizontal=True):
					dpg.add_input_text(tag='res_x', default_value='1920', width=50, no_spaces=True, decimal=True)
					dpg.add_text(' x')
					dpg.add_input_text(tag='res_y', default_value='1080', width=49, no_spaces=True, decimal=True)
					dpg.add_text('px')
					dpg.add_spacer(width=20)
					dpg.add_text('load preset:')
					dpg.add_combo(tag='res_presets', items=list(utils.render_resolutions.keys()), default_value=list(utils.render_resolutions.keys())[1], fit_width=True, callback=utils.set_render_preset)
				dpg.add_spacer(width=-1)

			# mplay monitor
			with dpg.table_row():
				dpg.add_text(utils.get_label('Mplay monitor:'))
				with dpg.group(horizontal=True):
					dpg.add_checkbox(tag='mplay_monitor')
					dpg.add_text('aovs:')
					dpg.add_input_text(tag='mplay_aovs', default_value='-', width=200)
					utils.set_tooltip('Comma separated list of AOVs to monitor. ("-" =  all aovs)')
				dpg.add_spacer(width=-1)

	with dpg.collapsing_header(label='Render log', default_open=True):
		dpg.bind_item_theme(dpg.last_item(), 'section_header_theme')

		# output log
		with dpg.child_window(tag='logwindow', width=-1, height=-170, border=False):
			dpg.add_input_text(tag='log', multiline=True, readonly=True, tracked=True, track_offset=1, width=-1, height=-1)
			dpg.bind_item_theme(dpg.last_item(), 'render_log_theme')

		# autoscroll log checkbox
		with dpg.table(width=-1, header_row=False, policy=dpg.mvTable_SizingStretchProp):
			dpg.add_table_column()
			dpg.add_table_column(width_stretch=False, width_fixed=True)
			with dpg.table_row():
				dpg.add_spacer(width=-1)
				dpg.add_checkbox(tag='autoscroll_log', default_value=True, label='autoscroll', callback=log.toogle_log_autoscroll)	
				dpg.bind_item_font(dpg.last_item(), theme.font_small)
		
	# progress bar and utility buttons
	with dpg.table(width=-1, header_row=False, policy=dpg.mvTable_SizingStretchProp):
		dpg.add_table_column()
		dpg.add_table_column()
		dpg.add_table_column()
		with dpg.table_row():
			with dpg.group(horizontal=True):
				dpg.add_loading_indicator(tag='render_loading', color=(117, 240, 10), radius=1, speed=5, show=False)
				dpg.add_text('Progress:', tag='render_status')
			with dpg.group(horizontal=True):
				dpg.add_progress_bar(tag='render_progress', overlay='0%', width=-1)
				dpg.bind_item_theme('render_progress', 'progress_bar_theme_inactive')
			with dpg.group(horizontal=True):
				utils.load_image('icon_folder.png')
				utils.load_image('icon_mplay.png')
				utils.load_image('icon_create_video.png')
				dpg.add_image_button(texture_tag='icon_folder.png', width=16, height=16, callback=utils.open_render_output_folder)
				utils.set_tooltip('Open render output folder', delay=0.2)
				dpg.add_image_button(texture_tag='icon_mplay.png', width=16, height=16, callback=utils.open_render_in_mplay)
				utils.set_tooltip('Open render sequence in MPlay', delay=0.2)
				dpg.add_image_button(texture_tag='icon_create_video.png', width=16, height=16, callback=utils.create_video_from_render_output)
				utils.set_tooltip('Create video (ffmpeg)\n(Ctrl+click to open video output folder)', delay=0.2)

	# render button
	dpg.add_spacer(height=10)
	dpg.add_button(label='RENDER', callback=husk.render, width=-1, height=40)
	dpg.bind_item_font(dpg.last_item(), theme.font_big)
	dpg.bind_item_theme(dpg.last_item(), 'render_btn_theme')

	# info box (flashed messages)
	dpg.add_text('', tag='info_box', parent='main_win')
	dpg.bind_item_font(dpg.last_item(), theme.font_info_box)
	utils.update_flash_message_pos()

# load extra images
w,h,_ = utils.load_image('logo_usd.png')
logo_size = 0.5
utils.load_image('logo_nonsupported.png')
dpg.add_image('logo_usd.png', tag='logousd', parent='main_win', show=False, width=w*logo_size, height=h*logo_size)
dpg.add_image('logo_nonsupported.png', tag='logononsupported', parent='main_win', show=False, width=w*logo_size, height=h*logo_size)
utils.load_delegate_images()

# drag'n'drop callbacks
dpg_dnd.set_drop(drop)
dpg_dnd.set_drag_enter(drag_enter)
dpg_dnd.set_drag_leave(drag_leave)

# dpg init
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window(mainwin, True)

# render loop
while dpg.is_dearpygui_running():
	utils.fade_info_box()
	log.fetch()
	dpg.render_dearpygui_frame()

# dpg terminate
dpg.destroy_context()