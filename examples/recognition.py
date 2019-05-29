'''
Simple recognition memory experiment:

Presents list of words then mix of old and new items.
Response is old-new button press followed by confidence rating 1-3.
'''

from psychopy import visual, monitors, core, data, event, gui
import random, os, csv
import pandas as pd

### SETTINGS
WINSIZE = [1000, 1000]
WIDTH = 30
DIST = 60
BACKGROUND=[0,0,0]
FOREGROUND=[-1,-1,-1]
QUIT="escape"

### CREATE PSYCHOPY OBJECTS
mon = monitors.Monitor("monitor1", width=WIDTH, distance=DIST)
mon.setSizePix(WINSIZE)
mon.save()

win = visual.Window(WINSIZE, units = 'deg', allowGUI=False, fullScr=True, color=BACKGROUND, monitor=mon)

text_stim = visual.TextStim(win, color=FOREGROUND, pos=[0,0], height=1, wrapWidth=25)
conf_scale = visual.RatingScale(win, low=1, high=3, singleClick=True, showAccept=False, labels=('Low','Med','High'), scale='How confident are you?', pos=[0,0])

RT = core.Clock()

### GUI FOR GETTING PARTICIPANT INFO
expInfo = {'Participant' : 1, 'Order': [1, 2], 'Age' : 18}
expInfo['dateStr'] = data.getDateStr()

dlg = gui.DlgFromDict(expInfo, title = "Basic Information", fixed = ['dateStr'], order=['Participant', 'Order', 'Age'])
if not dlg.OK:
    core.quit()

save_path = "recognition-data/"
if not os.path.exists(save_path):
    os.makedirs(save_path)

# determine the list seen
a = csv.DictReader(open('stimuli/study_list%s.csv' % expInfo["Order"]), delimiter=',')
study_list = [x for x in a]

b = csv.DictReader(open('stimuli/test_list%s.csv' % expInfo["Order"]), delimiter=',')
test_list = [x for x in b]


'''
# alternatively - the code below produces random lists for each participant from the words.txt file

def read_words(file):
    f = open(file, 'r')
    x = f.readlines()
    x = [i.replace('\n', '') for i in x]
    x = [i.replace('\r', '') for i in x]
    return(x)

all_words = read_words(file="stimuli/words.txt")

study_words = random.sample(all_words, len(all_words)/2)
study_list = [{"word": i} for i in study_words]
print(study_list)

test_list = []
for i in range(len(all_words)):
    if all_words[i] in study_words:
        test_list.append({"num": i+1, "word": all_words[i], "item_old": 1})
    else:
        test_list.append({"num": i+1, "word": all_words[i], "item_old": 0})
'''


### FUNCTIONS USED IN THE EXPERIMENT
def press_key(text = 'Press SPACE to continue', k_list = ['space']):
    text_stim.text = text
    text_stim.draw()
    win.flip()
    k_list.append(QUIT)
    key = event.waitKeys(keyList = k_list)[0]
    if key == QUIT:
        core.quit()
    else:
        return(key)


def study_proc(study_list, pres_time = 2, isi = .5):

    win.flip()
    core.wait(1)
    for item in study_list:
        text_stim.text = item["word"].upper()
        text_stim.draw()
        win.flip()
        core.wait(pres_time)

        text_stim.text = "+"
        text_stim.draw()
        win.flip()
        core.wait(isi)


def test_proc(test_list):

    press_key("Test:\n\n'O' = old\n'N' = new\n\nPress SPACE to start")
    # loop through the test list
    for item in test_list:
        text_stim.text = item["word"].upper()
        text_stim.draw()
        win.flip()

        RT.reset()
        resp = event.waitKeys(keyList=["o", "n", QUIT])[0] # returns a list, we just want the first element
        if resp == QUIT:
            core.quit()
        resp_rt = RT.getTime()

        while conf_scale.noResponse:
            conf_scale.draw()
            win.flip()

        conf = conf_scale.getRating()
        conf_rt = conf_scale.getRT()
        conf_scale.reset()

        win.flip()
        core.wait(.5)

        if resp == "o":
            resp_old = 1
        else:
            resp_old = 0

        # add data to the dictionary
        item["resp"] = resp
        item["resp_old"] = resp_old
        item["resp_rt"] = resp_rt
        item["conf"] = conf
        item["conf_rt"] = conf_rt

    return(test_list)

### MAIN EXPERIMENT FUNCTION
def main():

    press_key("Remember these words.\n\nLater on you'll be asked to identify these words among new words.\n\nPress SPACE to begin...")
    # present study list
    study_proc(study_list)

    press_key("Now we will test your memory for the words you just saw. You'll see words one at a time. For each decide whether it is old (just studied) or new (not studied).\n\nPress SPACE to continue...")
    # present test
    test_data = test_proc(test_list)

    # convert to a data frame and add some columns
    test_data_pd = pd.DataFrame(test_data)
    test_data_pd["pid"] = expInfo["Participant"]
    test_data_pd["order"] = expInfo["Order"]
    test_data_pd["age"] = expInfo["Age"]

    # use pandas to write data to csv file
    test_data_pd.to_csv(save_path + "p" + str(expInfo["Participant"]) + "_" + expInfo["dateStr"] + ".csv")


if __name__ == '__main__':
    main()
