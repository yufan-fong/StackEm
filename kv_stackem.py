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

class GameWidget(Widget):
    drop = False
    lose = False
    
    def __init__(self,**kwargs):
        Widget.__init__(self,**kwargs)
        
        '''
        listen to keyboard events
        request_keyboard(callback fx when keyboard is closed, 
        widget that requested for the keyboard)
        '''
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
        
        # bind events from keyboard to the function on_keyboard_down()
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
        
        # create custom event for subsequent binding
        self.register_event_type('on_frame')
        
        line_instruction = InstructionGroup()
        line_instruction.add(Color(1,1,1,1))
        line_instruction.add(Line(points=[0,568,500,568],width=2))
        self.canvas.add(line_instruction)
        
        # execute on_frame_dispatcher every frame
        self.bind(on_frame=self.drop_block)
        Clock.schedule_interval(self.on_frame_dispatcher,0)
        Clock.schedule_interval(self.add_block,1)
        
    def add_block(self,dt):
        block = NextBlock()
        self.canvas.add(block.instruction_group)
            
    def on_frame_dispatcher(self,dt):
        # this function dispatches the event 'on_frame'
        # functions binded to 'on_frame' will then be executed
        self.dispatch('on_frame',dt)
        
    def on_frame(self,dt):
        pass                  
        
    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # allow building block to drop
        if keycode[1] == 'spacebar' and self.lose == False:
            print('spacebar pressed')
            self.drop = True
            
    def keyboard_closed(self):
        # I am not sure what is the purpose for this
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard = None
        
    def drop_block(self,other,dt):
        print(self == other)
        print('drop')
        pass

game = GameWidget()
        
class StackEmApp(App):
    def build(self):
        return game
    
StackEmApp().run()