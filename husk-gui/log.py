import dearpygui.dearpygui as dpg
from pathlib import Path
import tempfile, re, time, os
import textwrap 
import utils, config

# fetches statusfile, act upon its status (for example updating the progressbar when status=rendering)
def fetch():
	status = get_render_status_file()
	if status == 'rendering':
		with open(config.logfile, 'r') as f: contents = f.read()
		set_render_progress(contents)
		auto_scroll_log(contents)
	if status == 'finished':
		utils.render_finished()

# get status file (possible contents are: "stopped" | "rendering" | "finished")
def get_render_status_file():
	status = 'stopped'
	if not config.statusfile.exists(): 
		os.makedirs(config.statusfile.parent, exist_ok=True)
		config.statusfile.touch(exist_ok=True)
		with open(config.statusfile, 'w') as f: f.write('stopped')
	else:
		with open(config.statusfile, 'r') as f: status = f.read()
	return status

# dpg trick to autoscroll text (uses "tracked" and child window)
def auto_scroll_log(log_contents):
	FRAME_PADDING = 10
	lines = log_contents.splitlines()

	wrapped_lines = [textwrap.fill(line, width=128, replace_whitespace=False) for line in lines]
	wrapped_log = '\n'.join(wrapped_lines)

	if wrapped_log:
		#dpg.configure_item('log', tracked=True)
		dpg.set_item_height('log', dpg.get_text_size(wrapped_log)[1] + (2 * FRAME_PADDING))
		dpg.set_value('log', wrapped_log)	

# updates progress bar based on regex over "ALF_PROGRESS" lines
def set_render_progress(log_contents):
	matches = re.findall(r'ALF_PROGRESS (\d+)\%', log_contents)
	percentage = 0
	if len(matches): percentage = float(matches[-1])/100
	matches = re.findall(r'\((\d+) of (\d+)\)', log_contents)
	frame_curr = None
	frame_max = None
	if len(matches): 
		frame_curr = int(matches[-1][0])
		frame_max = int(matches[-1][1])
	dpg.set_value('render_progress', percentage)
	frame_txt = f' [frame {frame_curr} of {frame_max}]' if frame_curr else ''
	dpg.configure_item('render_progress', overlay=f'{int(percentage*100)}%{frame_txt}')

# appends widget log with more content
def append(content):
	new_content = f'{dpg.get_value('log')}\n{content}'
	dpg.set_value('log', new_content)
	auto_scroll_log(new_content)

# turns on/off log autoscrolling based on UI checkbox
def toogle_log_autoscroll(sender, app_data, user_data):
	dpg.configure_item('log', tracked=app_data)