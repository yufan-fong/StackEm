from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label, CoreLabel
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.vertex_instructions import Rectangle,Line
from kivy.graphics.context_instructions import Color
from kivy.clock import Clock
from kivy.graphics.instructions import InstructionGroup
import numpy as np

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
    
    
class oscillateSM(SM):
    '''To vary the speed of the tower as the game progresses'''
    start_state = ['RIGHT',0]
    coeff = 0
    
    def get_next_values(self, state):
        x_norm = np.pi/2/20
        unit = x_norm*state[1]
        if state[0] == 'RIGHT':
            if state[1] < 20:
                output = self.coeff*np.cos(unit)
                ns = ['RIGHT', state[1]+1]
            else:
                # state[1] is 20
                output = 0
                ns = ['LEFT', state[1]-1]
                
        if state [0] == 'LEFT':
            if state[1] > -20:
                output = -self.coeff*np.cos(unit)
                ns = ['LEFT', state[1]-1]
            else:
                # state[1] is -20
                output = 0
                ns = ['RIGHT', state[1]+1]
        return ns, output
    
colour_machine = colourSM()
colour_machine.start()

move_blockSM = oscillateSM()
move_blockSM.start()
move_blockSM.coeff = 6

move_towerSM = oscillateSM()
move_towerSM.start()
move_towerSM.coeff = 2
##################### SM ########################


