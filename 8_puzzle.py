import random
import math
import readchar
import os
import time
import platform
vals = [1, 2, 3, 4, 5, 6, 7, 8, 0]
random.shuffle(vals)
dimension = int(math.sqrt(len(vals)))
board = []
# if you want to set a board you can do it here commented out for now
#vals = [8, 1, 2, 5, 4, 6, 0, 7, 3]
for i in range(0, len(vals), dimension):
    board.append(vals[i:i+dimension])
    #print(*vals[i:i+dimension])

def clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def show_board(board):
    for row in board:
        print(*row)

def flash_board(board, seconds):
    clear_screen()
    print(f"Memorize this board in {seconds}s:")
    show_board(board)
    time.sleep(seconds)
    clear_screen()

# example
flash_board(board, 5)
def left_command(vals, dimension):
    open_index = vals.index(0)
    if (open_index+1)%dimension == 0:
        return vals
    else:
        vals[open_index] = vals[open_index + 1]
        vals[open_index + 1] = 0
    return (vals)
def up_command(vals, dimension):
    open_index = vals.index(0)
    if (open_index + 1) > len(vals) - dimension:
        return vals
    else:
        vals[open_index] = vals[open_index + dimension]
        vals[open_index + dimension] = 0
    return (vals)
def right_command(vals, dimension):
    open_index = vals.index(0)
    if (open_index + 1) % dimension == 1:
        return (vals)
    else:
        vals[open_index] = vals[open_index - 1]
        vals[open_index - 1] = 0
    return (vals)
def down_command(vals, dimension):
    open_index = vals.index(0)
    if (open_index + 1) <= dimension:
        return vals
    else:
        vals[open_index] = vals[open_index - dimension]
        vals[open_index - dimension] = 0
    return (vals)
moves = ""

print("Use arrow keys. Press Enter when done.")

while True:
    key = readchar.readkey()

    if key == readchar.key.ENTER:
        break
    elif key == readchar.key.LEFT:
        moves += "l"
        print("l", end="", flush=True)
    elif key == readchar.key.RIGHT:
        moves += "r"
        print("r", end="", flush=True)
    elif key == readchar.key.UP:
        moves += "u"
        print("u", end="", flush=True)
    elif key == readchar.key.DOWN:
        moves += "d"
        print("d", end="", flush=True)

print()
print("moves:", moves)
commands = moves
# if you want to test a command string do it here - mostly for debugging when i thought my code may be wrong
#commands = "dllurrdlrdllururdllurdruldlurrdllurrdllu"

for i in range (len(commands)):
    if commands[i] == "l":
        vals = left_command(vals, dimension)
    if commands[i] == "u":
        vals = up_command(vals, dimension)
    if commands[i] == "r":
        vals = right_command(vals, dimension)
    if commands[i] == "d":
        vals = down_command(vals, dimension)

    #print(f"Move {i+1}: {commands[i]} gives vals: {vals}")
for i in range(0, len(vals), dimension):
    #board.append(vals[i:i+dimension])
    print(*vals[i:i+dimension])
if vals == [1,2,3,4,5,6,7,8,0]:
    print("CORRECT - YOU WIN")
else:
    print("INCORRECT")