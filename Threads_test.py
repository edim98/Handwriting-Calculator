import threading
import pdb
from tkinter import *
from PIL import ImageTk, Image
# import pyttsx3

try:
    import queue as queue
except ImportError:
    import Queue as queue

import time


# <=~=> Class that implements the Graphical User Interface
class GUI():

    # -> formula which will be displayed
    formula = ''

    # --- Main constructor
    # -> threadID helps differentiate between threads
    # -> queue is the shared queue this thread will read from
    # -> exit is the flag which tells the thread to stop
    def __init__(self, queue):
        self.queue = queue
        self.exit = 0

        self.root = Tk()
        self.root.geometry("800x600")
        self.image = ImageTk.PhotoImage(Image.open('./image.jpg').resize((800, 600), Image.ANTIALIAS))
        self.panel = Label(self.root, image = self.image)
        self.panel.pack(side = "bottom", fill = X)
        self.root.update_idletasks()
        self.root.update()

    # --- Basic setter
    # Sets a new value of < formula >
    def setFormula(self, formula):
        self.formula = formula

    # --- Basic setter
    # Sets a new value of < exit >
    def setExit(self, exit):
        self.exit = exit

    # --- Override the Thread run() method
    # Thread will display frames which are read from the shared queue. Whenever the formula is changed, it will be displayed.
    def run(self):

        print("Starting GUI...")

        while self.exit == 0:
            s.acquire()
            frame = self.queue.get()
            print("I am displaying frame number: " + str(frame))

            newImage = ImageTk.PhotoImage(Image.open(frame).resize((800, 600), Image.ANTIALIAS))
            self.panel.configure(image = newImage)
            self.panel.image = newImage
            self.root.update_idletasks()
            self.root.update()

            if(self.formula != ''):
                print("I got a formula: " + self.formula)
                self.formula = ''

            time.sleep(1)

            s.release()

        print("GUI shutting down...")

        return

# <=~=> Class that implements the equation recognition and communication with the GPIO.
class backgroundApp(threading.Thread):

    # -> Random values for formulas.
    formulas = ['x^2+y^2', '1/3', '3+2']

    frames = ['./image.jpg', './dog.jpg', './Birds.jpg', './dude.jpg', './trump.jpg', './wow.jpg']

    # -> Formulas queue. Testing purposes.
    formulasQueue = queue.Queue(0)

    # -> Formula found by character recognition.
    formula = ''

    exit = 0

    # --- Main constructor
    # -> queue is the shared queue this thread will write to
    # -> threadID helps differentiate between threads
    def __init__(self, threadID, queue):
        threading.Thread.__init__(self)
        self.queue = queue

        # For testing purposes.
        for i in range(0, 3):
            self.formulasQueue.put(self.formulas[i])

    # --- Override the Thread run() method
    # Thread will create frames and put them in the shared queue (where the GUI will read them from). For testing purposes, this thread will "find" a formula every 3 frames
    # and send it to the GUI thread.
    def run(self):
        print("Starting background app...")
        #i = 0
        #while self.exit == 0:
        for i in range(0, 6):
            s.acquire()
            self.queue.put(self.frames[i])
            if i % 2 == 0:
                while self.formula == '':
                    self.formula = self.formulasQueue.get()
                    threadGUI.setFormula(self.formula)
                self.formula = ''
            time.sleep(1)
            if(self.formulasQueue.empty()):
                threadGUI.setExit(1)
                self.exit = 1
            s.release()
        print("App shutting down...")
        return


# <== MAIN CODE HERE ==>

# --- Frame queue that both threads work will access. The GUI thread will read from it while the BackgroundApp thread will write to it.
workQueue = queue.Queue(10)

# --- Semaphore for allowing certain threads to access shared memory at a time.
s = threading.Semaphore(3)

# --- Setup the GUI.
threadGUI = GUI(workQueue)

# --- Setup and start the BackgroundApp thread.
threadBackgroundApp = backgroundApp(2, workQueue)
threadBackgroundApp.start()

# -- Start the main Thread
threadGUI.run()

# --- Wait for both threads to finish and join them.
threadBackgroundApp.join()

print("DONE!")
