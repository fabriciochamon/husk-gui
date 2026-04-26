import dearpygui.dearpygui as dpg
import os, re, json
from pathlib import Path
import utils

USER_PREFS_FILE = '~/.husk-gui/prefs.json'

def add_custom_install_path():
	path = dpg.get_value('custom_path')
	if os.path.isdir(path):
		path = path.replace('\\', '/').replace('//', '/')
		if path[-1]=='/': path = path[0:-1]
		prefs = get_user_prefs()
		if not 'custom_install_paths' in prefs.keys():
			prefs['custom_install_paths'] = [path]
		else:
			prefs['custom_install_paths'].append(path)
			prefs['custom_install_paths'] = list(set(prefs['custom_install_paths']))
		save_user_prefs(prefs)
		dpg.set_value('custom_path', '')
		dpg.hide_item('popup_add_custom_path')
		dpg.configure_item('houdini_version', items=get_houdini_installed_versions(fullpaths=True))
		dpg.set_value('houdini_version', path)
		utils.flash_message(f'Custom path added: {path}')

def rem_custom_install_path():
	path = dpg.get_value('houdini_version')
	prefs = get_user_prefs()
	if path in prefs['custom_install_paths']:
		idx = prefs['custom_install_paths'].index(path)
		del prefs['custom_install_paths'][idx]
		save_user_prefs(prefs)
		dpg.configure_item('houdini_version', items=get_houdini_installed_versions(fullpaths=True))
		dpg.set_value('houdini_version', get_houdini_installed_versions(fullpaths=True)[0])
		utils.flash_message(f'Custom path removed: {path}')

def get_user_prefs():
	path = os.path.expanduser(USER_PREFS_FILE)
	if not os.path.isfile(path):
		os.makedirs(os.path.dirname(path))
		prefs = {}
		with open(path, 'w') as f:
			json.dump(prefs, f, indent=4)
	else:
		with open(path, 'r') as f:
			prefs = json.load(f)
	return prefs

def save_user_prefs(prefs):
	path = os.path.expanduser(USER_PREFS_FILE)
	if os.path.isfile(path):
		with open(path, 'w') as f:
			json.dump(prefs, f, indent=4)

# get all available houdini versions installed on machine (mostly assumes installation on default folders!)
def get_houdini_installed_versions(fullpaths=False):
	installs = []
	install_path = None

	# windows
	if os.name == 'nt':
		programs = []
		install_path = 'C:/Program Files/Side Effects Software'
		programs = os.listdir(install_path)
		pattern = re.compile(r'Houdini (\d{2})\.(\d)\.(\d{3})')
	
	# linux
	else:
		install_path = '/opt'
		programs = os.listdir(install_path)
		pattern = re.compile(r'hfs(\d{2})\.(\d)\.(\d{3})')	
	
	for p in programs:
		if pattern.match(p): 
			if not fullpaths:
				installs.append(p.replace('hfs', '').replace('Houdini ', ''))
			else:
				program_path = os.path.join(install_path, p)
				program_path = program_path.replace('\\', '/')
				installs.append(program_path)

	# custom install paths
	prefs = get_user_prefs()
	if 'custom_install_paths' in prefs.keys():
		installs.extend(prefs['custom_install_paths'])
	
	return sorted(installs, reverse=True)

# get houdini install path for a specific houdini version
def get_houdini_install_path(houdini_version):
	installs = get_houdini_installed_versions(fullpaths=True)
	houdini = [item for item in installs if houdini_version in item]
	if len(houdini): 
		return houdini[0]
	else:
		return None

# get binary program inside $HFS/houdini/bin (for example "husk" or "mplay")
def get_bin(name):
	houdini_version = dpg.get_value('houdini_version')
	houdini = get_houdini_install_path(houdini_version)
	if houdini:
		if os.name == 'nt': 
			husk = Path(houdini) / 'bin' / f'{name}.exe'
		else: 
			husk = Path(houdini) / 'bin' / name
		return str(husk)
	else:
		return None