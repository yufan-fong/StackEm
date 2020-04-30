from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.label import Label, CoreLabel
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics.vertex_instructions import Rectangle,Line
from kivy.graphics.context_instructions import Color
from kivy.clock import Clock
from kivy.graphics.instructions import InstructionGroup
import numpy as np


class Block:
    '''
    Custom class to create InstructionGroup for 
    each block that will be used in the game.
    '''
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
        
        # create canvas instruction
        self.instruction = InstructionGroup()
        self.instruction.add(self.colour)
        self.instruction.add(self.shape)

        
# State Machines
class SM:    
    '''
    Custom state machine parent class
    that does not require inputs.
    '''
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
    '''
    To vary the colour of the blocks.
    '''
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
    '''
    To vary the speed of the blocks as the game progresses.
    '''
    start_state = ['RIGHT',0]
    coeff = 0
    
    def get_next_values(self, state):
        unit = np.pi/2/20
        direction = state[0]
        pos = state[1]
        step = self.coeff*np.cos(unit*pos)
        if direction == 'RIGHT':
            output = step
            if pos < 20:
                ns = ['RIGHT', state[1]+1]
            else:    # position is 20
                ns = ['LEFT', state[1]-1]
                
        elif direction == 'LEFT':
            output = -step
            if pos > -20:
                ns = ['LEFT', state[1]-1]
            else:     # position is -20
                ns = ['RIGHT', state[1]+1]
        return ns, output

# start the state machines
colour_machine = colourSM()
colour_machine.start()

move_blockSM = oscillateSM()
move_blockSM.start()
move_blockSM.coeff = 4

move_towerSM = oscillateSM()
move_towerSM.start()
move_towerSM.coeff = 2


