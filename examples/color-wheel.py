'''
Delayed estimation experiment:

Presents sequence of colored circles (varying in hue) in different locations.
Colors are recalled on color wheel in order of presentation.
'''

from psychopy import visual, core, event, monitors
#import pandas as pd
import numpy as np
import random, os
from psychopy.tools.colorspacetools import hsv2rgb # useful function for converting color space
from datetime import datetime
from extras import LAB2RGB # load function from extras.py

try:
    import win32api # if we're on a windows machine we can use this module to move the mouse
except:
    pass

### SETTINGS
WINSIZE = [1000, 1000]
WIDTH = 30
DIST = 60
BACKGROUND=[0,0,0]#[-1,-1,-1]
FOREGROUND=[-1,-1,-1]#[1,1,1]
QUIT='f8'

WHEELRADIUS = 7
WHEELWIDTH = 1
NONCUECOL = [.25,.25,.25]
CUECOL = [-.25,-.25,-.25]

### CREATE PSYCHOPY OBJECTS
mon = monitors.Monitor("monitor1", width=WIDTH, distance=DIST)
mon.setSizePix(WINSIZE)
mon.save()

win = visual.Window(WINSIZE, units = 'deg', allowGUI=False, fullScr=False, color=BACKGROUND, monitor=mon)
instr = visual.TextStim(win, color=FOREGROUND, pos=[0, 0], height=.8, wrapWidth=20)
my_mouse = event.Mouse(win = win)

wheel = visual.ElementArrayStim(win, units = 'deg', fieldPos = [0,0], fieldSize = [5,5], fieldShape = 'circle', nElements = 360, sizes = WHEELWIDTH,elementMask = 'circle', elementTex = 'none', texRes = 400, phases = 1)

'''
choose the color space
can either use
(1) colors differing in hue or
(2) draw a circle in lab color space

comment out line you don't want to use
'''

colors = hsv2rgb([[i, 1, .8] for i in range(360)]) # creates 360 color values differing in hue and converts them to rgb [-1,1] format

# colors = LAB2RGB(L = 60, a = 20, b = 20, radius = 60) # uses function from extras.py to convert lab to rgb
# note that these colors won't be rendered exactly as intended if the monitor isn't calibrated properly
# see https://www.ncbi.nlm.nih.gov/pubmed/24715329

stim = [] # this loop creates 8 circle objects
for s in range(8):
    stim.append(visual.Circle(win, radius=.5))
# or
#stim = [visual.Circle(win, radius=.5) for s in range(8)]

def circle_locs(radius, angles=None):
    # function for defining locations on a circle with a certain radius at specific angles
    # if angles are not specified, 360 locations are returned
    if angles is None:
        angles = range(360)
    locs = [[np.sin((i*np.pi/180))*radius, np.cos((i*np.pi/180))*radius] for i in angles]
    return(locs)

# set the locations and colors of the circle objects
stim_locs = circle_locs(radius=4, angles=range(0,360,45))
for s in range(8):
    stim[s].pos = stim_locs[s]
    stim[s].fillColor = NONCUECOL
    stim[s].lineColor = NONCUECOL

# set the locations and colors of the color wheel
wheel_locs = circle_locs(WHEELRADIUS)
wheel.setColors(colors)
wheel.setXYs(wheel_locs)

### FUNCTIONS USED IN THE EXPERIMENT
def move_mouse(x, y):
    # uses win32api (if available) or psychopy to move the cursor
    try:
        win32api.SetCursorPos((x,y))
    except:
        x = x - WINSIZE[0]/2
        y = y - WINSIZE[1]/2
        my_mouse.setPos((x,y))

def press_key(text = 'Press SPACE to continue', k_list = ['space']):
    instr.text = text
    instr.draw()
    win.flip()
    k_list.append(QUIT)
    key = event.waitKeys(keyList = k_list)[0]
    if key == QUIT:
        core.quit()
    else:
        return(key)

def get_error(pres, resp): # gets recall error in angle difference between target and response
    error = resp - pres
    if error >= 180.0:
        error -= 360.0
    elif error <= -180.0:
        error += 360.0
    return int(error)

