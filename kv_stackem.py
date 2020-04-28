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
from kivy.graphics.instructions import InstructionGroup

Window.size = (500,650)

class Block:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.size = (40,60)
        self.shape = Rectangle(pos=(self.x,self.y),
                               size=self.size)
        # get the next colour each time a new block is created
        colour_machine.step()
        if colour_machine.state == 'red':
            self.colour = Color(1,0,0,1)
        elif colour_machine.state == 'green':
            self.colour = Color(0,1,0,1)
        elif colour_machine.state == 'blue':
            self.colour = Color(0,0,1,1)
            
        self.instruction = InstructionGroup()
        self.instruction.add(self.colour)
        self.instruction.add(self.shape)
        
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

##################### SM ########################


class GameWidget(Widget):
    drop = False
    lose = False
    new_start = False
    base_block = Block(230,0)
    tower = [base_block]
    
    def __init__(self,**kwargs):
        Widget.__init__(self,**kwargs)
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
        
        line_instruction = InstructionGroup()
        line_instruction.add(Color(1,1,1,1))
        line_instruction.add(Line(points=[0,568,500,568],width=2))
        self.canvas.add(line_instruction)
        
        self.next_block = Block(230,570)
        self.canvas.add(self.next_block.instruction)
        
        delay = 0.02
        Clock.schedule_interval(self.draw_tower,delay)
        # Clock.schedule_interval(self.draw_next_block,delay)
        Clock.schedule_interval(self.drop_block,delay)
        
    def draw_tower(self,dt):
        for towerblock in self.tower:
            self.canvas.add(towerblock.instruction)
            
    def draw_next_block(self,dt):
        if self.new_start == True:
            # create a new Block object
            self.next_block = Block(230,570)
            self.canvas.add(self.next_block.instruction)
            self.new_start = False
            
    def drop_block(self,dt):
        current_y = self.next_block.y
        top_towerblock = len(self.tower)-1
        top_towerblock_y = self.tower[top_towerblock].y
        
        if self.drop == True and current_y > top_towerblock_y+60:
            self.canvas.remove(self.next_block.instruction)
            self.next_block.y -= 10
            self.next_block.y.update_position()
            self.canvas.add(self.next_block.instruction)
            
        if current_y == top_towerblock_y+60:
            # stop dropping
            self.drop = False
            # change position of next_block
            self.next_block.x = self.next_block.instruction.x
            self.next_block.y = self.next_block.instruction.y
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