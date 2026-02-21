import dearpygui.dearpygui as dpg
import utils

# main UI font
with dpg.font_registry():
	font_path = utils.get_path('./font/SpaceMono-Regular.ttf')
	font = dpg.add_font(font_path, 16)
	font_big = dpg.add_font(font_path, 24)
	font_info_box = dpg.add_font(font_path, 20)
	font_small = dpg.add_font(font_path, 14)
dpg.bind_font(font)

# -------- THEMES -------- #

# reload delegates button
with dpg.theme(tag='transparent_button_theme'):
	with dpg.theme_component(dpg.mvImageButton):
		dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 0, 0))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (100, 100, 100, 50))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 0, 0, 0))

# delegates selectables (buttons)
bg_clr = (255, 230, 0)
bg_clr_hover = (171, 134, 41)
bg_clr_hover_sel = (255, 218, 33)
txt_clr = (0,0,0)
with dpg.theme(tag='toogle_OFF'):
	with dpg.theme_component(dpg.mvAll):
		dpg.add_theme_color(dpg.mvThemeCol_FrameBg, bg_clr)
		dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, bg_clr_hover)
		dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, bg_clr)
with dpg.theme(tag='toogle_ON'):
	with dpg.theme_component(dpg.mvAll):
		dpg.add_theme_color(dpg.mvThemeCol_FrameBg, bg_clr)
		dpg.add_theme_color(dpg.mvThemeCol_Button, bg_clr)
		dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, bg_clr_hover_sel)
		dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, bg_clr)
		dpg.add_theme_color(dpg.mvThemeCol_Text, txt_clr)

# render log
with dpg.theme(tag='render_log_theme'):
	with dpg.theme_component(dpg.mvAll):
		dpg.add_theme_color(dpg.mvThemeCol_Text, (150, 150, 150))

# progress bar
with dpg.theme(tag='progress_bar_theme_active'):
	with dpg.theme_component(dpg.mvAll):
		dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (51, 51, 55))
		dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (105, 189, 32))
with dpg.theme(tag='progress_bar_theme_inactive'):
	with dpg.theme_component(dpg.mvAll):
		dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (51, 51, 55))

# render button
with dpg.theme(tag='render_btn_theme'):
	with dpg.theme_component(dpg.mvAll):
		dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 20)
		dpg.add_theme_color(dpg.mvThemeCol_Button, (33, 105, 145))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (15, 114, 171))
		dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (12, 153, 235))
		
# section headers
with dpg.theme(tag='section_header_theme'):
	with dpg.theme_component(dpg.mvAll):
		dpg.add_theme_color(dpg.mvThemeCol_Header, (92, 98, 105))
