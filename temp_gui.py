import argparse
import os
import time
from collections import deque
import math
import pyaudio
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, pyqtSlot, QElapsedTimer
import pyqtgraph as pg
from PyQt5 import QtWidgets
import numpy as np
import sys
from PyQt5.QtGui import QPixmap, QIcon
from sklearn.externals import joblib
import ctypes
from pyqtgraph.Qt import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout,
                             QLabel, QVBoxLayout, QCheckBox, QDoubleSpinBox)
from datetime import datetime

class UI(QtWidgets.QMainWindow):
    """
        Class to create the GUI, the front-end of this project
    """
    def __init__(self, showCTWM, showWHM, showRTLE, algorithmCTWM, algorithmWHM, tool_type_text, material_text,
                 flutes_text, coating_text, cutting_type_text, wpmaterial_text, heat_text, tool_diameter_num,
                 parent_img_path=None):
        """
        Initialize the GUI. Entire thing is in a VBox
        :param showCTWM: boolean: Show the Cutting Tool Wear Monitoring (CTWM)
        :param showWHM: boolean: Show the Workpiece Hardness Monitoring (WHM)
        :param showRTLE: boolean: Show the Remaining Tool Life Estimation (RTLE)
        :param algorithmCTWM: Thread that run the algorithm for CTWM
        :param algorithmWHM: Thread that runs the algorithm for WHM
        :param parent_img_path: Path of where the images to display are
        """

        # Initialize the widget and the main window
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle("Smart Sensing System")
        #self.setFixedSize(1000, 450)
        self.widgetHolder = QtWidgets.QWidget()
        self.setCentralWidget(self.widgetHolder)

        # Set all the passed arguments as class variables
        self.parent_img_path = parent_img_path
        self.showCTWM = showCTWM
        self.showWHM = showWHM
        self.showRTLE = showRTLE
        self.tool_type_text = tool_type_text
        self.material_text = material_text
        self.flutes_text = flutes_text
        self.coating_text = coating_text
        self.cutting_type_text = cutting_type_text
        self.wpmaterial_text = wpmaterial_text
        self.heat_text = heat_text
        self.tool_diameter_num = tool_diameter_num


        # Pre-loading all images into dictionary
        self.images = dict()

        if self.showCTWM:
            self.images['imageFailureGrayCTWM'] = QPixmap(os.path.join(self.parent_img_path, "failure_gray.jpg"))
            self.images['imageAdvancedGrayCTWM'] = QPixmap(os.path.join(self.parent_img_path, "advanced_gray.jpg"))
            self.images['imageAverageGrayCTWM'] = QPixmap(os.path.join(self.parent_img_path, "average_gray.jpg"))
            self.images['imageGoodGrayCTWM'] = QPixmap(os.path.join(self.parent_img_path, "good_gray.jpg"))
            self.images['imageGoodGreenCTWM'] = QPixmap(os.path.join(self.parent_img_path, "good_green.jpg"))
            self.images['imageAverageYellowCTWM'] = QPixmap(os.path.join(self.parent_img_path, "average_yellow.jpg"))
            self.images['imageAdvancedOrangeCTWM'] = QPixmap(os.path.join(self.parent_img_path, "advanced_orange.jpg"))
            self.images['imageFailureRedCTWM'] = QPixmap(os.path.join(self.parent_img_path, "failure_red.jpg"))
        if self.showWHM:
            self.images['imageLevelFourWHMgray'] = QPixmap(os.path.join(self.parent_img_path, "levelFour_gray.jpg"))
            self.images['imageLevelThreeWHMgray'] = QPixmap(os.path.join(self.parent_img_path, "levelThree_gray.jpg"))
            self.images['imageLevelTwoWHMgray'] = QPixmap(os.path.join(self.parent_img_path, "levelTwo_gray.jpg"))
            self.images['imageLevelOneWHMgray'] = QPixmap(os.path.join(self.parent_img_path, "levelOne_gray.jpg"))
            self.images['imageLevelOneWHMgreen'] = QPixmap(os.path.join(self.parent_img_path, "levelOne_green.jpg"))
            self.images['imageLevelTwoWHMyellow'] = QPixmap(os.path.join(self.parent_img_path, "levelTwo_yellow.jpg"))
            self.images['imageLevelThreeWHMorange'] = QPixmap(os.path.join(self.parent_img_path, "levelThree_orange.jpg"))
            self.images['imageLevelFourWHMred'] = QPixmap(os.path.join(self.parent_img_path, "levelFour_red.jpg"))

        # Initialize file to save output to
        self.save_file_name = "HTW" + str(datetime.now().date())
        self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "w")
        self.save_file.write("History of Tool Wear" + "\n")
        self.save_file.close()


        # Assigns the thread that runs the algorithm to the flag setPointsCTWM
        self.setPointsCTWM = algorithmCTWM
        # When the algorithm raises the flag 'finished', do the function "updateCTWM"
        self.setPointsCTWM.finished.connect(self.updateCTWM)

        # Assigns the thread that runs the algorithm to the flag setPointsWHM
        self.setPointsWHM = algorithmWHM
        # When the algorithm raises the flag 'finished', do the function "updateWHM"
        self.setPointsWHM.finished.connect(self.updateWHM)

        # Create a VBox called Main Layout that will contain all the other widgets
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.widgetHolder.setLayout(self.mainLayout)

        ###############################################################################################################
        #                                                                                                             #
        #                                               FIRST ROW: IN AN HBOX                                         #
        #                          Contains Title, Start, Stop, Reset, Save buttons, and Save directory               #
        ###############################################################################################################
        self.firstRow = QtWidgets.QHBoxLayout()
        self.windowTitle = QtWidgets.QLabel("Smart Sensing System")
        self.windowTitle.setContentsMargins(0, 0, 30, 0)  # someLayout.setContentsMargins(left, top, right, bottom)
        self.font = QtGui.QFont("Corbel", 16, QtGui.QFont.Bold, QtGui.QFont.StyleItalic)
        self.windowTitle.setFont(self.font)
        self.firstRow.addWidget(self.windowTitle)
        self.startButton = QtWidgets.QPushButton("Start")
        self.startButton.setMinimumWidth(200)
        self.startButton.setEnabled(True)
        self.startButton.setStyleSheet("background-color: #009933")
        self.startButton.clicked.connect(self.startButtonPressed)
        self.firstRow.addWidget(self.startButton)
        self.stopButton = QtWidgets.QPushButton("Stop")
        self.stopButton.setMinimumWidth(200)
        self.stopButton.setEnabled(False)
        self.stopButton.setStyleSheet("background-color: #cc2900")
        self.stopButton.clicked.connect(self.stopButtonPressed)
        self.firstRow.addWidget(self.stopButton)
        self.reset = QtWidgets.QPushButton("Reset") # connection to clicked in init -> Clear CTWM and WHM Graphs
        self.reset.setEnabled(True)
        self.reset.setMaximumWidth(70)
        self.reset.clicked.connect(self.resetPressed)
        self.firstRow.addWidget(self.reset)

        self.addressBox = QtWidgets.QLineEdit()
        self.addressBox.setMaximumWidth(200)
        self.addressBox.setPlaceholderText("Address")
        self.addressBox.setContentsMargins(30, 0, 0, 0) # someLayout.setContentsMargins(left, top, right, bottom)
        self.addressBox.setAlignment(QtCore.Qt.AlignCenter)
        self.firstRow.addWidget(self.addressBox)
        self.screenshotNum = 0 # For filename saving purposes
        self.save = QtWidgets.QPushButton("Save")
        self.save.setMaximumWidth(70)
        self.save.clicked.connect(self.saveWindowState)
        self.firstRow.addWidget(self.save)
        self.mainLayout.addLayout(self.firstRow)

        ###############################################################################################################
        #                                                                                                             #
        #                                               SECOND ROW: IN AN HBOX                                        #
        #                          For Cutting Tool Wear Monitoring and Workpiece Hardness Monitoring                 #
        ###############################################################################################################
        self.secondRow = QtWidgets.QHBoxLayout()
        # These are some configurations for the graph for user-viewing purposes
        pg.setConfigOption('background', '#d9d9d9')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)
        # Set up pen to be used to draw the graphs
        self.pen = pg.mkPen(color='b', width=3)

        # Use a numpy array to keep track of the outcomes of the wear condition
        self.outcomesCTWM = np.array([])
        # Use a numpy array to keep track of the outcomes of the hardness condition
        self.outcomesWHM = np.array([])

        if self.showCTWM: # Show the Cutting Tool Wear Monitoring widget
            self.initCTWM()
        if self.showWHM: # Show the Workpiece Hardness Monitoring widget
            self.initWHM()
        self.mainLayout.addLayout(self.secondRow)

        ###############################################################################################################
        #                                                                                                             #
        #                                               THIRD ROW: IN AN VBOX                                         #
        #                                        For Remaining Tool Life Estimation                                   #
        ###############################################################################################################
        if self.showRTLE: # Show the Remaining Tool Life Estimation widget
            self.initRTLE()

        ###############################################################################################################
        #                                                                                                             #
        #                                               FOURTH ROW: IN AN HBOX                                        #
        #                                         Contains RIT label and version number                               #
        ###############################################################################################################
        self.fourthRow = QtWidgets.QHBoxLayout()
        self.versionFont = QtGui.QFont("Corbel", 10)
        self.version = QLabel("Version: 1.0")
        self.version.setFont(self.versionFont)
        self.version.setAlignment(QtCore.Qt.AlignRight)
        self.fourthRow.addWidget(self.version)
        self.mainLayout.addLayout(self.fourthRow)

        # Show all these widgets
        self.show()

        ##############################################################################################################
        #                                                                                                             #
        #                                              ALL BUTTONS' FUNCTIONALITY                                     #
        #                                                                                                             #
        ###############################################################################################################
    def startButtonPressed(self):
        """
        Starts the algorithm when Start button is pressed
        :return: None
        """
        self.showtime = time.time()

        self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "a")
        self.save_file.write("\nStart Button Pressed\n")
        self.save_file.close()

        # Timers for x axis scrolling.
        self.tmr = QElapsedTimer()
        self.tmr.start()
        print("Start button has been pressed!")

        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.reset.setEnabled(False)
        if self.showCTWM:
            self.setPointsCTWM.start()  # starts the algorithm
        if self.showWHM:
            time.sleep(0.1)
            self.setPointsWHM.start()

    def stopButtonPressed(self):
        """
        Stops the algorithm when Stop button is pressed
        :return: None
        """

        self.booleanStartButtonPressed = False  # For RTLE's updateLabel function to check

        self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "a")
        self.save_file.write("\nStop Button Pressed\n")
        self.save_file.close()

        print("Stop button has been pressed!")

        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)
        self.reset.setEnabled(True)
        if self.showCTWM:
            self.setPointsCTWM.stopit() # stops the algorithm
        if self.showWHM:
            time.sleep(0.1)
            self.setPointsWHM.stopit()

        # self.save_file.close()

    def saveWindowState(self):
        """
        Save a snapshot of the window state currently
        :return: None
        """
        print("Save button has been pressed!")
        screenshot = self.widgetHolder.grab()
        self.screenshotNum += 1
        if(self.addressBox.text() != ""):
            screenshot.save(os.path.join(self.addressBox.text(), ("screenshot" + str(self.screenshotNum) + ".jpg")))
        else:
            screenshot.save("screenshot" + str(self.screenshotNum) + ".jpg", "jpg")

    def resetPressed(self):

        """
        Reset CTWM and WHM graphs
        :return: None
        """
        print("Reset button has been pressed!")
        self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "a")
        self.save_file.write("\n" + "-------*Reset Button Pressed*-------" + "\n")
        self.save_file.close()
        # CTWM Resetting
        if self.showCTWM:
            self.outcomesCTWM = np.array([])
            self.CTWMx = [0]
            self.CTWMy = [0]
            self.curveCTWMGraph.setData(x=self.CTWMx, y=self.CTWMy)
            self.CTWMGraph.clear()
            self.CTWMGraph.draw()
            # Does what initImgCTWM does
            self.labelFailureGrayCTWM.setPixmap(self.images['imageFailureGrayCTWM'])
            self.labelAdvancedGrayCTWM.setPixmap(self.images['imageAdvancedGrayCTWM'])
            self.labelAverageGrayCTWM.setPixmap(self.images['imageAverageGrayCTWM'])
            self.labelGoodGrayCTWM.setPixmap(self.images['imageGoodGrayCTWM'])

        # WHM resetting
        if self.showWHM:
            self.outcomesWHM = np.array([])
            self.curveWHMGraph.setData(x=[0], y=[0])
            self.WHMGraph.clear()
            self.WHMGraph.draw()
            # Does what initImgWHM does
            self.labelLevelFourWHM.setPixmap(self.images['imageLevelFourWHMgray'])
            self.labelLevelThreeWHM.setPixmap(self.images['imageLevelThreeWHMgray'])
            self.labelLevelTwoWHM.setPixmap(self.images['imageLevelTwoWHMgray'])
            self.labelLevelOneWHM.setPixmap(self.images['imageLevelOneWHMgray'])

        # RTLE resetting
        if self.showRTLE:
            self.speed.setText("")
            self.feed.setText("")
            self.RTLEGraph.clear()
            self.RTLEGraph.draw()
            self.labelTimeAverageWear.setText("")
            self.labelTimeAdvancedWear.setText("")
            self.labelTimeFailureWear.setText("")
            self.curveRTLEGraph = pg.BarGraphItem(name="RLTEGraph", x=[1], height=30, width=3, brush='d9d9d9')
            self.curveRTLEGraph.rotate(-90)  # horizontal graph
            self.RTLEGraph.addItem(self.curveRTLEGraph)

        ###############################################################################################################
        #                                                                                                             #
        #                                            INITIALIZING ALL THE WIDGETS                                     #
        #                                                                                                             #
        ###############################################################################################################
    def initCTWM(self):
        """
        Create a CTWM widget
        :return: None
        """

        self.dataCTWM = deque(maxlen=100) # change this for how many seconds are visible before scrolling

        # To create one "big" widget, use a VBox
        self.secondRowCTWM = QtWidgets.QVBoxLayout()

        # Add the title on the first row of the VBox
        self.CTWMTitle = QLabel("Cutting Tool Wear Monitoring")
        self.CTWMTitle.setContentsMargins(0, 0, 0, 10)  # someLayout.setContentsMargins(left, top, right, bottom)
        self.CTWMTitle.setAlignment(QtCore.Qt.AlignHCenter)
        self.CTWMFont = QtGui.QFont("Corbel", 14, QtGui.QFont.Bold)
        self.CTWMTitle.setFont(self.CTWMFont)
        self.secondRowCTWM.addWidget(self.CTWMTitle)

        # Second row of this VBox includes an Hbox that will contain the images "Good, Average...", the information
        # on the tool, and the graph
        self.CTWM_ImgLabelGraph = QtWidgets.QHBoxLayout()
        self.initImgCTWM()  # This function already adds the images to the CTWM_ImgLabelGraph HBox

        # VBox where the labels (information like Tool Type, Flutes, etc.) and the real-time graph is stored
        self.CTWMlabelGraph = QtWidgets.QVBoxLayout()

        # HBox for the labels
        self.CTWMlabels = QtWidgets.QHBoxLayout()
        # The small font to be used for the labels
        self.CTWMsmallFont = QtGui.QFont("Corbel", 10, italic=True)

        self.CTWMlabels_ColOne = QtWidgets.QFormLayout()
        self.toolTypeLabel = QLabel("Tool Type: ")
        self.toolTypeLabel.setFont(self.CTWMsmallFont)
        self.toolType = QLabel(self.tool_type_text)
        self.toolType.setFont(self.CTWMsmallFont)
        self.CTWMlabels_ColOne.addRow(self.toolTypeLabel, self.toolType)
        self.toolDiameterLabel = QLabel("Tool Diameter: ")
        self.toolDiameterLabel.setFont(self.CTWMsmallFont)
        self.toolDiameter = QLabel(self.tool_diameter_num)
        self.toolDiameter.setFont(self.CTWMsmallFont)
        self.CTWMlabels_ColOne.addRow(self.toolDiameterLabel, self.toolDiameter)
        self.flutesLabel = QLabel("Flutes: ")
        self.flutesLabel.setFont(self.CTWMsmallFont)
        self.flutes = QLabel(self.flutes_text)
        self.flutes.setFont(self.CTWMsmallFont)
        self.CTWMlabels_ColOne.addRow(self.flutesLabel, self.flutes)
        self.toolMaterialLabel = QLabel("Tool Material: ")
        self.toolMaterialLabel.setFont(self.CTWMsmallFont)
        self.toolMaterial = QLabel(self.material_text)
        self.toolMaterial.setFont(self.CTWMsmallFont)
        self.CTWMlabels_ColOne.addRow(self.toolMaterialLabel, self.toolMaterial)
        self.CTWMlabels.addLayout(self.CTWMlabels_ColOne)
        self.CTWMlabels_ColTwo = QtWidgets.QFormLayout()
        self.coatingLabel = QLabel("Coating: ")
        self.coatingLabel.setFont(self.CTWMsmallFont)
        self.coating = QLabel(self.coating_text)
        self.coating.setFont(self.CTWMsmallFont)
        self.CTWMlabels_ColTwo.addRow(self.coatingLabel, self.coating)
        self.typeLabel = QLabel("Type: ")
        self.typeLabel.setFont(self.CTWMsmallFont)
        self.type = QLabel("Type")
        self.type.setFont(self.CTWMsmallFont)
        self.CTWMlabels_ColTwo.addRow(self.typeLabel, self.type)
        self.CTWMlabels.addLayout(self.CTWMlabels_ColTwo)
        self.CTWMlabels.setContentsMargins(0, 0, 0, 10)  # someLayout.setContentsMargins(left, top, right, bottom)

        # Add these labels to the label/graph layout
        self.CTWMlabelGraph.addLayout(self.CTWMlabels)

        # Create the CTWM graph
        self.yCTWM = [' ', 'Good', 'Average', 'Advanced', 'Failure']
        self.ydictCTWM = dict(enumerate(self.yCTWM))
        self.stringAxisCTWM = pg.AxisItem(orientation='left')
        self.stringAxisCTWM.setRange(1, 4)
        self.stringAxisCTWM.setTicks([self.ydictCTWM.items()])
        self.CTWMGraph = pg.PlotWidget(name='CTWMGraph', axisItems={'left': self.stringAxisCTWM})
        self.CTWMGraph.setYRange(1, 4)
        self.CTWMGraph.setLabel('left', "Tool Condition")
        self.CTWMGraph.setLabel('bottom', "Time", units='s')
        self.CTWMGraph.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)
        self.CTWMGraph.setMouseEnabled(x=False, y=False)
        self.curveCTWMGraph = self.CTWMGraph.plot(pen=self.pen)

        # Add the graph to the label/graph layout
        self.CTWMlabelGraph.addWidget(self.CTWMGraph)
        # Add the labels and graph to the images/label/graph layout
        self.CTWM_ImgLabelGraph.addLayout(self.CTWMlabelGraph)
        # Add the images/label/graph layout to the CTWM widget
        self.secondRowCTWM.addLayout(self.CTWM_ImgLabelGraph)
        # Add the CTWM widget to the second row
        self.groupCTWM = QGroupBox()
        self.groupCTWM.setStyleSheet("QGroupBox { background-color: #d9d9d9; border:1px solid #070707; }")
        self.groupCTWM.setLayout(self.secondRowCTWM)
        self.secondRow.addWidget(self.groupCTWM)

    def initWHM(self):
        """
        Create a WHM widget
        :return: None
        """

        self.dataWHM = deque(maxlen=60)

        # To create on "big" widget, use Vbox
        self.secondRowWHM = QtWidgets.QVBoxLayout()

        # Add the title on the first row of the VBox
        self.WHMTitle = QLabel("Workpiece Hardness Monitoring")
        self.WHMTitle.setContentsMargins(0, 0, 0, 10)  # someLayout.setContentsMargins(left, top, right, bottom)
        self.WHMTitle.setAlignment(QtCore.Qt.AlignHCenter)
        self.WHMFont = QtGui.QFont("Corbel", 14, QtGui.QFont.Bold)
        self.WHMTitle.setFont(self.WHMFont)
        self.secondRowWHM.addWidget(self.WHMTitle)

        # Second row of this VBox includes an Hbox that will contain the images "Level 1, Level 2...", the information
        # on the material, and the graph
        self.WHM_ImgLabelGraph = QtWidgets.QHBoxLayout()
        self.initImgWHM() # This function already adds the images to the WHM_ImgLabelGraph HBox

        # VBox, where the labels (Workpiece Material and Heat Treatment) and the real-time graph is stored
        self.WHMlabelGraph = QtWidgets.QVBoxLayout()

        self.WHMsmallFont = QtGui.QFont("Corbel", 10, italic=True)

        # Form layout to store the labels
        self.WHMlabels = QtWidgets.QFormLayout()
        self.workpieceMaterialLabel = QLabel("Workpiece Material: ")
        self.workpieceMaterialLabel.setFont(self.WHMsmallFont)
        self.workpieceMaterial = QLabel(self.wpmaterial_text)
        self.workpieceMaterial.setFont(self.WHMsmallFont)
        self.WHMlabels.addRow(self.workpieceMaterialLabel, self.workpieceMaterial)
        self.heatTreatmentLabel = QLabel("Heat Treatment: ")
        self.heatTreatmentLabel.setFont(self.WHMsmallFont)
        self.heatTreatment = QLabel(self.heat_text)
        self.heatTreatment.setFont(self.WHMsmallFont)
        self.WHMlabels.addRow(self.heatTreatmentLabel, self.heatTreatment)
        # Added these two rows for space buffer reasons - lines up with CTWM graph perfectly
        self.WHMlabels.addRow(QLabel(""))
        self.WHMlabels.setContentsMargins(0, 0, 0, 10)  # someLayout.setContentsMargins(left, top, right, bottom)
        self.WHMlabelGraph.addLayout(self.WHMlabels)

        # Create the WHM graph
        self.yWHM = [' ', '1', '2', '3', '4']
        self.ydictWHM = dict(enumerate(self.yWHM))
        self.stringAxisWHM = pg.AxisItem(orientation='left')
        self.stringAxisWHM.setTicks([self.ydictWHM.items()])
        self.WHMGraph = pg.PlotWidget(name='WHM', axisItems={'left': self.stringAxisWHM})
        self.WHMGraph.setYRange(1, 4)
        self.WHMGraph.setLabel('left', 'Level')
        self.WHMGraph.setLabel('bottom', 'Time', units='s')
        self.WHMGraph.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)
        self.WHMGraph.setMouseEnabled(x=False, y=False)
        self.curveWHMGraph = self.WHMGraph.plot(pen=self.pen)

        # Add the graph to the label/graph layout
        self.WHMlabelGraph.addWidget(self.WHMGraph)
        # Add the labels and graph to the images/label/graph layout
        self.WHM_ImgLabelGraph.addLayout(self.WHMlabelGraph)
        # Add the images/label/graph layout to the CTWM widget
        self.secondRowWHM.addLayout(self.WHM_ImgLabelGraph)
        # Add the WHM widget to the second row
        self.groupWHM = QGroupBox()
        self.groupWHM.setStyleSheet("QGroupBox { background-color: #d9d9d9; border:1px solid #070707; }")
        self.groupWHM.setLayout(self.secondRowWHM)
        self.secondRow.addWidget(self.groupWHM)

    def initRTLE(self):
        """
        Initialize the Remaining Tool Life Estimation widget
        :return: None
        """
        # To create one "big" widget, use a VBox
        self.thirdRowRTLE = QtWidgets.QVBoxLayout()

        # Add the title on the first row of the VBox
        self.RTLETitle = QLabel("Remaining Tool Life Estimation")
        self.RTLETitle.setAlignment(QtCore.Qt.AlignHCenter)
        self.RTLETitle.setContentsMargins(0, 0, 0, 10)  # someLayout.setContentsMargins(left, top, right, bottom
        self.RTLEFont = QtGui.QFont("Corbel", 14, QtGui.QFont.Bold)
        self.RTLETitle.setFont(self.RTLEFont)
        # Add the title to the main VBox
        self.thirdRowRTLE.addWidget(self.RTLETitle)

        # HBox to hold the user input information, the labels to show, and the graph
        self.RTLEInfoLabelGraph = QtWidgets.QHBoxLayout()

        self.RTLEsmallFont = QtGui.QFont("Corbel", 10)

        # Form Layout to hold the user input information
        self.RTLEuserInput = QtWidgets.QFormLayout()
        self.toolNumberLabel = QLabel("Tool Number: ")
        self.toolNumberLabel.setFont(self.RTLEsmallFont)
        self.toolNumber = QtWidgets.QLineEdit()
        self.toolNumber.setFont(self.RTLEsmallFont)
        self.toolNumber.setFixedWidth(100)
        self.speedLabel = QLabel("Speed (RPM): ")
        self.speedLabel.setFont(self.RTLEsmallFont)
        self.speed = QtWidgets.QLineEdit()
        self.speed.setFont(self.RTLEsmallFont)
        self.speed.setFixedWidth(100)
        self.feedLabel = QLabel("Feed Rate (IPM): ")
        self.feedLabel.setFont(self.RTLEsmallFont)
        self.feed = QtWidgets.QLineEdit()
        self.feed.setFont(self.RTLEsmallFont)
        self.feed.setFixedWidth(100)
        self.radialDOCLabel = QLabel("Radial DOC (IN): ")
        self.radialDOCLabel.setFont(self.RTLEsmallFont)
        self.radialDOC = QtWidgets.QLineEdit()
        self.radialDOC.setFont(self.RTLEsmallFont)
        self.radialDOC.setFixedWidth(100)
        self.RTLEuserInput.addRow(self.toolNumberLabel, self.toolNumber)
        self.RTLEuserInput.addRow(self.speedLabel, self.speed)
        self.RTLEuserInput.addRow(self.feedLabel, self.feed)
        self.RTLEuserInput.addRow(self.radialDOCLabel, self.radialDOC)
        self.computeButton = QtWidgets.QPushButton("Compute")
        self.computeButton.setFixedWidth(70)
        self.computeButton.clicked.connect(self.updateRTLE)
        self.RTLEuserInput.addRow(self.computeButton)
        # Add the user input information to the HBox that holds the info, label, and graph
        self.RTLEInfoLabelGraph.addLayout(self.RTLEuserInput)

        # Form Layout to hold the labels to show
        self.RTLElabelsToShow = QtWidgets.QFormLayout()
        self.remainingTimeToFont = QtGui.QFont("Corbel", 10, QtGui.QFont.Bold)
        self.remainingTimeToLabel = QLabel("Remaining Time To (MIN):")
        self.remainingTimeToLabel.setFont(self.remainingTimeToFont)
        self.averageWearLabel = QLabel("Average Wear:          ")
        self.averageWearLabel.setFont(self.RTLEsmallFont)
        self.labelTimeAverageWear = QLabel()
        self.labelTimeAverageWear.setFont(self.RTLEsmallFont)
        self.advancedWearLabel = QLabel("Advanced Wear:      ")
        self.advancedWearLabel.setFont(self.RTLEsmallFont)
        self.labelTimeAdvancedWear = QLabel()
        self.labelTimeAdvancedWear.setFont(self.RTLEsmallFont)
        self.failureWearLabel = QLabel("Failure:                ")
        self.failureWearLabel.setFont(self.RTLEsmallFont)
        self.labelTimeFailureWear = QLabel()
        self.labelTimeFailureWear.setFont(self.RTLEsmallFont)
        self.RTLElabelsToShow.addRow(self.remainingTimeToLabel)
        self.RTLElabelsToShow.addRow(self.averageWearLabel, self.labelTimeAverageWear)
        self.RTLElabelsToShow.addRow(self.advancedWearLabel, self.labelTimeAdvancedWear)
        self.RTLElabelsToShow.addRow(self.failureWearLabel, self.labelTimeFailureWear)
        # Add the labels to show stuff to the HBox that holds the info, label, and graph
        self.RTLEInfoLabelGraph.addLayout(self.RTLElabelsToShow)

        x = [1]  # only one bar in the bar graph
        y = 30  # default value before actual plotting happens

        self.RTLEGraph = pg.PlotWidget()
        self.RTLEGraph.setContentsMargins(10, 0, 0, 0)  # someLayout.setContentsMargins(left, top, right, bottom)
        self.RTLEGraph.hideAxis("left")
        self.RTLEGraph.getAxis('bottom').setTicks([[(0, "Failure"), (1, "Advanced"), (2, "Average"), (3, "Good")]])
        self.RTLEGraph.hideAxis("bottom")
        self.curveRTLEGraph = pg.BarGraphItem(name="RLTEGraph", x=x, height=y, width=3, brush='d9d9d9')
        self.curveRTLEGraph.rotate(-90)  # horizontal graph
        self.RTLEGraph.addItem(self.curveRTLEGraph)

        # Add the graph to the HBox that holds the info, labels, and the graph
        self.RTLEInfoLabelGraph.addWidget(self.RTLEGraph)

        self.thirdRowRTLE.addLayout(self.RTLEInfoLabelGraph)

        self.groupRTLE = QGroupBox()
        self.groupRTLE.setStyleSheet("QGroupBox { background-color: #d9d9d9; border:1px solid #070707; }")
        self.groupRTLE.setLayout(self.thirdRowRTLE)
        self.mainLayout.addWidget(self.groupRTLE)


        ###############################################################################################################
        #                                                                                                             #
        #                            INITIALIZING ALL THE IMAGES FOR CTWM AND WHM WIDGETS                             #
        #                                                                                                             #
        ###############################################################################################################
    def initImgCTWM(self):
        """
        Add the grayed Good, Average, Advanced, and Failure images to the image/label/graph CTWMlayout
        :return: None
        """

        # Initialize the image's layout
        self.CTWMimageShow = QtWidgets.QVBoxLayout()
        self.CTWMimageShow.setContentsMargins(0, 0, 15, 0) # someLayout.setContentsMargins(left, top, right, bottom)

        self.labelFailureGrayCTWM = QLabel()
        # default image for when algorithm hasn't reached conclusion
        self.labelFailureGrayCTWM.setPixmap(self.images['imageFailureGrayCTWM'])
        self.CTWMimageShow.addWidget(self.labelFailureGrayCTWM)

        self.labelAdvancedGrayCTWM = QLabel()
        # default image for when algorithm hasn't reached conclusion
        self.labelAdvancedGrayCTWM.setPixmap(self.images['imageAdvancedGrayCTWM'])
        self.CTWMimageShow.addWidget(self.labelAdvancedGrayCTWM)

        self.labelAverageGrayCTWM = QLabel()
        # default image for when algorithm hasn't reached conclusion
        self.labelAverageGrayCTWM.setPixmap(self.images['imageAverageGrayCTWM'])
        self.CTWMimageShow.addWidget(self.labelAverageGrayCTWM)

        self.labelGoodGrayCTWM = QLabel()
        # default image for when algorithm hasn't reached conclusion
        self.labelGoodGrayCTWM.setPixmap(self.images['imageGoodGrayCTWM'])
        self.CTWMimageShow.addWidget(self.labelGoodGrayCTWM)

        # Add the image's layout to the image/label/graph layout
        self.CTWM_ImgLabelGraph.addLayout(self.CTWMimageShow)

    def initImgWHM(self):
        """
        Add the grayed Level 1, Level 2, Level 3, and Level 4 images to the image/label/graph WHM layout
        :return: None
        """

        self.WHMimageShow = QtWidgets.QVBoxLayout()
        self.WHMimageShow.setContentsMargins(0, 0, 15, 0)  # someLayout.setContentsMargins(left, top, right, bottom)

        self.labelLevelFourWHM = QLabel()
        # default image for when algorithm hasn't reached conclusion
        self.labelLevelFourWHM.setPixmap(self.images['imageLevelFourWHMgray'])
        self.WHMimageShow.addWidget(self.labelLevelFourWHM)

        self.labelLevelThreeWHM = QLabel()
        # default image for when algorithm hasn't reached conclusion
        self.labelLevelThreeWHM.setPixmap(self.images['imageLevelThreeWHMgray'])
        self.WHMimageShow.addWidget(self.labelLevelThreeWHM)

        self.labelLevelTwoWHM = QLabel()
        # default image for when algorithm hasn't reached conclusion
        self.labelLevelTwoWHM.setPixmap(self.images['imageLevelTwoWHMgray'])
        self.WHMimageShow.addWidget(self.labelLevelTwoWHM)

        self.labelLevelOneWHM = QLabel()
        # default image for when algorithm hasn't reached conclusion
        self.labelLevelOneWHM.setPixmap(self.images['imageLevelOneWHMgray'])
        self.WHMimageShow.addWidget(self.labelLevelOneWHM)

        self.WHM_ImgLabelGraph.addLayout(self.WHMimageShow)

        ###############################################################################################################
        #                                                                                                             #
        #                                        ALL UPDATE METHODS FOR THE WIDGETS                                   #
        #                                                                                                             #
        ###############################################################################################################
    @pyqtSlot(int)
    def updateCTWM(self, wear):
        """
        The real-part where threading takes place - Update the image according to the prediction
        :param wear: The prediction number - between 1 and 4
        :return: None
        """

        if wear == 1:
            self.labelGoodGrayCTWM.setPixmap(self.images['imageGoodGreenCTWM'])
            self.labelAverageGrayCTWM.setPixmap(self.images['imageAverageGrayCTWM'])
            self.labelAdvancedGrayCTWM.setPixmap(self.images['imageAdvancedGrayCTWM'])
            self.labelFailureGrayCTWM.setPixmap(self.images['imageFailureGrayCTWM'])

        elif wear == 2:
            self.labelGoodGrayCTWM.setPixmap(self.images['imageGoodGrayCTWM'])
            self.labelAverageGrayCTWM.setPixmap(self.images['imageAverageYellowCTWM'])
            self.labelAdvancedGrayCTWM.setPixmap(self.images['imageAdvancedGrayCTWM'])
            self.labelFailureGrayCTWM.setPixmap(self.images['imageFailureGrayCTWM'])

        elif wear == 3:
            self.labelGoodGrayCTWM.setPixmap(self.images['imageGoodGrayCTWM'])
            self.labelAverageGrayCTWM.setPixmap(self.images['imageAverageGrayCTWM'])
            self.labelAdvancedGrayCTWM.setPixmap(self.images['imageAdvancedOrangeCTWM'])
            self.labelFailureGrayCTWM.setPixmap(self.images['imageFailureGrayCTWM'])

        elif wear == 4:
            self.labelGoodGrayCTWM.setPixmap(self.images['imageGoodGrayCTWM'])
            self.labelAverageGrayCTWM.setPixmap(self.images['imageAverageGrayCTWM'])
            self.labelAdvancedGrayCTWM.setPixmap(self.images['imageAdvancedGrayCTWM'])
            self.labelFailureGrayCTWM.setPixmap(self.images['imageFailureRedCTWM'])

        self.outcomesCTWM = np.append(self.outcomesCTWM, wear)

        if self.outcomesCTWM.size > 0:
            elapsed = self.tmr.elapsed()/float(1000)
            self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "a")
            self.save_file.write("Time Elapsed: (" + str(elapsed)+" sec) - Tool Wear: "+str(wear)+", \n")
            self.save_file.close()
            self.dataCTWM.append({'x': elapsed, 'y': wear})
            self.CTWMx = [item['x'] for item in self.dataCTWM]
            self.CTWMy = [item['y'] for item in self.dataCTWM]
            self.CTWMx = np.asarray(self.CTWMx).flatten()
            self.CTWMy = np.asarray(self.CTWMy).flatten()
            self.curveCTWMGraph.setData(x=self.CTWMx, y=self.CTWMy)
            #self.save.clicked.connect(self.saveGraph(self.addressBox))

    @pyqtSlot(int)
    def updateWHM(self, hardnessLevel):
        """
        The real-part where threading takes place - Update the image according to the prediction
        :parhardnessLevel: The prediction number - between 1 and 4
        :return: None
        """

        if hardnessLevel == 1:
            self.labelLevelOneWHM.setPixmap(self.images['imageLevelOneWHMgreen'])
            self.labelLevelTwoWHM.setPixmap(self.images['imageLevelTwoWHMgray'])
            self.labelLevelThreeWHM.setPixmap(self.images['imageLevelThreeWHMgray'])
            self.labelLevelFourWHM.setPixmap(self.images['imageLevelFourWHMgray'])


        elif hardnessLevel == 2:
            self.labelLevelTwoWHM.setPixmap(self.images['imageLevelTwoWHMyellow'])
            self.labelLevelOneWHM.setPixmap(self.images['imageLevelOneWHMgray'])
            self.labelLevelThreeWHM.setPixmap(self.images['imageLevelThreeWHMgray'])
            self.labelLevelFourWHM.setPixmap(self.images['imageLevelFourWHMgray'])

        elif hardnessLevel == 3:
            self.labelLevelThreeWHM.setPixmap(self.images['imageLevelThreeWHMorange'])
            self.labelLevelOneWHM.setPixmap(self.images['imageLevelOneWHMgray'])
            self.labelLevelTwoWHM.setPixmap(self.images['imageLevelTwoWHMgray'])
            self.labelLevelFourWHM.setPixmap(self.images['imageLevelFourWHMgray'])

        elif hardnessLevel == 4:
            self.labelLevelFourWHM.setPixmap(self.images['imageLevelFourWHMred'])
            self.labelLevelOneWHM.setPixmap(self.images['imageLevelOneWHMgray'])
            self.labelLevelTwoWHM.setPixmap(self.images['imageLevelTwoWHMgray'])
            self.labelLevelThreeWHM.setPixmap(self.images['imageLevelThreeWHMgray'])

        self.outcomesWHM = np.append(self.outcomesWHM, hardnessLevel)

        if self.outcomesWHM.size > 0:
            elapsed = self.tmr.elapsed() / float(1000)
            self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "a")
            self.save_file.write("Time Elapsed: (" + str(elapsed) + " sec) - Hardness Level: "+str(hardnessLevel)+",\n")
            self.save_file.close()
            self.dataWHM.append({'x': elapsed, 'y': hardnessLevel})
            self.WHMx = [item['x'] for item in self.dataWHM]
            self.WHMy = [item['y'] for item in self.dataWHM]
            self.WHMx = np.asarray(self.WHMx).flatten()
            self.WHMy = np.asarray(self.WHMy).flatten()
            self.curveWHMGraph.setData(x=self.WHMx, y=self.WHMy)

        # Stuff for Verbose - Helpful for debugging
        if self.setPointsWHM.verbose > 0:
            if self.setPointsWHM.verbose > 0:
                print 'Receive Time: {:0.6f}ms | Pre-process + SVM Run Time: {:0.6f}ms | Total Run Time: {:0.6f}ms'.format(
                    (self.setPointsWHM.algo_time - self.setPointsWHM.receive_time) * 1000.,
                    (self.setPointsWHM.final_time - self.setPointsWHM.algo_time) * 1000.,
                    (time.time() - self.showtime) * 1000.)
                # reset Showtime
                self.showtime = time.time()
                # print ' Total Showtime: {:0.6f}ms \n \n'.format((time.time() - self.showtime) * 1000.)

    def updateRTLE(self):
        """
        Update the labels of the RTLE widget
        :return: None
        """
        x = [1]


        self.V = self.cuttingSpeed(diameter=float(self.radialDOC.text()),
                                   rpm=float(self.speed.text()))  # V: cutting speed

        self.toolLife = self.algoRTLE(V=self.V, d=float(self.radialDOC.text()),
                                      f=float(self.feed.text()),rpm=float(self.speed.text()),
                                      flute=float(self.flutes.text()))  # Calculate remaining tool life
        self.RTLEGraph.setXRange(0, self.toolLife) # Set the X-Range according to the remaining tool life

        self.timeAverageWear = self.toolLife - (0.5 * self.toolLife)
        self.timeAdvancedWear = self.timeAverageWear + (0.25 * self.toolLife)
        self.timeFailureWear = self.timeAdvancedWear + (0.25 * self.toolLife)

        advancedtime = self.timeFailureWear - self.timeAdvancedWear
        averagetime = self.timeFailureWear - self.timeAverageWear
        currentwidth = 3
        self.currentWear = pg.BarGraphItem(x=x, height=0, width=currentwidth)

        if self.outcomesCTWM.size > 0:
            if self.outcomesCTWM[-1] == 1:
                self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "a")
                self.save_file.write("\nRemaining Tool Life Estimation\n")
                self.save_file.write("Average: "+str(self.timeAverageWear)+" min, ")
                self.save_file.write("Advanced: "+str(self.timeAdvancedWear)+" min, ")
                self.save_file.write("Failure: "+str(self.timeFailureWear)+" min, \n")
                self.save_file.close()
                self.labelTimeAverageWear.setText(str(self.timeAverageWear))
                self.labelTimeAdvancedWear.setText(str(self.timeAdvancedWear))
                self.labelTimeFailureWear.setText(str(self.timeFailureWear))
                self.currentWear = pg.BarGraphItem(x=x, height=self.timeFailureWear, width=currentwidth,
                                                   brush=(54,183,41))
                self.RTLEGraph.setLabel("bottom", "Tool Life Remaining: 100%")

            elif self.outcomesCTWM[-1] == 2:
                self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "a")
                self.save_file.write("\nRemaining Tool Life Estimation\n")
                self.save_file.write("Average: N/A, ")
                self.save_file.write("Advanced: "+str(self.timeAdvancedWear)+" min, ")
                self.save_file.write("Failure: "+str(self.timeFailureWear)+" min \n")
                self.save_file.close()
                self.labelTimeAverageWear.setText("N/A")
                self.labelTimeAdvancedWear.setText(str(self.timeAdvancedWear))
                self.labelTimeFailureWear.setText(str(self.timeFailureWear))
                self.currentWear = pg.BarGraphItem(x=x, height=averagetime, width=currentwidth,
                                                   brush=(221,215,69))
                percent = str((averagetime/self.timeFailureWear)*100)
                self.RTLEGraph.setLabel("bottom", "Tool Life Remaining: "+percent+"%")

            elif self.outcomesCTWM[-1] == 3:
                self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "a")
                self.save_file.write("\nRemaining Tool Life Estimation\n")
                self.save_file.write("Average: N/A, ")
                self.save_file.write("Advanced: N/A, ")
                self.save_file.write("Failure: "+str(self.timeFailureWear)+" min \n")
                self.save_file.close()
                self.labelTimeAverageWear.setText("N/A")
                self.labelTimeAdvancedWear.setText("N/A")
                self.labelTimeFailureWear.setText(str(self.timeFailureWear))
                self.currentWear = pg.BarGraphItem(x=x, height=advancedtime, width=currentwidth,
                                                   brush=(255,188,73))
                percent = str((advancedtime/self.timeFailureWear)*100)

                self.RTLEGraph.setLabel("bottom", "Tool Life Remaining: "+percent+"%")


            elif self.outcomesCTWM[-1] == 4:
                self.save_file = open(os.path.join(args.parent_img_path, self.save_file_name), "a")
                self.save_file.write("\nRemaining Tool Life Estimation\n")
                self.save_file.write("Average: N/A, ")
                self.save_file.write("Advanced: N/A, ")
                self.save_file.write("Failure: N/A \n")
                self.save_file.close()
                self.labelTimeAverageWear.setText("N/A")
                self.labelTimeAdvancedWear.setText("N/A")
                self.labelTimeFailureWear.setText("N/A")
                self.currentWear = pg.BarGraphItem(x=x, height=self.timeFailureWear/80, width=currentwidth,
                                                   brush=(253,94,91))
                self.RTLEGraph.setLabel("bottom", "Tool Life Remaining: 0%")

        # layered bar graph to show differences in good, average, advanced, failure
        self.RTLEGraph.getAxis('bottom').setTicks([[(0, "Failure"),
                                                    (advancedtime, "Advanced"),
                                                    (averagetime, "Average"),
                                                    (self.timeFailureWear, "Good")]])

        self.RTLEGraph.clear()
        self.curveRTLEGraphTotal = pg.BarGraphItem(x=x, height=self.timeFailureWear, width=3, brush="d9d9d9")
        self.curveRTLEGraphTotal.rotate(-90)
        self.currentWear.rotate(-90)
        self.RTLEGraph.addItem(self.curveRTLEGraphTotal)
        self.RTLEGraph.addItem(self.currentWear)

        ###############################################################################################################
        #                                                                                                             #
        #                                        SMALL COMPUTATIONS, ALGORITHMS, AND CALCULATIONS                     #
        #                                                                                                             #
        ###############################################################################################################
    def cuttingSpeed(self, diameter, rpm):
        """
        Return V, which is cutting speed in ft/min
        :param diameter: The radian DOC in inches
        :param rpm: Speed
        :return: V: cutting speed in ft/min
        """
        return (math.pi * diameter * rpm)/12

    def algoRTLE(self, V, d, f, rpm, flute):
        """
        Remaining Tool Life Estimation algorithm
        :param V: Cutting speed in ft/min
        :param d: Depth of cut in in
        :param f: Feed rate in in/min
        :return:
        """
        return math.pow(100, (1/0.15)) * math.pow(V, (-1/0.15)) * math.pow((d*25.4), -1) * math.pow(((f/(rpm * flute)) *
                                                                                                     25.4), (-0.1/0.15))

