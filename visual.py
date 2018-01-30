"""
hueh
"""
import math
import sys
import time
import argparse
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, pyqtSlot, QElapsedTimer
from PyQt5 import QtWidgets
import numpy as np
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout,
                             QLabel, QVBoxLayout, QCheckBox, QDoubleSpinBox)


class UI(QtWidgets.QMainWindow):

    def __init__(self):

        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Vizualizer")
        self.widgetHolder =  QtWidgets.QWidget()

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.widgetHolder.setLayout(self.mainLayout)

        self.show()


class Listen(QThread):

    CHANNELS = 1
    RATE = 44100
    p = None
    audio = np.array([])
    stream = None

    def __init__(self):
        QThread.__init__(self)

    def run(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=self.CHANNELS,)
        self.stream.start_stream()

    def callback(self, in_data, *kwargs):
        self.receive_time = time.time()
        audio_data = np.fromstring(in_data,dtype=np.float32)
        self.audio.extend(audio_data)
        self.comparableAudio = np.append(self.comparableAudio, audio_data)
        return audio_data, pyaudio.paContinue

    def algo(self):
        audio = np.array([self.audio.popleft() for _ in range(self.count)])

        #do stuff with audio

def my_exception_hook(exectype, value, traceback):
    """
    overrides normal exceptions, because it is wrong sometimes
    :param exectype:
    :param value:
    :param traceback:
    :return:
    """
    print(exectype,value,traceback)
    sys._excepthook(exectype,value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')



