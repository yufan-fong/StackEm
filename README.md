# Stack 'Em!

## Goal: Build the highest tower by stacking the blocks!

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
### State Machines
**Colour**
The colour of the blocks are cycled through red, green and blue using an infinite `colourSM` state machine that does not require any input. The state machine steps through the colours as shown below. <br>

Red --> Green --> Blue --> Red --> Green --> Blue --> ... <br>

**Movement of Blocks**
The blocks undergo oscillation using an infinite `oscillateSM` state machine that does not require any input. <br>
`oscillateSM` uses cosine function to oscillate the blocks. <br>
The state is a list with the direction and position as the first and second item respectively. <br>
The range [-pi/2, pi/2] is divided into 41 positions in the range [-20,20]. <br>
One `unit` = (pi/2)/20. Thus, the table below gives the values for some positions. <br>

| Position |cos(unit\*pos)|Position |cos(unit\*pos)|
| :-------:|:----:|:-------:|:----:|
| -20      | 0    | 20      | 0    |
| -15      | 0.38 | 15      | 0.38 |
| -10      | 0.71 | 10      | 0.71 |
| -5       | 0.92 | 5       | 0.92 |
| 0        | 1    |         |      | <br>

There is a coefficient attribute for each state machine to determine the step size. <br>
`move_blockSM` has a coefficient of 6. `move_towerSM` has a coefficient of 2. <br>
Thus, `step = self.coeff*np.cos(unit*pos)`. The step is the output of `oscillateSM`. <br>

**Time Step Diagram for `move_towerSM`**

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

