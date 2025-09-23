from src.ui import ScrollablePanel
from src.ui import mimlize, CLASSES




# generator funcs
def gen_debug_panel(parent=None):
    clses = CLASSES.copy()
    clses['>miml<'] = ScrollablePanel
    debug_panel_miml = """>miml<(size=[230;350], margin=[5;5], show_border=True, border_color='yellow', name='debug_panel', bg_color='#12121248')
    >vlist<(padding=[5;0])
    >h1<Debug Panel>/h1<
    >txt< # Performance INFO:- >/txt<
    >hlist< >txt<(color='gray') FPS : >/txt< >txt<(name='fps', color='yellow') 0.000 frames >/txt< >/hlist<
    >hlist< >txt<(color='gray') System CPU usage : >/txt< >txt<(name='cpu_usage', color='yellow') 0.000 % >/txt< >/hlist<
    >hlist< >txt<(color='gray') RAM usage : >/txt< >txt<(name='ram_usage', color='yellow') 00000 MB >/txt< >/hlist< 
    >hlist< >txt<(color='gray') System remaining RAM : >/txt< >txt<(name='system_available_ram', color='yellow') 00000 MB >/txt< >/hlist< 
    >hlist< >txt<(color='gray') System Disk usage : >/txt< >txt<(name='system_disk_usage', color='yellow') 00000000 MB >/txt< >/hlist< 
    >txt< ---------------- >/txt<
    >hlist< >txt< # Settings :- >/txt< >/hlist<
    >hlist< >txt<(color='gray') panel opacity : >/txt< >slider<(name='dpanel_opacity', margin=[0;4])>/slider< >/hlist<
    >hlist< >txt<(color='gray') fullscreen : >/txt< >checkbox<(name='fullscreen')>/checkbox< >/hlist<
    >hlist< >txt<(color='gray') scaled : >/txt< >checkbox<(name='scaled')>/checkbox< >/hlist<
    >txt< ---------------- >/txt<
    >txt< # UI info >/txt<
    >hlist< >txt<(color='gray') total ui checks checks: >/txt< >txt<(name='ui_collision_checks', color='yellow') later bro >/txt< >/hlist< 
    >hlist< >txt<(color='gray') show top ui element rects : >/txt< >checkbox<(name='show_top_ui_rects') okay >/checkbox< >/hlist<
    >txt< ---------------- >/txt<
    >txt< # Mouse >/txt<
    >hlist< >txt<(color='gray') absolute position : >/txt< >txt<(name='mouse_abs_pos', color='yellow') 0.000 frames >/txt< >/hlist<
    >hlist< >txt<(color='gray') relative position : >/txt< >txt<(name='mouse_rel_pos', color='brown') maybe later xd >/txt< >/hlist<
    >vlist<(v_gap=2) >txt<(color='gray') mouse ui path : >/txt< >txt<(name='mouse_path', wrap_width=230, color='pink') < ##this filler text will be replaced with other things later uwu alaksjdflkasjdf;lkajsdf;lkasjdfl;kasjdf;lkasjdfl;kasjdf;laksjdf;laskjdflsakdjf;laskjfd;laskdfjas;lkdfja;slkdfjlsa;kdjf >/txt< >/vlist<
    >/vlist<
        >/miml<
        """

    return mimlize(debug_panel_miml, classes=clses, parent=parent)