def get_recall(cue_loc):
    # probe for recall of a color at a particular cue location
    for i in range(len(stim)):
        if i == cue_loc:
            stim[i].fillColor = CUECOL
            stim[i].lineColor = CUECOL
        else:
            stim[i].fillColor = NONCUECOL
            stim[i].lineColor = NONCUECOL

    moved = False
    clicked = False
    move_mouse(WINSIZE[0]/2, WINSIZE[1]/2) # move mouse cursor to the middle of the screen
    win.setMouseVisible(True)

    while not clicked:
        mouse_xy = my_mouse.getPos() # get the current position of the mouse
        # then calculate the distance between the mouse position and all 360 response options
        distances = [np.sqrt((wheel_locs[i][0] - mouse_xy[0])**2 + (wheel_locs[i][1] - mouse_xy[1])**2) for i in range(len(wheel_locs))]
        min_dist = min(distances) # find the option closest to the mouse
        min_ind = np.argmin(distances) # and its index...
        current_color = colors[min_ind] # use this to update the color of the probe

        if np.sqrt(sum([x**2 for x in mouse_xy])) > 2:
            moved = True # the mouse has been moved from the center

        if moved:
            # if the mouse has been moved start continuously varying the color of the probe with mouse position
            stim[cue_loc].fillColor = current_color
            stim[cue_loc].lineColor = current_color

        wheel.draw()
        for s in range(len(stim)):
            stim[s].draw()
        win.flip()

        mouse1, mouse2, mouse3 = my_mouse.getPressed() # has the mouse been clicked?

        if mouse1 > 0 and moved:
            clicked = True
            # dont advance until the mouse is released
            while my_mouse.getPressed()[0]:
                pass

    win.setMouseVisible(False)

    stim[cue_loc].fillColor = NONCUECOL
    stim[cue_loc].lineColor = NONCUECOL
    return(min_ind) # return the hue angle recalled


def one_trial(N=4, study_time=1, delay=2, isi=.2):
    if N > 8:
        raise(Warning("too many stimuli requested"))

    trial_colors = random.sample(range(360), N)
    trial_locs = random.sample(range(8), N)

    # study
    for i in range(N):
        # set color of currently relevant item and present
        stim[trial_locs[i]].fillColor = colors[trial_colors[i]]
        stim[trial_locs[i]].lineColor = colors[trial_colors[i]]

        [stim[x].draw() for x in range(len(stim))]
        win.flip()
        core.wait(study_time)

        # isi in between items
        for s in range(len(stim)): # reset colors for isi
            stim[s].fillColor = NONCUECOL
            stim[s].lineColor = NONCUECOL

        [stim[x].draw() for x in range(len(stim))]
        win.flip()
        core.wait(isi)

    # delay interval (locations are still presented in NONCUECOL color)
    [stim[x].draw() for x in range(len(stim))]
    win.flip()
    core.wait(delay)

    # get recall responses
    recalled = []
    for r in range(N):
        recalled.append(get_recall(cue_loc = trial_locs[r]))
        [stim[x].draw() for x in range(len(stim))]
        win.flip()
        core.wait(isi)

    errors = [get_error(pres=trial_colors[x], resp=recalled[x]) for x in range(N)]
    trial_data = {"studied": trial_colors, "recalled": recalled, "locations": trial_locs, "errors": errors}

    return(trial_data)

### MAIN EXPERIMENT FUNCTION

def main(n_trials = 30, start_trial_wspace=True):

    save_path = "color-wheel-data/"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    date = datetime.now()
    datestr = date.strftime("%Y-%m-%d-%H%M")

    file_name = save_path + datestr + '.csv'

    data_file = open(file_name, 'w')
    col_headers = "id, trial, serial_pos, location, presented, recalled, error\n"
    data_file.write(col_headers)

    press_key("On each trial you will see a sequence of four colors.\n\nYou will then be asked to recall each color by clicking on a color wheel.\n\nPress SPACE to begin.")

    for t in range(n_trials):
        if start_trial_wspace:
            press_key("Press SPACE to begin trial")
        tdat = one_trial()

        # write trial data to file
        for i in range(4):
            data_file.write("%s, %i, %i, %i, %i, %i, %i \n" %(datestr, t+1, i+1, tdat["locations"][i], tdat["studied"][i], tdat["recalled"][i], tdat["errors"][i]))

    data_file.close()


main(5)
