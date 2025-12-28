import pygame
from src.utils import  Rect
from src.ui.branch import Panel

class ImageBox(Panel):
    """
    this class can hold an image and centers it inside itself
    it scales the image to fit its size depending on the chosen fit type
    available options are (contain, cover, stretch)

    """
    # FIXME padding might break the logic a little bit so i have to think about it more (it dosent clip currently )
    def __init__(self,pos=(0, 0), size=(10, 10), img=None, fit_type="contain", prevent_upscaling=False, show_border=False, **kwargs):
        super().__init__(pos=pos, size=size, show_border=show_border, **kwargs)
        self.og_img = img
        self.fit_type = fit_type
        # TODO implement this feature so its possible to not scale up things (only scale down)
        #if self.prevent_upscaling and scale > 1:
        #    scale = 1
        # i just need to insert the above code in the correct place in change_fit_type method and thats it (idk why i didnt just do it)
        self.prevent_upscaling = prevent_upscaling

        # TODO add a padding surf to clip the image when the mode is cover
        self.padding_surf = pygame.Surface(self.padding_rect.size, pygame.SRCALPHA)
        
        self.img = None
        self.change_image(self.og_img)

        self.is_dirty = True
        
    def change_image(self, new_surf, alpha=255):
        self.og_img = new_surf
        self.change_fit_type(self.fit_type)
        self.img.set_alpha(alpha)
        self.is_dirty = True

    def change_fit_type(self, fit_type):
        if fit_type == 'contain':
            self.fit_type = 'contain'
            if self.og_img:
                to_fit_width = self.padding_rect.width/self.og_img.width
                to_fit_height = self.padding_rect.height/self.og_img.height
                scale = min(to_fit_width, to_fit_height)
                self.img = pygame.transform.scale_by(self.og_img, scale) 

        elif fit_type == 'cover':
            self.fit_type = 'cover'
            if self.og_img:
                to_fit_width = self.padding_rect.width/self.og_img.width
                to_fit_height = self.padding_rect.height/self.og_img.height
                scale = max(to_fit_width, to_fit_height)
                self.img = pygame.transform.scale_by(self.og_img, scale) 

        elif fit_type == 'stretch':
            self.fit_type = 'stretch'
            if self.og_img:
                to_fit_width = self.padding_rect.width/self.og_img.width
                to_fit_height = self.padding_rect.height/self.og_img.height
                scalex = to_fit_width
                scaley =  to_fit_height
                self.img = pygame.transform.scale_by(self.og_img, (scalex, scaley)) 

        else:
            raise ValueError(f"the fit mode  '{fit_type}' is not a valid fit_type available fit types are (contain, cover, stretch)")
        self.is_dirty = True

    def draw(self, surf):
        #super().draw(surf)
        if self.is_dirty and self.img:
            # draw self.img in the center on the center of padding rect 
            #self.surf.fill(self.bg_color)
            brs = self.border_radius_list
            # this will fill
            pygame.draw.rect(self.surf, self.bg_color, (0, 0, self.rect.width, self.rect.height),
                                 border_top_left_radius=brs[0], border_top_right_radius=brs[1],
                                 border_bottom_right_radius=brs[2], border_bottom_left_radius=brs[3])
            self.padding_surf.fill((0, 0, 0, 0))
            self.padding_surf.blit(self.img, (self.padding_rect.width/2 - self.img.width/2, self.padding_rect.height/2 -  self.img.height/2))
            self.surf.blit(self.padding_surf, (self._padding[0], self._padding[1]))
        
            self.is_dirty = False
            # print('drew this img')

        surf.blit(self.surf, self.margin_rect)
        

   



