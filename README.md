# Stack 'Em!

**Goal:**  <br>

Build the highest tower by stacking the blocks! <br>

**Instructions:** <br>

The building block can be dropped onto the tower by pressing the SPACE BAR. <br>
The player loses once the block does not land on the tower. <br>
The building block and tower oscillate out of sync and their speed changes depending on the player's aim. <br>

| Landing    | Accuracy                        | Speed |
| :---------:|:-------------------------------:| :----:|
| *Bad..*    | More than 0.5 of block's width  | x1.2  |
| *Good*     | Within 0.1-0.5 of block's width | x1.1  |
| *Great!*   | Below 0.1 of block's width      | x0.9  | <br>

The maximum speed is capped at *2.0*. <br>
The score increases by one for every successful landing. <br>
The score, current speed and landing accuracy are displayed on the right. <br>

![SEsnapshot](https://user-images.githubusercontent.com/58071981/79825129-be720f80-83ca-11ea-9ef1-b70b9c3362ed.jpg) <br>

Players can click on the *Restart* button to restart the game. <br>
Players are able to enter their username and save their highscores. <br>
The top 10 highscores will be displayed the leaderboard on the starting screen. <br>

## Description of Code

### *Block* Class

- Custom class to create *InstructionGroup* for each block that will be used in the game. <br>
- Blocks are objects in this class with attributes like x-y coordinates, size, shape and colour. <br>
- There is a `tower` list in GameWidget, containing all the block objects that make up the tower. <br>

### State Machines

**Colour** <br>

The colour of the blocks are cycled through red, green and blue using an infinite `colourSM` state machine that does not require any input. The state machine steps through the colours as shown below. <br>

**Time Step Diagram for `colourSM`** <br>

| Time       | 0     | 1     | 2     | 3     | 4     | 5     |...  |
|:----------:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|:---:|
| State      |'blue' |'red'  |'green'|'blue' |'red'  |'green'|...  |
| Output     |'red'  |'green'|'blue' |'red'  |'green'|'blue' |...  |
| Next State |'red'  |'green'|'blue' |'red'  |'green'|'blue' |...  | <br>

**Movement of Blocks** <br>
- The blocks undergo oscillation using an infinite `oscillateSM` state machine that does not require any input. <br>
- `oscillateSM` uses cosine function to oscillate the blocks. <br>
- The state is a list with the direction and position as the first and second item respectively. e.g. `['RIGHT',11]` <br>
- The range [-pi/2, pi/2] is divided into 41 positions in the range [-20,20]. <br>
- One `unit` = (pi/2)/20. The table below gives the values for a few positions. <br>

| Position |cos(unit\*pos)|Position |cos(unit\*pos)|
| :-------:|:----:|:-------:|:----:|
| -20      | 0    | 20      | 0    |
| -15      | 0.38 | 15      | 0.38 |
| -10      | 0.71 | 10      | 0.71 |
| -5       | 0.92 | 5       | 0.92 |
| 0        | 1    |         |      | <br>

- Each state machine has a coefficient attribute to determine the step size. <br>
- `move_blockSM` has a coefficient of 6. `move_towerSM` has a coefficient of 2. <br>
- The step is the output of `oscillateSM`, where `step = self.coeff*np.cos(unit*pos)`. <br>

**Time Step Diagram for `move_towerSM`** <br>

| Time       | 0         | ... | 10         | ... | 20         | ... |30         |  ...|
|:----------:|:---------:|:---:|:----------:|:---:|:----------:|:---:|:---------:|:---:|
| State      |['RIGHT',0]|... |['RIGHT',10]|...  |['RIGHT',20]|  ...|['LEFT',10]|  ...|
| Output     |2          |... |1.41        |...  |0           |  ...|-1.41      |  ...|
| Next State |['RIGHT',1]|... |['RIGHT',11]|...  |['LEFT',19] |  ...|['LEFT',9] |  ...|

| Time       |...  |40          |...  |50          |...  |60           |...  |
|:----------:|:---:|:----------:|:---:|:----------:|:---:|:-----------:|:---:|
| State      |...  |['LEFT',0]  |...  |['LEFT',-10]|...  |['LEFT',-20] |...  |
| Output     |...  |-2          |...  |-1.41       |...  |0            |...  |
| Next State |...  |['LEFT',-1] |...  |['LEFT',-11]|...  |['RIGHT',-19]|...  |

### Game Widget

**Class Variables:** <br>

- *drop*: Boolean variable to allow the building block to drawn as dropping. <br>
- *lose*: Boolean variable to restrict SPACE BAR and prevent further dropping. <br>
- *tower*: a list containing all the Block objects making up the tower. <br>
- *next_block*: a Block object for the next building block to be dropped. <br>
- *score*: integer variable to be changed and displayed as the game progresses. <br>
- *speed*: float variable to be changed and displayed as the game progresses. <br>

**Methods:** <br>

- *\_\_init\_\_(self, \*\*kwargs)* <br>
   Keyboard is requested in case the player does not enter his username. <br>
   Creates custom event 'on_land' to dispatch `self.check_landing`. <br>
   Draws the labels for aim, lose, score and speed on the widget's canvas. <br>
   Uses `Clock.schedule_interval` to call `move_tower, move_block, drop_block, check_tower` at the specified interval. <br>
   
- *move_tower(self,dt)* <br>
   Uses the output from `move_towerSM` to change the x coordinate of the blocks in the tower. <br>
   Redraws the blocks in `self.tower` tower based on the new coordinates. <br>
   
- *move_block(self,dt)* <br>
   Uses the output from `move_blockSM` to change the x coordinate of the building block. <br>
   Redraws the block based on the new coordinates. <br>
   
- *check_tower(self,dt)* <br>
   Ensures thats the height of the tower is at most 4 blocks by removing the bottommost block from `self.tower`. <br>
   
- *drop_block(self,dt)* <br>
   Drops the block onto the same height as the top of the tower once the SPACE BAR is pressed. <br>
   Once the block reaches the top of the tower, this function calls `self.check_landing()` <br>
   
- *check_landing(self,value,dt)* <br>
   Checks the position of the dropped block relative to the topmost block of the tower. <br>
   Adjusts the speed and score according to the aim. <br>
   Resets the variables to preapre for next landing. <br>
   This function calls `self.update_labels()` to update the aim and lose label. <br> 
   This function calls `self.update_speed(), self.update_score()` to update the speed and score label. <br>
   This function calls `self.draw_new_block()` to create a new block. <br>
   
- *update_labels(self)* <br>
   Called by self.check_landing. <br>
   Updates the aim and lose label accordingly. <br>
   
- *update_speed(self)* <br>
   Called at the end of self.check_landing. <br>
   Updates the speed label accordingly. <br>
   
- *update_score(self)* <br>
   Called at the end of self.check_landing. <br>
   Updates the score label accordingly. <br>
   
- *draw_new_block(self)* <br>
   Called at the end of self.check_landing. <br>
   Restart `move_blockSM` and redraw next building block. <br>
   
- *restart(self)* <br>
   Remove drawing of the tower and next building block. <br>
   Redraws base block for the tower and next building block. <br>
   Resets the `move_blockSM` and `move_towerSM`. <br>
   Resets score, speed, all labels and class variables. <br>
   
- *on_land(self,dt)* <br>
   Default handler for custom event 'on_land'. <br>
   
- *keyboard_closed(self)* <br>
   Execute when self.keyboard is closed. <br>

- *on_keyboard_down(self, keyboard, keycode, text, modifiers)* <br>
   Listens for SPACE BAR key down to trigger self.drop_block() <br>
   
### Start Screen

**Class Variables:** <br>

- *username*: string variable to store the username input from player. <br>
- *sorted_scores*: list variable to store the scores in descending order. <br>
- *sorted_names*: list variable to store the usersnames based on `sorted_scores`. <br>
- *panel1_text*: string variable to store text for panel1. <br>
- *panel2_text*: string variable to store text for panel2. <br>


**Methods:** <br>
- *\_\_init\_\_(self, \*\*kwargs)* <br>
   Draws the labels for welcome, leaderboard, panels and username on the widget's canvas. <br>
   Creates text input box for username. <br>
   Created buttons to change to the play screen and refresh leaderboard. <br>   
   Calls `self.check_highscore(), self.sort_highscores(), self.display_leaderboard()` to display the leaderboard. <br>
   
- *check_highscores(self)* <br>
   Processes the content inside 'highscores.txt'. <br>
   Returns a dictionary containing the scores and usernames. <br>
   
- *sort_highscores(self, highscores)* <br>
   `highscores` parameter is a dictionary from check_highscores. <br>
   Returns a list `sorted_scores` in descending order and corresponding names in the list `sorted_names`. <br>
   
- *display_leaderboard(self)* <br>
   Prepares 2 strings containing the top 5 and 6th-10th highscore into `self.panel1_text` and `self.panel2_text` respectively. <br>
   Changes the text in panel1 and panel2. <br>
   
- *refresh_leaderboard(self,value)* <br>
   Resets the string variable `self.panel1_text` and `self.panel2_text` to be empty. <br>
   Calls `self.check_highscore(), self.sort_highscores(), self.display_leaderboard()` to display the updates. <br>
   
- *change_to_play(self,value)* <br>
   Changes screen to the play screen. <br>
   
### Play Screen

**Methods:** <br>
- *\_\_init\_\_(self, \*\*kwargs)* <br>
   Creates buttons for return, restart and save. <br>
   Creates text input box for username and button to change to the play screen. <br>
   
- *change_to_start(self,value)* <br>
   Changes screen to the start screen. <br>
   
- *restart_game(self,value)* <br>
   Calls `GameWidget.restart(self)` <br>
   
- *save_game(self,value)* <br>
   Update the score of the player if username already exists. <br>
   Rewrite `highscores.txt` with the updated scores. <br>
