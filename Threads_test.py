import threading
import pdb
# import pyttsx3

try:
    import queue as queue
except ImportError:
    import Queue as queue

import time


# <=~=> Class that implements the Graphical User Interface
class GUI(threading.Thread):

    # -> formula which will be displayed
    formula = ''

    # --- Main constructor
    # -> threadID helps differentiate between threads
    # -> queue is the shared queue this thread will read from
    # -> exit is the flag which tells the thread to stop
    def __init__(self, threadID, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.threadID = threadID
        self.exit = 0

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
    formulas = ['3+7/(2*5)', '2*3*4', '1-2+10/3']

    # -> Formulas queue. Testing purposes.
    formulasQueue = queue.Queue(0)

    # -> Formula found by character recognition.
    formula = ''

    # --- Main constructor
    # -> queue is the shared queue this thread will write to
    # -> threadID helps differentiate between threads
    def __init__(self, threadID, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.threadID = threadID

        # For testing purposes.
        for i in range(0, 3):
            self.formulasQueue.put(self.formulas[i])

    # --- Override the Thread run() method
    # Thread will create frames and put them in the shared queue (where the GUI will read them from). For testing purposes, this thread will "find" a formula every 3 frames
    # and send it to the GUI thread.
    def run(self):
        print("Starting background app...")
        for i in range(1, 10):
            s.acquire()
            self.queue.put(i)
            if i % 3 == 0:
                while self.formula == '':
                    self.formula = self.formulasQueue.get()
                    threadGUI.setFormula(self.formula)
                self.formula = ''
            time.sleep(1)
            if(self.formulasQueue.empty()):
                threadGUI.setExit(1)
            s.release()
        print("App shutting down...")
        return


# <== MAIN CODE HERE ==>

# --- Frame queue that both threads work will access. The GUI thread will read from it while the BackgroundApp thread will write to it.
workQueue = queue.Queue(10)

# --- Semaphore for allowing certain threads to access shared memory at a time.
s = threading.Semaphore(3)

# --- Setup and start the GUI thread.
threadGUI = GUI(1, workQueue, '')
threadGUI.start()

# --- Setup and start the BackgroundApp thread.
threadBackgroundApp = backgroundApp(2, workQueue)
threadBackgroundApp.start()


# --- Wait for both threads to finish and join them.
threadBackgroundApp.join()
threadGUI.join()

print("DONE!")
