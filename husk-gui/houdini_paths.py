import dearpygui.dearpygui as dpg
import os, re
from pathlib import Path

# get all available houdini versions installed on machine (assumes installation on default folders!)
def get_houdini_installed_versions(fullpaths=False):
	installs = []
	install_path = None

	# windows
	if os.name == 'nt':
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
				installs.append(os.path.join(install_path, p))

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