class GameWidget(Widget):
    drop,lose,new_start,land = (False,False,False,False)
    
    tower = [Block(230,0)]
    next_block = Block(230,520)
    
    score = 0
    speed = 1.0
    
    def __init__(self,**kwargs):
        Widget.__init__(self,**kwargs)
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
        
        # canvas labels        
        self.lose_label = CoreLabel(text='',font_size=40)
        self.lose_label.refresh()
        self.lose_instruction = Rectangle(texture=self.lose_label.texture,
                                          pos=(85,430),size=self.lose_label.texture.size)
        
        self.land_label = CoreLabel(text='',font_size=20)
        self.land_label.refresh()
        self.land_instruction = Rectangle(texture=self.land_label.texture,
                                         pos=(70,300),size=self.land_label.texture.size)
        
        self.score_label = CoreLabel(text='Score: 0',font_size=16)
        self.score_label.refresh()
        self.score_instruction = Rectangle(texture=self.score_label.texture,
                                          pos=(415,530),size=self.score_label.texture.size)
        
        self.speed_label = CoreLabel(text='Speed: 1.0',font_size=16)
        self.speed_label.refresh()
        self.speed_instruction = Rectangle(texture=self.speed_label.texture,
                                         pos=(415,485),size=self.speed_label.texture.size)
        
        self.canvas.add(self.lose_instruction)
        self.canvas.add(self.score_instruction)
        self.canvas.add(self.land_instruction)
        self.canvas.add(self.speed_instruction)
        
        # graphics        
        line_instruction = InstructionGroup()
        line_instruction.add(Color(1,1,1,1))
        line_instruction.add(Line(points=[0,518,500,518],width=2))
        self.canvas.add(line_instruction)
        self.canvas.add(self.next_block.instruction)
        
        # functions
        Clock.schedule_interval(self.move_tower,0.02)
        Clock.schedule_interval(self.move_block, 0.04)
        Clock.schedule_interval(self.drop_block,0)
        Clock.schedule_interval(self.check_tower,0)
        
    def move_tower(self,dt):
        step = move_towerSM.step()
        for towerblock in self.tower:
            self.canvas.remove(towerblock.instruction)
            towerblock.x += step
            towerblock.shape.pos = (towerblock.x,towerblock.y)
            towerblock.instruction.add(towerblock.shape)
            self.canvas.add(towerblock.instruction)
    
    def move_block(self,dt):
        if self.drop == False:
            self.canvas.remove(self.next_block.instruction)
            self.next_block.x += move_blockSM.step()*0.7
            self.next_block.shape.pos = (self.next_block.x,self.next_block.y)
            self.next_block.instruction.add(self.next_block.shape)
            self.canvas.add(self.next_block.instruction)
            
    def check_tower(self,dt):
        if len(self.tower) == 5:
            # clear the bottomest towerblock
            self.canvas.remove(self.tower[0].instruction)
            self.tower.pop(0)
            for towerblock in self.tower:                
                towerblock.y -= towerblock.size[1]
            
    def drop_block(self,dt):
        if self.drop == False or self.lose == True:
            return
        
        current_y = self.next_block.y
        top_towerblock = len(self.tower)-1
        top_towerblock_y = self.tower[top_towerblock].y
        
        if current_y > top_towerblock_y+60:
            self.canvas.remove(self.next_block.instruction)
            self.next_block.y -= 5
            self.next_block.shape.pos = (self.next_block.x,self.next_block.y)
            self.next_block.instruction.add(self.next_block.shape)
            self.canvas.add(self.next_block.instruction)
            
        if current_y == top_towerblock_y+60:
            # stop dropping
            self.drop = False
            self.land = True
            self.check_landing()
    
    def check_landing(self):
        top_block = len(self.tower)-1
        top_x = self.tower[top_block].x
        top_y = self.tower[top_block].y
        width = self.tower[top_block].size[0]
        height = self.tower[top_block].size[1]
        print('land')
        
        # failed landing
        if self.next_block.x<top_x-width or self.next_block.x>top_x+width:
            self.lose = True
            self.update_label('lose')
            print('lose')
        
        # successful landing
        else:
            self.score += 1
            # bad landing        
            if self.next_block.x<top_x-0.5*width or self.next_block.x>top_x+0.5*width:
                if move_towerSM.coeff<=14:
                    move_towerSM.coeff *= 1.2
                    move_blockSM.coeff *= 1.2
                    self.speed += 0.2
                    self.update_label('Bad..')
                    print('bad')
                    
            # good landing        
            elif self.next_block.x<top_x-0.1*width or self.next_block.x>top_x+0.1*width:
                if move_towerSM.coeff<=14:
                    move_towerSM.coeff *= 1.1
                    move_blockSM.coeff *= 1.1
                    self.speed += 0.1
                    self.update_label('Good')
                    print('good')
                    
            # great landing
            else:
                self.update_label('Great!')
                print('great')
                if move_towerSM.coeff>2:
                    self.speed -= 0.1
                    move_towerSM.coeff *= 0.9
                    move_blockSM.coeff *= 0.9
                
        # append next_block to tower
        self.tower.append(self.next_block)
        
        # reset for next landing
        self.land = False
        self.update_speed()
        self.update_score()
        self.draw_new_block()
        
    def update_label(self,result):
        if result == 'lose':
            self.lose_label.text = "OH NO! YOU LOST!"
            self.lose_label.refresh()
            self.lose_instruction.texture = self.lose_label.texture
            self.lose_instruction.size = self.lose_label.texture.size
            self.land_label.text = ''             
        elif result == 'restart':
            self.lose_label.text = ''
            self.lose_label.refresh()
            self.lose_instruction.texture = self.lose_label.texture
            self.lose_instruction.size = self.lose_label.texture.size
            self.land_label.text = ''
        else:
            self.land_label.text = result
        self.land_label.refresh()
        self.land_instruction.texture = self.land_label.texture
        self.land_instruction.size = self.land_label.texture.size
            
    def draw_new_block(self):
        # create a new Block object
        move_blockSM.start()
        self.next_block = Block(230,520)
        self.canvas.add(self.next_block.instruction)
        
    def update_speed(self):
        self.speed_label.text = "Speed: " + str(round(self.speed,1))
        self.speed_label.refresh()
        self.speed_instruction.texture = self.speed_label.texture
        self.speed_instruction.size = self.speed_label.texture.size
            
    def update_score(self):
        self.score_label.text = "Score: " + str(self.score)
        self.score_label.refresh()
        self.score_instruction.texture = self.score_label.texture
        self.score_instruction.size = self.score_label.texture.size
            
    def restart(self):
        # reset blocks
        for towerblock in self.tower:
            self.canvas.remove(towerblock.instruction)
        self.tower = [Block(230,0)]
        self.canvas.remove(self.next_block.instruction)
        self.next_block = Block(230,520)
        move_blockSM.start()
        move_towerSM.start()
        move_blockSM.coeff = 6
        move_towerSM.coeff = 2
        
        # reset labels
        self.score = 0
        self.speed = 1.0
        self.update_score()
        self.update_speed()
        self.drop,self.lose,self.new_start,self.land = (False,False,False,False)
        self.update_label('restart')
        
        # add new highscore entry
        if StartScreen.username not in namelist:
            print(StartScreen.username)
        
    def keyboard_closed(self):
        self.keyboard.unbind(on_key_down=self.on_keyboard_down)
        self.keyboard = None
    
    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if self.manager.current == 'play':
            if keycode[1] == 'spacebar' and self.lose == False:
                self.drop = True

        