class GameWidget(Widget):
    drop,lose,started = (False,False,False)
    tower = [Block(230,0)]
    next_block = Block(230,520)
    
    score = 0
    speed = 1.0
    vibrate = 1
    
    def __init__(self,**kwargs):
        Widget.__init__(self,**kwargs)
        # create keyboard
        self.keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self.keyboard.bind(on_key_down=self.on_keyboard_down)
        
        # custom events
        self.register_event_type('on_land')
        self.bind(on_land=self.check_landing)
        self.register_event_type('on_lose')
        
        # canvas core labels        
        self.lose_label = CoreLabel(text='',font_size=40)
        self.lose_label.refresh()
        self.lose_instruction = Rectangle(texture=self.lose_label.texture,
                                          pos=(85,430),size=self.lose_label.texture.size)
        
        self.aim_label = CoreLabel(text='',font_size=20)
        self.aim_label.refresh()
        self.aim_instruction = Rectangle(texture=self.aim_label.texture,
                                         pos=(415,300),size=self.aim_label.texture.size)
        
        self.score_label = CoreLabel(text='Score: 0',font_size=20)
        self.score_label.refresh()
        self.score_instruction = Rectangle(texture=self.score_label.texture,
                                          pos=(390,530),size=self.score_label.texture.size)
        
        self.speed_label = CoreLabel(text='Speed: 1.0',font_size=20)
        self.speed_label.refresh()
        self.speed_instruction = Rectangle(texture=self.speed_label.texture,
                                         pos=(390,485),size=self.speed_label.texture.size)
        
        self.canvas.add(self.lose_instruction)
        self.canvas.add(self.score_instruction)
        self.canvas.add(self.aim_instruction)
        self.canvas.add(self.speed_instruction)
        
        # graphics        
        line_instruction = InstructionGroup()
        line_instruction.add(Color(1,1,1,1))
        line_instruction.add(Line(points=[0,518,500,518],width=2))
        self.canvas.add(line_instruction)
        self.canvas.add(self.next_block.instruction)
        
        # run these functions continuously
        self.move_tower_event = Clock.schedule_interval(self.move_tower,0.02)
        Clock.schedule_interval(self.move_block, 0.04)
        Clock.schedule_interval(self.drop_block,0)
        Clock.schedule_interval(self.check_tower,0)
        
    def move_tower(self,dt):
        '''
        Oscillates the towers based on 
        the step size from move_towerSM.
        '''
        step_size = move_towerSM.step()
        for towerblock in self.tower:
            self.canvas.remove(towerblock.instruction)
            if self.started == True:
                towerblock.y -= 0.1
            towerblock.x += step_size
            towerblock.shape.pos = (towerblock.x,towerblock.y)
            towerblock.instruction.add(towerblock.shape)
            self.canvas.add(towerblock.instruction)
    
    def move_block(self,dt):
        '''
        Oscillates the building block based on 
        the step size from move_blockSM.
        '''
        if self.drop == False:
            step_size = move_blockSM.step()
            self.canvas.remove(self.next_block.instruction)
            self.next_block.x += step_size
            self.next_block.shape.pos = (self.next_block.x,self.next_block.y)
            self.next_block.instruction.add(self.next_block.shape)
            self.canvas.add(self.next_block.instruction)
            
    def check_tower(self,dt):
        '''
        Removes the bottommost block if 
        tower is more than 4 blocks tall.
        '''
        for i,towerblock in enumerate(self.tower):
            if towerblock.y <-60:
                        self.canvas.remove(self.tower[0].instruction)
                        self.tower.pop(i)
                    
        if len(self.tower) == 6:
            self.canvas.remove(self.tower[0].instruction)
            self.tower.pop(0)
            
            # shift remaining blocks down
            for towerblock in self.tower:
                towerblock.y -= towerblock.size[1]
                
            
    def drop_block(self,dt):
        '''
        Drops the building block was the SPACEBAR is pressed.
        '''
        if self.drop == False:
            return
        
        current_y = self.next_block.y
        top_towerblock = len(self.tower)-1
        top_towerblock_y = self.tower[top_towerblock].y
        height = self.tower[top_towerblock].size[1]
        
        if current_y > top_towerblock_y+height:
            # change y coordinate and redraw
            self.canvas.remove(self.next_block.instruction)
            self.next_block.y -= 450*dt
            self.next_block.shape.pos = (self.next_block.x,self.next_block.y)
            self.next_block.instruction.add(self.next_block.shape)
            self.canvas.add(self.next_block.instruction)
            
        if current_y <= top_towerblock_y+height:
            # stop dropping
            self.next_block.y = top_towerblock_y+height
            self.drop = False
            
            self.dispatch('on_land',dt)
    
    def check_landing(self,value,dt):
        '''
        Checks the accuracy of the landing. 
        Update score, speed and labels accordingly.
        '''
        top_block = len(self.tower)-1
        top_x = self.tower[top_block].x
        top_y = self.tower[top_block].y
        width = self.tower[top_block].size[0]
        height = self.tower[top_block].size[1]
                
        # failed landing
        if self.next_block.x<top_x-width or self.next_block.x>top_x+width:
            self.lose = True
            self.update_labels('lose')
            self.dispatch('on_lose',1)
        
        # successful landing
        else:
            self.score += 1
            
            # bad landing        
            if self.next_block.x<top_x-0.5*width or self.next_block.x>top_x+0.5*width:
                self.update_labels('Bad..')
                if move_towerSM.coeff<=14:
                    move_towerSM.coeff *= 1.1
                    move_blockSM.coeff *= 1.1
                    self.speed += 0.1            
                    
            # good landing        
            elif self.next_block.x<top_x-0.1*width or self.next_block.x>top_x+0.1*width:
                self.update_labels('Good')
                if move_towerSM.coeff<=14:
                    move_towerSM.coeff *= 1.05
                    move_blockSM.coeff *= 1.05
                    self.speed += 0.05
                    
            # great landing
            else:
                self.update_labels('Great!')
                if move_towerSM.coeff>2:
                    self.speed -= 0.1
                    move_towerSM.coeff *= 0.9
                    move_blockSM.coeff *= 0.9
                
        # append next_block to self.tower
        self.tower.append(self.next_block)
        
        # update labels, draw new building block
        self.update_speed()
        self.update_score()
        self.draw_new_block()
        
    def update_labels(self,result):
        '''
        Updates aim and lose label.
        '''
        if result == 'lose':
            self.aim_label.text = ''
            
            self.lose_label.text = "OH NO! YOU LOST!"
            self.lose_label.refresh()
            self.lose_instruction.texture = self.lose_label.texture
            self.lose_instruction.size = self.lose_label.texture.size
            
        elif result == 'restart':
            self.aim_label.text = ''
            
            self.lose_label.text = ''
            self.lose_label.refresh()
            self.lose_instruction.texture = self.lose_label.texture
            self.lose_instruction.size = self.lose_label.texture.size
            
        else:
            self.aim_label.text = result
        self.aim_label.refresh()
        self.aim_instruction.texture = self.aim_label.texture
        self.aim_instruction.size = self.aim_label.texture.size
        
    def update_speed(self):
        '''
        Updates speed label.
        '''
        self.speed_label.text = "Speed: " + str(round(self.speed,2))
        self.speed_label.refresh()
        self.speed_instruction.texture = self.speed_label.texture
        self.speed_instruction.size = self.speed_label.texture.size
            
    def update_score(self):
        '''
        Updates score label.
        '''
        self.score_label.text = "Score: " + str(self.score)
        self.score_label.refresh()
        self.score_instruction.texture = self.score_label.texture
        self.score_instruction.size = self.score_label.texture.size
        
    def draw_new_block(self):
        '''
        Creates a new Block object at the starting position.
        '''
        move_blockSM.start()
        self.next_block = Block(230,520)
        self.canvas.add(self.next_block.instruction)
        
    def restart(self):
        '''
        Reset tower and building blocks, SM, class variables and labels.
        Unschedules vibrate and collapse event if any.
        Reschedules move_tower_event if player lost.
        '''
        if self.started == False:
            return True
        
        try:
            Clock.unschedule(self.vibrate_event)
            self.unvibrate.cancel()
        except:
            pass
        try:
            Clock.unschedule(self.collapse_event)
        except:
            pass
        
        for towerblock in self.tower:
            self.canvas.remove(towerblock.instruction)
        self.tower = [Block(230,0)]
        self.canvas.remove(self.next_block.instruction)
        self.next_block = Block(230,520)
        move_blockSM.start()
        move_towerSM.start()
        move_blockSM.coeff = 4
        move_towerSM.coeff = 2
        
        if self.lose == True:
            # schedule move_tower_event again only after player loses
            self.move_tower_event = Clock.schedule_interval(self.move_tower,0.02)
        
        # reset labels
        self.score = 0
        self.speed = 1.0
        self.update_score()
        self.update_speed()
        self.update_labels('restart')
        self.drop,self.lose,self.started = (False,False,False)
        
        
    def on_land(self,dt):
        '''
        Default handler for the custom event 'on_land'.
        '''
        self.started = True
    
    def on_lose(self,dt):
        '''
        Schedules and unschedules the vibrate event.
        '''
        Clock.unschedule(self.move_tower_event)
        self.vibrate_event = Clock.schedule_interval(self.vibrate_tower,0.06)
        self.unvibrate = Clock.schedule_once(self.unschedule_vibrate,0.8)
    
    def vibrate_tower(self,dt):
        '''
        Canvas instructions to animate vibrating.
        '''
        for i,towerblock in enumerate(self.tower):
            self.canvas.remove(towerblock.instruction)
            if i%2 == 0:
                towerblock.x += self.vibrate*4
            else:
                towerblock.x -= self.vibrate*4
            towerblock.shape.pos = (towerblock.x,towerblock.y)
            towerblock.instruction.add(towerblock.shape)
            self.canvas.add(towerblock.instruction)
            
        self.vibrate *= -1            
        
    def collapse_tower(self,dt):
        '''
        Canvas instructions to animate collapsing.
        '''
        for i,towerblock in enumerate(self.tower):
            self.canvas.remove(towerblock.instruction)
            if i%2 == 0:
                towerblock.x -= 1
            else:
                towerblock.x += 1
            towerblock.y -= 4
            towerblock.shape.pos = (towerblock.x,towerblock.y)
            towerblock.instruction.add(towerblock.shape)
            self.canvas.add(towerblock.instruction)
        
    def unschedule_vibrate(self,dt):
        '''
        Unschedules vibrate event, schedules collapse event.
        '''
        Clock.unschedule(self.vibrate_event)
        self.collapse_event = Clock.schedule_interval(self.collapse_tower,0)
        Clock.schedule_once(self.unschedule_collapse,1.5)
        
    def unschedule_collapse(self,dt):
        '''
        Unschedules collapse event.
        '''
        Clock.unschedule(self.collapse_event)
    
    def keyboard_closed(self):
        pass
    
    def on_keyboard_down(self, keyboard, keycode, text, modifiers):
        '''
        Listens for SPACE BAR key down to trigger self.drop_block().
        '''
        if self.manager.current == 'play':
            if keycode[1] == 'spacebar' and self.lose == False:
                self.drop = True

        
