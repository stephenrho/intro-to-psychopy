'''
Cued recall experiment:

Presents pairs of images and words.
Recall of word is cued with image and feedback is given.
For another cued recall task, see color-wheel.py
'''

from psychopy import visual, core, data, event, gui, monitors
import pandas as pd
import random, os, string, pickle

### SETTINGS
WINSIZE = [1000, 1000]
WIDTH = 30
DIST = 60
BACKGROUND=[0,0,0]
FOREGROUND=[-1,-1,-1]
IMSIZE=100
IMSIZE_DEG = 4
WORDSIZE_DEG = 1
IMWORD_SEP = 1.2*(IMSIZE_DEG + WORDSIZE_DEG)/2.0
SYMBOLS = (u"\u2713", u"\u2718")
QUIT='f8'

NLEARN = 20

### CREATE PSYCHOPY OBJECTS
mon = monitors.Monitor("monitor1", width=WIDTH, distance=DIST)
mon.setSizePix(WINSIZE)
mon.save()

win = visual.Window(WINSIZE, units = 'deg', allowGUI= False, fullScr=True, color=BACKGROUND, monitor=mon)

t_stim = visual.TextStim(win, color=FOREGROUND, pos=[0, -IMWORD_SEP/2.0], height=WORDSIZE_DEG, wrapWidth=25)
i_stim = visual.ImageStim(win, pos=[0, IMWORD_SEP/2.0], size=[IMSIZE_DEG]*2) # alt. SimpleImageStim
rect = visual.Rect(win, pos=[0,IMWORD_SEP/2.0], width=IMSIZE_DEG, height=IMSIZE_DEG, lineColor=[1,1,1], fillColor=[1,1,1])
instr = visual.TextStim(win, color=FOREGROUND, pos=[0, 0], height=.8, wrapWidth=20)
RT = core.Clock()

### READ WORDS AND CREATE BLOCK LIST
def read_words(file):
    f = open(file, 'r')
    x = f.readlines()
    x = [i.replace('\n', '') for i in x]
    x = [i.replace('\r', '') for i in x]
    return(x)

all_words = read_words(file="stimuli/words.txt")
all_images = [im for im in os.listdir('stimuli/images/') if im.endswith('.png') and not im.startswith(".")]

words = random.sample(all_words, NLEARN)
images = random.sample(all_images, NLEARN)

block_list = []
for i in range(NLEARN):
    block_list.append({"study_num": i+1, "word": words[i], "image": images[i]})


### FUNCTIONS USED IN THE EXPERIMENT
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

def study_pair(image, word, study_time = 4, isi = .5):

    i_stim.image = "stimuli/images/" + image
    t_stim.text = word.upper()

    rect.draw()
    i_stim.draw()
    t_stim.draw()
    win.flip()
    core.wait(study_time)

    win.flip()
    core.wait(isi)

def recall_pair(cue_image, correct_word, time_lim = 10, feedback = True, feedback_time = .5, restudy_time = 4, char_lim = 10):
    if not isinstance(cue_image, str) or not isinstance(correct_word, str):
        raise(Warning("in recall_pair - only one cue string at a time"))

    valid_keys = list(string.ascii_lowercase)

    i_stim.image = "stimuli/images/" + cue_image

    event.clearEvents()
    prompt = "..."
    input = prompt
    finished = False
    RT.reset()
    while not finished and RT.getTime() <= time_lim:
        t_stim.text = input
        rect.draw()
        i_stim.draw()
        t_stim.draw()
        win.flip()

        n_chars = len(list(input))
        for key in event.getKeys():
            if key in [QUIT]:
                core.quit()
            if key in ['backspace'] and n_chars > 0 and input != prompt:
                input = input[:-1] # remove last char
                if len(list(input)) == 0:
                    input = prompt
            if key in valid_keys and n_chars < char_lim:
                if input == prompt:
                    input = ""
                input = input + key.upper()
            if key in ['return']:
                finished = True

    recall_rt = RT.getTime()
    recalled = input.lower()

    correct = int(recalled == correct_word) # could give credit for mis-spelling... e.g. pashler et al 2005 gave credit for at least 70% of letters correct (presumably not in order)

    if feedback:
        if correct == 1:
            t_stim.color = [0,1,0]
            t_stim.text = recalled.upper()
            rect.draw()
            i_stim.draw()
            t_stim.draw()
            win.flip()
            core.wait(feedback_time)
            t_stim.color = FOREGROUND
        else:
            t_stim.color = [1,0,0]
            t_stim.text = recalled.upper()
            rect.draw()
            i_stim.draw()
            t_stim.draw()
            win.flip()
            core.wait(feedback_time)

            t_stim.color = FOREGROUND
            t_stim.text = correct_word.upper()
            rect.draw()
            i_stim.draw()
            t_stim.draw()
            win.flip()
            core.wait(restudy_time)

    win.flip()
    core.wait(.25)

    if recalled == prompt:
        recalled = "NA"

    return(recalled, correct, recall_rt)


### MAIN EXPERIMENT FUNCTION
def main():
    save_path = "cued-recall-data/"
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    #win.winHandle.minimize()
    #win.flip()

    expInfo = {'Participant' : 1, 'Gender': ['M', 'F', "O"], 'Age' : 18}
    expInfo['dateStr'] = data.getDateStr()

    dlg = gui.DlgFromDict(expInfo, title = "Basic Information", fixed = ['dateStr'], order=['Participant', 'Age', 'Gender'])
    if not dlg.OK:
        core.quit()

    #win.winHandle.maximize()
    #win.winHandle.activate()
    #win.fullscr=True
    #win.winHandle.set_fullscreen(True)
    #win.flip()

    pNo = expInfo["Participant"]
    gen =  expInfo["Gender"]
    age =  expInfo["Age"]
    date = expInfo['dateStr']

    press_key("Press SPACE to start.")

    # study
    for pair in range(NLEARN):
        study_pair(image=block_list[pair]["image"], word=block_list[pair]["word"])

    instr.text = "RECALL"
    instr.draw()
    win.flip()
    core.wait(1)

    recall_order = range(NLEARN)
    random.shuffle(recall_order)
    # recall
    for pair in recall_order:
        recalled, acc, rt = recall_pair(cue_image=block_list[pair]["image"], correct_word=block_list[pair]["word"])
        # add to dictionary
        block_list[pair]["recall_order"] = recall_order.index(pair) + 1
        block_list[pair]["recalled"] = recalled
        block_list[pair]["recall_acc"] = acc
        block_list[pair]["recall_rt"] = rt

    #print(block_list)

    block_list_pd = pd.DataFrame(block_list)
    block_list_pd["pid"] = pNo
    block_list_pd["date"] = date
    block_list_pd["age"] = age

    file_name = save_path + "p" + str(pNo) + "_" + date

    block_list_pd.to_csv(file_name + ".csv")
    block_list_pd.to_pickle(file_name + ".pkl")


if __name__ == '__main__':
    main()