class Algorithm(QThread):
    """
    Class to run the actual algorithm, which is taking in audio data and refers to the PKL file for a prediction number
    """
    finished = pyqtSignal(int)

    # Set variables for PyAudio
    CHANNELS = 1
    RATE = 44100
    # Instantiate PyAudio
    p = None
    # Instantiate a NumPy array
    audio = np.array([])
    # For checking stop button
    stop = QTimer()
    # For opening audio stream
    stream = None

    def __init__(self, clf_path, window_length=0.05, rate=44100, verbose=0):
        """
        Initialize the algorithm
        :param clf_path: Path of the PKL file
        :param window_length: Length of the amount of data to be read
        :param rate: Rate at which information is stored
        :param verbose: Used for printing debug data
        """
        self.verbose = verbose
        self.clf = joblib.load(clf_path)
        self.rate = rate
        self.count = int(np.floor(self.rate * window_length))
        self.audio = deque(maxlen=self.count)
        self.t = None
        self.window_length = window_length

        self.comparableAudio = np.array([])

        QThread.__init__(self)

    def run(self):
        """
        Algorithm that initializes PyAudio and opens stream
        :return: None
        """
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paFloat32, channels=self.CHANNELS, rate=self.RATE, input=True,
                                  output=False, stream_callback=self.callback)
        self.stream.start_stream()
        self.stop.setSingleShot(True)
        self.stop.start()

    def callback(self, in_data, *kwargs):
        """
        Call backfunction to execute in a while loop for stream
        :param in_data: In data Stream
        :param kwargs: Extra arguments coming from c
        allback by stream
        :return: audio data
        """
        self.receive_time = time.time()
        audio_data = np.fromstring(in_data, dtype=np.float32)
        self.audio.extend(audio_data)
        # if the queue is full then run SVM
        if len(self.audio) == self.count:
            self.algo_time = time.time()
            self.algo()
            self.final_time = time.time()
        self.comparableAudio = np.append(self.comparableAudio, audio_data)
        return audio_data, pyaudio.paContinue

    def stopit(self):
        """
        Algorithm that terminates PyAudio and closes the stream
        :return: None
        """

        self.stop.stop()
        self.stream.close()
        self.p.terminate()
        self.p = None

        print("Recording terminated!")


    def algo(self):
        """
        Algorithm that takes in audio data and refers to the PKL file. Accordingly, emits the number that is the wear
        status
        :return: None
        """
        audio = np.array([self.audio.popleft() for _ in range(self.count)])
        # Run Classifier
        wav_data = np.abs(np.fft.rfft(audio.flatten()))
        if len(wav_data) > 0:
            pred = self.clf.predict(np.expand_dims(wav_data, 0))
            if self.verbose > 1:
                print('The prediction is : ' + str(pred))
            self.finished.emit(int(pred[-1]))
        else:
            self.finished.emit(0)