class StartScreen(Screen):
    username = ''
    
    sorted_names = []
    sorted_scores = []
    
    panel1_text = ''
    panel2_text = ''
    
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)

        self.layout = FloatLayout(size=(500,650))
        
        # welcone label
        lbl_welcome = Label(text="Welcome to \n Stack 'Em!", font_size=50, 
                            pos_hint={'top': 0.95,'center_x':0.5}, 
                            size_hint = (0.5,0.3))
        self.layout.add_widget(lbl_welcome)
        
        # leaderboard label
        lbl_leaderboard = Label(text="Leaderboard",font_size=25, 
                            pos_hint={'center_x':0.5,'y':0.42}, 
                            size_hint=(0.3,0.3))
        self.layout.add_widget(lbl_leaderboard)
        
        # panel 1 label
        self.lbl_panel1 = Label(text=self.panel1_text,font_size=15, 
                            pos_hint={'right': 0.5,'y':0.28}, 
                            size_hint=(0.3,0.3))
        self.layout.add_widget(self.lbl_panel1)
        
        # panel 2 label
        self.lbl_panel2 = Label(text=self.panel2_text,font_size=15, 
                            pos_hint={'x': 0.5,'y':0.28}, 
                            size_hint=(0.3,0.3))
        self.layout.add_widget(self.lbl_panel2)
        
        # username label
        lbl_username = Label(text="Username: ",font_size=25,
                            pos_hint={'right':0.5,'y':0.25},
                            size_hint=(0.3,0.05))
        self.layout.add_widget(lbl_username)
        
        # username text input       
        self.ti_username = TextInput(text='',multiline=False,
                                pos_hint={'x':0.5,'y':0.25},
                                size_hint=(0.3,0.05))
        self.layout.add_widget(self.ti_username)
        
        # play button
        btn_play = Button(text='Play!', font_size = 30, 
                          pos_hint={'top':0.2,'center_x':0.5}, 
                          size_hint = (0.4,0.15),
                          on_release=self.change_to_play)
        self.layout.add_widget(btn_play)
        
        # refresh button
        btn_refresh = Button(text='Refresh',font_size=12,
                            pos_hint={'center_x':0.7,'y':0.55},
                            size_hint=(0.1,0.04),
                            on_release=self.refresh_leaderboard)
        self.layout.add_widget(btn_refresh)
        
        self.add_widget(self.layout)
        
        # prepare data and string text for leaderboard/panels
        highscores = self.check_highscores()
        sorted_names,sorted_scores = self.sort_highscores(highscores)
        self.display_leaderboard(sorted_names,sorted_scores)
        
        
    def check_highscores(self):
        '''
        Reads the file highscores.txt and 
        returns a dictionary containing all the names and scores.
        '''
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
        '''
        Returns a list of sorted_scores in descending order 
        and the corresponding names in sorted_names.
        '''
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
                        
        StartScreen.sorted_names = sorted_names
        StartScreen.sorted_scores = sorted_scores
        return sorted_names,sorted_scores
    
    def display_leaderboard(self,sorted_names,sorted_scores):
        '''
        Prepares the text to be displayed on the leaderboard.
        Changes text in the panels.
        '''
        for i in range(0,11):
            try:
                if sorted_scores[i]<10:
                    score=str(sorted_scores[i])+'  '
                else:
                    score=str(sorted_scores[i])
                if i<5:
                    self.panel1_text+=score+'  '+sorted_names[i]+'\n'
                else:
                    self.panel2_text+=score+'  '+sorted_names[i]+'\n'
            except:
                pass
        # change text in lbl_panel 1 & 2
        self.lbl_panel1.text = self.panel1_text
        self.lbl_panel2.text = self.panel2_text
        
    def refresh_leaderboard(self,value):
        '''
        Update the highscores and display leaderboard.
        '''
        self.panel1_text = ''
        self.panel2_text = ''
        highscores = self.check_highscores()
        sorted_names,sort_scores = self.sort_highscores(highscores)
        self.display_leaderboard(sorted_names,sort_scores)
    
    def change_to_play(self,value):
        '''
        Changes screen to play screen.
        '''
        self.manager.transition.direction='left'
        self.manager.current='play'
        StartScreen.username = self.ti_username.text
        
