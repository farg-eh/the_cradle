import pygame
from src.ui import VList, HList, Group, Panel
from src.ui.branch.panel import Panel
from src.ui import mimlize, Text
from src.utils import Timer
from src.settings import SW, SH

class NotificationCard(Panel):
    def __init__(self,txt="your map have been\n saved bla bla bla bla bal hehe heheh hehe ", duration=1500,  pos=(0, 0), size=(150, 50), name='NCard') -> None:
        # pre super init calcs
        # msg pos
        pos = pygame.display.get_surface().get_width() - size[0] - 10 , 10
        # text object 
        self.txt = Text(txt,pos=(0, 0), color="gray", font_size="small", lang="en", wrap_width=size[0], align="mid")
        # calc size
        if size[1] < self.txt.rect.size[1]:
            size = size[0], self.txt.rect.size[1]
        # center text on the y axis (its already centered on the x axis cuz of align = mid)
        self.txt.move_to_by_center((self.txt.rect.centerx, size[1]//2))

        super().__init__(pos, size, name=name)
        self.border_color = 'gray'
        self.hover_color = 'yellow'
        self.show_border = True
        self.bg_color = "#12121248"
        self.add_child(self.txt)

        # timers
        self.fade_timer = Timer(duration=1700, func=self.leave_parent)
        self.dur_timer = Timer(duration=duration, autostart=True, func=self.fade_timer.activate)
    
    def leave_parent(self):
        if self.parent:
            self.parent.remove_child(self)
        else:
            print(f"Warning: your trying to delete {self.name} but it doesnt have a parent")

    def update(self, dt, mouse=None):
        super().update(dt, mouse)
        self.dur_timer.update()
        self.fade_timer.update()

        if self.fade_timer:
            self.set_opacity(1-self.fade_timer.get_progress())

# TODO fix the visual bug showing when there is too many notifications and with different sizes 
class NotificationManager(Panel):
    def __init__(self):
        # pre super init calcs
        self.default_msg_size = 150, 50  # the width shouldnt change but the hight might expand based on the msg content
        size = SW/4, SH
        pos = SW - size[0]  , 0
        super().__init__(pos, size, name="notification-panel")
        self.msg_spawn_pos = size[0]//2 - self.default_msg_size[0]//2, 0  # basically in the top middle 
        self.msg_gap = 10

        # timers
        self.top_msg_drop_timer = Timer(duration=400)
        self.move_the_rest_timer = Timer(400, func=self.top_msg_drop_timer.activate)

        # top msg
        self.top_msg = None
        
        # TODO: maybe add a limit to the queue
        # queue when msgs come too fast
        self.msgs_queue = []

    def _process_msg_queue(self):
            # first in first out (its a queue duh)
            fifo_msg = self.msgs_queue[0]
            self.msgs_queue = self.msgs_queue[1:]
            self.notify(msg=fifo_msg[0], dur=fifo_msg[1])

    def notify(self, msg="notification", dur=1500):
        # if moving the rest animation effect is running means we are busy so lets queue
        if self.move_the_rest_timer or self.top_msg_drop_timer:
            self.msgs_queue.append((msg, dur))
            return
        # calcualte total duration
        dur = dur + self.top_msg_drop_timer.duration 
        # create msg
        msg = NotificationCard(txt=msg, duration=dur, size=self.default_msg_size)
        msg.move_to((msg.rect.left, -msg.rect.height))
        if not self.children:
            # activate top msg effect 
            self.top_msg_drop_timer.activate()
        else:
            self.move_the_rest_timer.activate()
            # increase total dur
            dur += self.move_the_rest_timer.duration
        self.top_msg = msg
        self.add_child(self.top_msg)


    def update(self, dt, mouse=None):
        super().update(dt, mouse)
        self.top_msg_drop_timer.update()
        self.move_the_rest_timer.update()

        if self.msgs_queue and not (self.top_msg_drop_timer or self.move_the_rest_timer):
            self._process_msg_queue()

        if self.top_msg_drop_timer.active:
            if self.top_msg:
                t = self.top_msg_drop_timer.get_progress() **3  # for an ease-out effect
                self.top_msg.move_to((self.msg_spawn_pos[0], -self.top_msg.rect.size[1] +  (self.top_msg.rect.size[1]  + self.msg_gap) * t))


        if self.move_the_rest_timer:
            offset = self.msg_gap
            for i, msg in enumerate(reversed(self.children)):
                if msg== self.top_msg: continue
                t = self.move_the_rest_timer.get_progress() ** 2
                dist = self.top_msg.rect.size[1] + self.msg_gap  # height + gap 
                pos = (len(self.children) - i - 1) * dist # original pos
                msg.move_to((self.msg_spawn_pos[0], (offset + dist * t)))
                offset += msg.rect.size[1] + self.msg_gap
            
                

        