class StartScreen(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        highscores = self.check_highscores()
        sorted_names,sorted_scores = self.sort_highscores(highscores)
        panel_1 = ''
        panel_2 = ''
        for i in range(0,11):
            try:
                if sorted_scores[i]<10:
                    score=str(sorted_scores[i])+'  '
                else:
                    score=str(sorted_scores[i])
                if i<5:
                    panel_1+=score+'  '+sorted_names[i]+'\n'
                else:
                    panel_2+=score+'  '+sorted_names[i]+'\n'
            except:
                pass
            
        self.layout = FloatLayout(size=(500,650))
        
        lbl_welcome = Label(text="Welcome to \n Stack 'Em!", font_size=50, 
                            pos_hint={'top': 0.95,'center_x':0.5}, 
                            size_hint = (0.5,0.3))
        self.layout.add_widget(lbl_welcome)
        
        lbl_highscores = Label(text="Highscores",font_size=25, 
                            pos_hint={'center_x':0.5,'y':0.42}, 
                            size_hint=(0.3,0.3))
        self.layout.add_widget(lbl_highscores)
        
        lbl_panel_1 = Label(text=panel_1,font_size=15, 
                            pos_hint={'right': 0.5,'y':0.3}, 
                            size_hint=(0.3,0.3))
        self.layout.add_widget(lbl_panel_1)
        
        lbl_panel_2 = Label(text=panel_2,font_size=15, 
                            pos_hint={'x': 0.5,'y':0.3}, 
                            size_hint=(0.3,0.3))
        self.layout.add_widget(lbl_panel_2)
        
        btn_play = Button(text='Play!', font_size = 30, 
                          pos_hint={'top':0.2,'center_x':0.5}, 
                          size_hint = (0.4,0.15),
                          on_release=self.change_to_play)
        self.layout.add_widget(btn_play)
        
        lbl_username = Label(text="Username: ",font_size=25,
                            pos_hint={'right':0.5,'y':0.25},
                            size_hint=(0.3,0.05))
        self.layout.add_widget(lbl_username)
        
        self.ti_username = TextInput(text='',multiline=False,
                                pos_hint={'x':0.5,'y':0.25},
                                size_hint=(0.3,0.05))
        self.layout.add_widget(self.ti_username)
        self.add_widget(self.layout)
        
    def check_highscores(self):
        highscores = {}
        f = open("highscores.txt",'r')
        line = f.readline()
        while line:
            details = line.split(',')
            name = details[0]
            score = int(details[1].rstrip())
            highscores[name] = score
            line = f.readline()
        f.close()
        return highscores
    
    def sort_highscores(self,highscores):
        sorted_scores = []
        sorted_names = []
        namelist = list(highscores.keys())
        unsorted_scores = list(highscores.values())
        sorted_scores = unsorted_scores[:]
        sorted_scores.sort()
        sorted_scores.reverse()
                
        for score in sorted_scores:
            for i,name in enumerate(namelist):
                if score == unsorted_scores[i]:
                    if name not in sorted_names:
                        sorted_names.append(name)
        return sorted_names,sorted_scores
    
    def change_to_play(self,value):
        #self.manager.transition.direction='left'
        #self.manager.current='play'
        #self.username = self.ti_username.text
        print(self)
        print(self.username)
        
class PlayScreen(Screen,GameWidget):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout(size=(500,600))
        btn_return = Button(text='Return',font_size=20,
                           pos_hint={'top':1,'x':0},
                           size_hint=(0.2,0.08),
                           on_release=self.change_to_start)
        btn_restart = Button(text='Restart',font_size=20,
                           pos_hint={'top':1,'x':0.8},
                           size_hint=(0.2,0.08),
                           on_release=self.restart_game)
        self.layout.add_widget(btn_return)
        self.layout.add_widget(btn_restart)
        self.add_widget(self.layout)
                
    def change_to_start(self,value):
        self.manager.transition.direction='right'
        self.manager.current='start'
        
    def restart_game(self,value):
        GameWidget.restart(self)
        
class StackEmApp(App):
    def build(self):
        sm = ScreenManager()
        start_screen = StartScreen(name='start')
        play_screen = PlayScreen(name='play')
        sm.add_widget(start_screen)
        sm.add_widget(play_screen)
        sm.current = 'start'
        return sm
    
username = ''
namelist = []
    
Window.size = (500,600)    
StackEmApp().run()