class PlayScreen(Screen,GameWidget):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout(size=(500,600))
        btn_return = Button(text='Return',font_size=15,
                           pos_hint={'top':0.8,'x':0},
                           size_hint=(0.15,0.05),
                           on_release=self.change_to_start)
        self.layout.add_widget(btn_return)
        
        btn_restart = Button(text='Restart',font_size=15,
                           pos_hint={'top':0.72,'x':0},
                           size_hint=(0.15,0.05),
                           on_release=self.restart_game)
        self.layout.add_widget(btn_restart)
        
        btn_save = Button(text='Save',font_size=15,
                           pos_hint={'top':0.64,'x':0},
                           size_hint=(0.15,0.05),
                           on_release=self.save_game)        
        self.layout.add_widget(btn_save)
        
        self.add_widget(self.layout)
                
    def change_to_start(self,value):
        '''
        Changes screen to start screen.
        '''
        self.manager.transition.direction='right'
        self.manager.current='start'
        
    def restart_game(self,value):
        '''
        Restarts the game upon pressing the restart button.
        '''
        GameWidget.restart(self)
        
    def save_game(self,value):
        '''
        Saves the player's username and 
        score into the file highscores.txt.
        '''       
        if StartScreen.username == '':
            # player did not enter username
            return
        
        if StartScreen.username not in StartScreen.sorted_names:
            # add new entry if username does not exist
            StartScreen.sorted_names.append(StartScreen.username)
            StartScreen.sorted_scores.append(self.score)
            f = open('highscores.txt','a')
            f.write('{},{}\n'.format(StartScreen.username,self.score))
        else:
            # update the username's if it is a new highscore
            new_text = ''
            f = open('highscores.txt','w')
            for pos,name in enumerate(StartScreen.sorted_names):
                if name == StartScreen.username:
                    previous_score = int(StartScreen.sorted_scores[pos])
                    if previous_score < self.score:
                        StartScreen.sorted_scores[pos] = str(self.score)
            for i in range(len(StartScreen.sorted_names)):
                new_text += StartScreen.sorted_names[i]+','+str(StartScreen.sorted_scores[i])+'\n'
            f.write(new_text)
        f.close()
        
# Run the game        
class StackEmApp(App):
    def build(self):
        sm = ScreenManager()
        start_screen = StartScreen(name='start')
        play_screen = PlayScreen(name='play')
        sm.add_widget(start_screen)
        sm.add_widget(play_screen)
        sm.current = 'start'
        return sm
    
Window.size = (500,600)    
StackEmApp().run()