class Dialog(QDialog):
    """
    Screen where user inputs data about tool.
    """
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, parent_img_path):
        """
        initializing the screen
        """
        super(Dialog, self).__init__()

        self.parent_img_path = parent_img_path
        self.windowLogoPath = os.path.join(self.parent_img_path, "sss_Logo.jpg")
        self.ssspath = QPixmap(os.path.join(self.parent_img_path, "sss_Logo.jpg"))
        self.logo = QtGui.QIcon(self.windowLogoPath)
        # Set a logo for the program
        self.setWindowIcon(self.logo)
        # Specifically for Windows
        if sys.platform == 'win32':
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.windowLogoPath)

        self.createFormGroupBox()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Machine and Tool Settings")

        self.secondScreen = None

    def accept(self):
        self.show1 = self.cb1.isChecked()
        self.show2 = self.cb2.isChecked()
        self.show3 = self.cb3.isChecked()
        self.tool_type_text = str(self.tool_type.currentText())
        self.tool_diameter_num = str(self.tool_diameter.value())
        self.flutes_num = str(self.flutes.value())
        self.material_text = str(self.material.currentText())
        self.coating_text = str(self.coating.currentText())
        self.cutting_type_text = str(self.cutting_type.currentText())
        self.wpmaterial_text = str(self.wpmaterial.currentText())
        self.heat_text = str(self.heat.currentText())

        ctwmGraphPoints = Algorithm(clf_path=args.clf_path_CTWM, window_length=args.window_length, rate=args.rate)
        whmGraphPoints = Algorithm(clf_path=args.clf_path_WHM, window_length=args.window_length, rate=args.rate)

        self.secondScreen = UI(showCTWM=self.show1, showWHM=self.show2, showRTLE=self.show3,
                               algorithmCTWM=ctwmGraphPoints, algorithmWHM=whmGraphPoints,
                               tool_type_text=self.tool_type_text, material_text= self.material_text,
                               flutes_text=self.flutes_num, coating_text=self.coating_text,
                               cutting_type_text=self.cutting_type_text, wpmaterial_text=self.wpmaterial_text,
                               heat_text=self.heat_text, tool_diameter_num=self.tool_diameter_num,
                               parent_img_path=args.parent_img_path)
        self.secondScreen.show()

    def createFormGroupBox(self):
        layout = QHBoxLayout()

        # checkboxes for which windows will open
        self.cb1 = QCheckBox("Tool Wear Window")
        self.cb1.setCheckState(True)  # automatically checked
        self.cb2 = QCheckBox("Workpiece Hardness Window")
        self.cb3 = QCheckBox("Remaining Tool Life Window")

        self.formGroupBox = QGroupBox("Settings")
        layout1 = QFormLayout()

        self.ssspic = QLabel()
        pixmap = QtGui.QPixmap(self.ssspath)
        self.ssspic_scaled = pixmap.scaled(200, 200)
        self.ssspic.setPixmap(self.ssspic_scaled)

        layout1.addRow(self.ssspic)
        layout1.addRow(self.cb1)
        layout1.addRow(self.cb2)
        layout1.addRow(self.cb3)

        layout2 = QFormLayout()
        layout2.addRow(QLabel("Cutting Tool Settings"))

        self.tool_type = QComboBox()
        tool_type_list = ["End Milling", "Drill", "Slab", "Slit", "Gear Cutter", "Fly Cutter"]
        self.tool_type.clear()
        self.tool_type.addItems(tool_type_list)
        layout2.addRow(QLabel("Tool Type:"), self.tool_type)

        self.tool_diameter = QDoubleSpinBox()
        self.tool_diameter.setSingleStep(0.005)
        self.tool_diameter.setDecimals(3)
        self.tool_diameter.setSuffix("in")
        layout2.addRow(QLabel("Tool Diameter:"), self.tool_diameter)

        #Will this get pushed?

        self.flutes = QDoubleSpinBox()
        self.flutes.setSingleStep(1)
        self.flutes.setMinimum(1)
        self.flutes.setDecimals(0)
        layout2.addRow(QLabel("Flutes:"), self.flutes)

        self.material = QComboBox()
        material_list = ["HSS (High Speed Steel)", "Carbide", "Cobalt"]
        self.material.clear()
        self.material.addItems(material_list)
        layout2.addRow(QLabel("Material:"), self.material)

        self.coating = QComboBox()
        coating_list = ["Titanium Nitrate", "Titanium Carbonitride", "Titanim Aluminum Nitride", "Zirconium Nitride",
                        "Diamond", "Black Oxide", "Non-Coated"]
        self.coating.clear()
        self.coating.addItems(coating_list)
        layout2.addRow(QLabel("Coating:"), self.coating)

        self.cutting_type = QComboBox()
        ctlst = ["End Mill", "Slot Cut", "Side Mill", "Slit Cut", "Angle Mill", "Plain Mill", "Form Mill"]
        self.cutting_type.clear()
        self.cutting_type.addItems(ctlst)
        layout2.addRow(QLabel("Cutting Type:"), self.cutting_type)

        self.wpmaterial = QComboBox()
        wpmaterial_list = ["Aluminum", "Low-Carbon Steel", "High-Carbon Steel", "Plastic", "Alloy Steel", "Titanium",
                           "Brass", "Copper", "Stainless Steel", "8620 Alloy Carbon Steel"]
        self.wpmaterial.clear()
        self.wpmaterial.addItems(wpmaterial_list)
        layout2.addRow(QLabel("Workpiece Material:"), self.wpmaterial)

        self.heat = QComboBox()
        heat_list = ["Normalized", "Stress Relieves", "Hardened", "Tempered", "Cure Hardened"]
        self.heat.clear()
        self.heat.addItems(heat_list)
        layout2.addRow(QLabel("Heat Treatment:"), self.heat)

        layout.addLayout(layout1)
        layout.addLayout(layout2)

        self.formGroupBox.setLayout(layout)

def my_exception_hook(exctype, value, traceback):
    """
    Overrides the normal exception stuff that PyCharm prints out. Essentially used for PyQt
    :param exctype: Execution Type
    :param value: The type of error
    :param traceback: Traceback data
    :return: None
    """
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Smart Sensing System')
    parser.add_argument("--clf_path_CTWM", help='Classifier path', type=str, default='')
    parser.add_argument("--clf_path_WHM", help='Classifier path', type=str, default='')
    parser.add_argument("--parent_img_path", help='Parent Directory of display images', type=str, default='')
    parser.add_argument('--window_length', help='Window length used to train Algorithm', type=float, default=0.5)
    parser.add_argument('--rate', help='Sampling rate of audio', type=float, default=44100)
    args = parser.parse_args()

    app = QApplication(sys.argv)
    dialog = Dialog(args.parent_img_path)
    dialog.show()

    app.setWindowIcon(QIcon(os.path.join(args.parent_img_path, "sss_Logo.jpg")))

    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook
    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook
    # Prints actual traceback of errors
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
