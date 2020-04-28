from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.vertex_instructions import Rectangle,Line
from kivy.graphics.context_instructions import Color
from kivy.clock import Clock

Window.size = (500,650)

'''Learn how to remove instruction from canvas'''

class Block:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.size = (40,60)
        self.instruction = None
        
        # get the next colour each time a new block is created
        colour_machine.step()
        self.colour = colour_machine.state

class SM:    
    '''Custom state machine parent class that does not require input'''
    def __init__(self):
        self.state = None
        
    def start(self):
        self.state = self.start_state
        
    def step(self):
        state = self.state
        ns, output = self.get_next_values(state)
        self.state = ns
        return output    
    
class colourSM(SM):
    '''To vary the colour of the blocks'''
    start_state = 'blue'
    
    def get_next_values(self,state):
        if state == 'red':
            ns = 'green'
        elif state == 'green':
            ns = 'blue'
        elif state == 'blue':
            ns = 'red'
        output = ns    # output is redundant for colourSM
        return ns, output
    
colour_machine = colourSM()
colour_machine.start()


class GameWidget(Widget):
    drop, lose = (False,False)
    new_start = True
    base_block = Block(230,0)
    tower = [base_block]
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
        
        with self.canvas:
            Color(1,1,1,1)
            Line(points=[0,568,500,568],width=2)
        
        delay = 0.02
        Clock.schedule_interval(self.draw_tower,0.5)
        Clock.schedule_interval(self.draw_next_block,delay)            
        Clock.schedule_interval(self.drop_next_block,delay)
        
    def draw_tower(self,dt):
        with self.canvas:
            for towerblock in self.tower:
                if towerblock.colour == 'red':
                    Color(1,0,0,1)
                elif towerblock.colour == 'green':
                    Color(0,1,0,1)
                elif towerblock.colour == 'blue':
                    Color(0,0,1,1)
                towerblock.instruction = Rectangle(pos=(towerblock.x,towerblock.y),size=towerblock.size)
                
    def draw_next_block(self,dt):
        if self.new_start == True:
            # create a new Block object
            self.next_block = Block(230,570)
            with self.canvas:
                if self.next_block.colour == 'red':
                    Color(1,0,0,1)
                elif self.next_block.colour == 'green':
                    Color(0,1,0,1)
                elif self.next_block.colour == 'blue':
                    Color(0,0,1,1)
                # draw the new Block object on canvas &
                # call it new_block_canvas
                self.next_block_instruction = Rectangle(pos=(self.next_block.x,self.next_block.y),size=self.next_block.size)
                self.new_start = False
                
        
    def drop_next_block(self,dt):
        current_y = self.next_block_instruction.pos[1]
        top_block = len(self.tower)-1
        top_tower_block_y = self.tower[top_block].y
        # comparing y values
        if self.drop == True and current_y > top_tower_block_y+60:
            current_y -= 10
            # redraw the block on canvas
            self.next_block_canvas.pos = (self.next_block_instruction.pos[0],current_y)
        if current_y == top_tower_block_y+60:
            # stop dropping
            self.drop = False
            # change position of next_block
            self.next_block.x,self.next_block.y = self.next_block_instruction.pos
            self.tower.append(self.next_block)
            self.new_start = True
            
            
    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard = None
        
    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == 'spacebar' and self.lose == False:
            self.drop = True
    
    def next_level(next_block,top_block):
        if next_block.x < top_block.x-40 or next_block.x > topblock.x+40:
            self.lose = True
        if nextBlock.x < topBlock_x-5 and nextBlock.x < topBlock_x+5:
            pass
        if nextBlock.x < topBlock_x-5 or nextBlock.x > topBlock_x+5:
            pass

        
class StartScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        self.layout = FloatLayout(size=(500,650))
        lbl_welcome = Label(text="Welcome to \n Stack 'Em!", font_size=50, 
                            pos_hint={'top': 0.9,'center_x':0.5}, 
                            size_hint = (0.5,0.3))
        self.layout.add_widget(lbl_welcome)
        btn_play = Button(text='Play!', font_size = 30, 
                          pos_hint={'top':0.3,'center_x':0.5}, 
                          size_hint = (0.4,0.15),
                          on_release=self.change_to_play)
        self.layout.add_widget(btn_play)
        self.add_widget(self.layout)
        
    def change_to_play(self,value):
        self.manager.transition.direction='left'
        self.manager.current='play'
        
class PlayScreen(Screen,GameWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout(size=(500,650))
        btn_return = Button(text='Return',font_size=20,
                           pos_hint={'top':1,'x':0},
                           size_hint=(0.2,0.08),
                           on_release=self.change_to_start)
        self.layout.add_widget(btn_return)
        self.add_widget(self.layout)
                
        
    def change_to_start(self,value):
        self.manager.transition.direction='right'
        self.manager.current='start'
        
class StackEmApp(App):
    def build(self):
        sm = ScreenManager()
        start_screen = StartScreen(name='start')
        play_screen = PlayScreen(name='play')
        sm.add_widget(start_screen)
        sm.add_widget(play_screen)
        sm.current = 'play'
        return sm
    
StackEmApp().run()