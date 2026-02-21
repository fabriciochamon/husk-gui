import dearpygui.dearpygui as dpg

# this module handles checked/unckecked buttons 
# in this project is used for render delegates

# global dict to store selections
glb = {}

def toggle_off_all_items(name_prefix):
	index = 0
	while dpg.does_item_exist(f'{name_prefix}--{index}'):
		tag = f'{name_prefix}--{index}'
		dpg.bind_item_theme(tag, 'toogle_OFF')
		index += 1

def set_item(sender, app_data, user_data):
	global glb
	k = user_data[0]
	v = user_data[1]

	# handles multi-selection toogles
	if len(user_data) > 2 and user_data[2]:

		if k in glb.keys():

			isOFF = v not in glb[k]

			if isOFF:
				glb[k].append(v)
				dpg.bind_item_theme(sender, 'toogle_ON')
			else:
				try:
					del glb[k][glb[k].index(v)]
				except:
					pass
				dpg.bind_item_theme(sender, 'toogle_OFF')
		else:
			glb[k] = [v]
			dpg.bind_item_theme(sender, 'toogle_ON')

	# handles single-selection toogles
	else:
		glb[k] = v
		prefix = sender.split('--')[0]
		toggle_off_all_items(prefix)
		dpg.bind_item_theme(sender, 'toogle_ON')