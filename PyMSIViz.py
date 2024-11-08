import warnings
warnings.filterwarnings('ignore')
import matplotlib
import struct
import copy
import csv
import time
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from numpy import genfromtxt

from pyimzml.ImzMLParser import ImzMLParser
from bisect import bisect_left, bisect_right

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon

import pyautogui
from datetime import datetime
from matplotlib.figure import Figure

if QtCore.qVersion() >= "5.":
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

# class TaskThread(QtCore.QThread):
#     taskFinished = QtCore.pyqtSignal()
#     def run(self):
#         time.sleep(1)
#         self.taskFinished.emit()
        
class progressBar_Thread(QThread):
    bar_signal = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(100):
            time.sleep(0.4)
            self.bar_signal.emit(i)

class Ui_MplMainWindow(object):
    def setupUi(self, MplMainWindow):
        MplMainWindow.setObjectName("MplMainWindow")
        #MplMainWindow.resize(1000, 700)
        #MplMainWindow.setFixedSize(1000,700)
        MplMainWindow.setFixedSize(950, 920)
        #MplMainWindow.move(125,125)
        
        qtRectangle = MplMainWindow.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        MplMainWindow.move(qtRectangle.topLeft())
        
        self.centralwidget = QtWidgets.QWidget(MplMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setFixedSize(950,700)
        
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.setWindowIcon(QIcon('bIms.png'))

        
        self.spectrum =MplWidgetTest(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spectrum.sizePolicy().hasHeightForWidth())
        self.spectrum.setSizePolicy(sizePolicy)
        self.spectrum.setObjectName("spectrum")
        self.spectrum.setMinimumSize(300, 250)
        self.spectrum.setMaximumSize(1200, 1050)
        self.gridLayout_2.addWidget(self.spectrum, 1, 0, 1, 1)
        
        
        self.mpl = MplWidgetTest(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mpl.sizePolicy().hasHeightForWidth())
        self.mpl.setSizePolicy(sizePolicy)
        self.mpl.setObjectName("mpl")
        self.gridLayout_2.addWidget(self.mpl, 0, 0, 1, 1)
        
       
        self.groupBox = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox.setMaximumSize(QtCore.QSize(500, 16777215))
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        
        
        self.setAutoFillBackground(True)
        self.k = self.palette()
        self.k.setColor(self.backgroundRole(),Qt.darkGray) 
        self.setPalette(self.k) 
  
        
        #LOAD DATA BUTTON
        self.buttonDrawDate = QtWidgets.QPushButton(self.groupBox)
        self.buttonDrawDate.setMaximumSize(QtCore.QSize(125, 16777215))
        self.buttonDrawDate.setObjectName("buttonDrawDate")
        self.gridLayout.addWidget(self.buttonDrawDate, 0, 0, 1, 1)
        self.buttonDrawDate.setStyleSheet("QPushButton { border: 0.75px solid #8f8f91;    border-radius: 5px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 80px;}"
                                               "QPushButton:: pressed { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,  stop: 0 #dadbde, stop: 1 #f6f7fa);}"
                                                   "QPushButton:flat {  border: none; /* no border for a flat push button */}"
                                                       "QPushButton:default { border-color: navy; /* make the default button prominent */ }")


        #LOAD DATA FİLENAME
        self.viewFileName = QLineEdit()
        self.viewFileName.setReadOnly(True)
        self.viewFileName.setMaximumSize(QtCore.QSize(125, 16777215))
        self.viewFileName.setObjectName("viewFileName")
        self.gridLayout.addWidget(self.viewFileName, 0, 1, 1, 1)
        self.viewFileName.setStyleSheet("QLineEdit{ border-width: 0.75px; border-style: solid; border-color: gray ;border-radius:15px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 150px;}" )

        
        
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 1, 1, 1)
        MplMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MplMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 628, 21))
        self.menubar.setObjectName("menubar")
        MplMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MplMainWindow)
        self.statusbar.setObjectName("statusbar")
        MplMainWindow.setStatusBar(self.statusbar)

        
        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)
        
        menus = {
            'File': [
                ('Load File', 'l', 'Load application', self.openFileNameDialog),
                ('New File', 'N', 'New application', [self.clear, self.openFileNameDialog]),
                ('Restart', 'Ctrl+R', 'Restart application', self.clear),
                ('Exit', 'Ctrl+Q', 'Exit application', self.close)
            ],
            'Tool': [
                ('Spectrum', 'S', 'Spectrum Processing', self.spectrumProcessing),
                ('Image', 'P', 'Image Processing', self.DataProcessing),
                ('Multi Image', 'M', 'Multi Image Processing', self.DataProcessing2),
                ('BoxPlot', 'B', 'Box application', self.boxplot_),
                ('Multi BoxPlot', 'Ctrl+Alt+P', 'Multi Box application', self.boxplot_2)
            ],
            'Help': []  # Help menüsü için öğeleri buraya ekleyebilirsiniz
        }
        
        for menu_name, actions in menus.items():
            menu = mainMenu.addMenu(menu_name)
            for action in actions:
                action_name, shortcut, status_tip, function = action
                menu_action = QAction(action_name, self)
                menu_action.setShortcut(shortcut)
                menu_action.setStatusTip(status_tip)
                if isinstance(function, list):
                    for f in function:
                        menu_action.triggered.connect(f)
                else:
                    menu_action.triggered.connect(function)
                menu.addAction(menu_action)

        self.onlyInt = QDoubleValidator()
        self.targetALabel = QLabel("target A:")
        self.targetA_textbox = QLineEdit()
        self.targetA_textbox.setValidator(self.onlyInt)
        self.targetALabel.setMaximumSize(QtCore.QSize(125, 16777215))
        self.targetALabel.setObjectName("targetALabel")
        self.gridLayout.addWidget(self.targetALabel, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.targetA_textbox, 1, 1, 1, 1)
        self.targetALabel.setStyleSheet("QLabel { color: black ; fontName='Times-Italic';text-align: center ; }")
        self.targetA_textbox.setStyleSheet("QLineEdit{ border-width: 1px; border-style: solid; border-color: gray; border-radius: 15px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 100px;}" )
        
        self.widthLabel = QLabel("Peak width TOLa:")
        self.width_textbox = QLineEdit()
        self.width_textbox.setValidator(self.onlyInt)
        self.widthLabel.setMaximumSize(QtCore.QSize(125, 16777215))
        self.widthLabel.setObjectName("widthLabel")
        self.gridLayout.addWidget(self.widthLabel, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.width_textbox, 2, 1, 1, 1)
        self.widthLabel.setStyleSheet("QLabel { color: black ; fontName='Times-Italic';text-align: center ; }")
        self.width_textbox.setStyleSheet("QLineEdit{ border-width: 1px; border-style: solid; border-color: gray ;border-radius: 15px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 100px;}" )


        self.zLabel = QLabel("z:")
        self.z_textbox = QLineEdit()
        self.z_textbox.setValidator(self.onlyInt)
        self.zLabel.setMaximumSize(QtCore.QSize(100, 16777215))
        self.zLabel.setObjectName("targetCLabel")
        self.gridLayout.addWidget(self.zLabel, 3, 0, 1, 1)
        self.gridLayout.addWidget(self.z_textbox, 3, 1, 1, 1)
        self.zLabel.setStyleSheet("QLabel { color: black ; fontName='Times-Italic';text-align: center ; }")
        self.z_textbox.setStyleSheet("QLineEdit{ border-width: 0.75px; border-style: solid; border-color: gray; border-radius: 15px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 100px;}" )

       
        self.targetBLabel = QLabel("target B:")
        self.targetB_textbox = QLineEdit()
        self.targetB_textbox.setValidator(self.onlyInt)
        self.targetBLabel.setMaximumSize(QtCore.QSize(100, 16777215))
        self.targetBLabel.setObjectName("targetBLabel")
        self.gridLayout.addWidget(self.targetBLabel, 4, 0, 1, 1)
        self.gridLayout.addWidget(self.targetB_textbox,4, 1, 1, 1)
        self.targetBLabel.setStyleSheet("QLabel { color: black ; fontName='Times-Italic';text-align: center ; }")
        self.targetB_textbox.setStyleSheet("QLineEdit{ border-width: 0.75px; border-style: solid; border-color: gray;border-radius:15px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 100px;}" )

        
        self.widthLabelb = QLabel("Peak width TOLb:")
        self.width_textboxb = QLineEdit()
        self.width_textboxb.setValidator(self.onlyInt)
        self.widthLabelb.setMaximumSize(QtCore.QSize(100, 16777215))
        self.widthLabel.setObjectName("widthLabelb")
        self.gridLayout.addWidget(self.widthLabelb, 5, 0, 1, 1)
        self.gridLayout.addWidget(self.width_textboxb, 5, 1, 1, 1)
        self.widthLabelb.setStyleSheet("QLabel { color: black ; fontName='Times-Italic';text-align: center ; }")
        self.width_textboxb.setStyleSheet("QLineEdit{ border-width: 0.75px; border-style: solid; border-color: gray;border-radius: 15px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 100px;}" )
                   
        
        self.targetCLabel = QLabel("target C:")
        self.targetC_textbox = QLineEdit()
        self.targetC_textbox.setValidator(self.onlyInt)
        self.targetCLabel.setMaximumSize(QtCore.QSize(100, 16777215))
        self.targetCLabel.setObjectName("targetCLabel")
        self.gridLayout.addWidget(self.targetCLabel, 6, 0, 1, 1)
        self.gridLayout.addWidget(self.targetC_textbox, 6, 1, 1, 1)
        self.targetCLabel.setStyleSheet("QLabel { color: black ; fontName='Times-Italic';text-align: center ; }")
        self.targetC_textbox.setStyleSheet("QLineEdit{ border-width: 0.75px; border-style: solid; border-color: gray;border-radius: 15px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width:100px;}" )
            
        
        self.widthLabelc = QLabel("TOLc:")
        self.width_textboxc = QLineEdit()
        self.width_textboxc.setValidator(self.onlyInt)
        self.widthLabelc.setMaximumSize(QtCore.QSize(100, 16777215))
        self.widthLabelc.setObjectName("widthLabelc")
        self.gridLayout.addWidget(self.widthLabelc, 7, 0, 1, 1)
        self.gridLayout.addWidget(self.width_textboxc,7, 1, 1, 1)
        self.widthLabelc.setStyleSheet("QLabel { color: black ; fontName='Times-Italic';text-align: center ; }")
        self.width_textboxc.setStyleSheet("QLineEdit{ border-width: 0.75px; border-style: solid; border-color: gray;border-radius: 15px; background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 110px;}" )


        self.buttonSpectrum = QtWidgets.QPushButton(self.groupBox)
        self.buttonSpectrum.setMaximumSize(QtCore.QSize(140, 16777215))
        self.buttonSpectrum.setObjectName("buttonSpectrum")
        self.gridLayout.addWidget(self.buttonSpectrum, 10, 0, 1, 1)  
        self.buttonSpectrum.setStyleSheet("QPushButton {border: 2px solid #8f8f91; border-radius: 0.5px;  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 140px;  min-height: 20px; font-size: 12px; text-align: center;}"
                                           "QPushButton:: pressed { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,  stop: 0 #dadbde, stop: 1 #f6f7fa);}"
                                                  "QPushButton:flat {  border: none; /* no border for a flat push button */}"
                                                      "QPushButton:default { border-color: navy; /* make the default button prominent */ }")
                               
                 
        self.buttonErase = QtWidgets.QPushButton(self.groupBox)
        self.buttonErase.setMaximumSize(QtCore.QSize(125, 16777215))
        self.buttonErase.setObjectName("buttonErase")
        self.gridLayout.addWidget(self.buttonErase, 11, 0, 1, 1)
        self.buttonErase.setStyleSheet("QPushButton {border: 2px solid #8f8f91; border-radius: 0.5px;  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 140px;  min-height: 20px; font-size: 12px; text-align: center;}"
                                           "QPushButton:: pressed { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,  stop: 0 #dadbde, stop: 1 #f6f7fa);}"
                                                  "QPushButton:flat {  border: none; /* no border for a flat push button */}"
                                                      "QPushButton:default { border-color: navy; /* make the default button prominent */ }")
                               
                          
        self.buttonErase2 = QtWidgets.QPushButton(self.groupBox)
        self.buttonErase2.setMaximumSize(QtCore.QSize(125, 16777215))
        self.buttonErase2.setObjectName("buttonErase2")
        self.gridLayout.addWidget(self.buttonErase2, 11, 1, 1, 1)
        self.buttonErase2.setStyleSheet("QPushButton {border: 2px solid #8f8f91; border-radius: 0.5px;  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 140px;  min-height: 20px; font-size: 12px; text-align: center;}"
                                           "QPushButton:: pressed { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,  stop: 0 #dadbde, stop: 1 #f6f7fa);}"
                                                  "QPushButton:flat {  border: none; /* no border for a flat push button */}"
                                                      "QPushButton:default { border-color: navy; /* make the default button prominent */ }")
                                              
        self.colormapLabel = QLabel("Colormap : ")
        self.colormapLabel.setMaximumSize(QtCore.QSize(100, 16777215))
        self.colormapLabel.setObjectName("targetCLabel")
        self.gridLayout.addWidget(self.colormapLabel, 8, 0, 1, 1)
        self.colormapLabel.setStyleSheet("QLabel { color: black ; fontName='Times-Italic';text-align: center ; }")
        
        self.cb = QComboBox()
        self.cb.setMaximumSize(QtCore.QSize(125, 16777215))
        self.cb.setObjectName("Colormap")
        self.gridLayout.addWidget(self.cb, 8, 1, 1, 1)
        
        colormap_names = ["viridis", "jet", "hot", "copper", "inferno", "Spectral", 
                          "cividis", "magma", "coolwarm", "pink", "plasma", "binary", 
                          "bone", "gray"]
        
        self.cb.addItems(colormap_names) 
        
        #self.cb.addItems(["seismic", "twilight_shifted", "gist_rainbow", "cubehelix", "gnuplot","spring", "summer", "autumn", "winter", "pink", "plasma", "hsv", "rainbow", "cubehelix"])
        
        self.interpolLabel = QLabel("Interpolation : ")
        self.interpolLabel.setMaximumSize(QtCore.QSize(100, 16777215))
        self.interpolLabel.setObjectName("targetCLabel")
        self.gridLayout.addWidget(self.interpolLabel, 9, 0, 1, 1)
        self.interpolLabel.setStyleSheet("QLabel { color: black ; fontName='Times-Italic';text-align: center ; }")
        
        self.cb2 = QComboBox()
        self.cb2.setMaximumSize(QtCore.QSize(125, 16777215))
        self.cb2.setObjectName("Interpoli")
        self.gridLayout.addWidget(self.cb2, 9, 1, 1, 1)
        interpolation_options = ["nearest", "hanning", "bicubic", "bilinear"]
        self.cb2.addItems(interpolation_options)
        
        
       
        self.boxplot = QtWidgets.QPushButton(self.groupBox)
        self.boxplot.setMaximumSize(QtCore.QSize(125, 16777215))
        self.boxplot.setObjectName("boxplot")
        self.gridLayout.addWidget(self.boxplot, 12, 0, 1, 1)
        self.boxplot.setStyleSheet("QPushButton {border: 2px solid #8f8f91; border-radius: 0.5px;  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 140px;  min-height: 20px; font-size: 12px; text-align: center;}"
                                           "QPushButton:: pressed { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,  stop: 0 #dadbde, stop: 1 #f6f7fa);}"
                                                  "QPushButton:flat {  border: none; /* no border for a flat push button */}"
                                                      "QPushButton:default { border-color: navy; /* make the default button prominent */ }")
                               
        
        self.boxplot2 = QtWidgets.QPushButton(self.groupBox)
        self.boxplot2.setMaximumSize(QtCore.QSize(125, 16777215))
        self.boxplot2.setObjectName("boxplot2")
        self.gridLayout.addWidget(self.boxplot2, 12, 1, 1, 1)
        self.boxplot2.setStyleSheet("QPushButton {border: 2px solid #8f8f91; border-radius: 0.5px;  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 140px;  min-height: 20px; font-size: 12px; text-align: center;}"
                                           "QPushButton:: pressed { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,  stop: 0 #dadbde, stop: 1 #f6f7fa);}"
                                                  "QPushButton:flat {  border: none; /* no border for a flat push button */}"
                                                      "QPushButton:default { border-color: navy; /* make the default button prominent */ }")
                               
           
        self.clearButton=QPushButton("Clear")
        self.clearButton.clicked.connect(self.clear)
        self.gridLayout.addWidget(self.clearButton,14, 0, 1, 1)     
        self.clearButton.setStyleSheet("QPushButton {border: 2px solid #8f8f91; border-radius: 0.5px;  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 140px;  min-height: 20px; font-size: 12px; text-align: center;}"
                                           "QPushButton:: pressed { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,  stop: 0 #dadbde, stop: 1 #f6f7fa);}"
                                                  "QPushButton:flat {  border: none; /* no border for a flat push button */}"
                                                      "QPushButton:default { border-color: navy; /* make the default button prominent */ }")                                       
        
        self.closeButton=QPushButton("Close")
        self.closeButton.clicked.connect(self.close)
        self.gridLayout.addWidget(self.closeButton,14, 1, 1, 1)
        self.closeButton.setStyleSheet("QPushButton {border: 2px solid #8f8f91; border-radius: 0.5px;  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 140px;  min-height: 20px; font-size: 12px; text-align: center;}"
                                          "QPushButton:: pressed { background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,  stop: 0 #dadbde, stop: 1 #f6f7fa);}"
                                                 "QPushButton:flat {  border: none; /* no border for a flat push button */}"
                                                     "QPushButton:default { border-color: navy; /* make the default button prominent */ }")
                              
       
        
        self.progressBar = QProgressBar()

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

        self.progressBar.setRange(0,1)
        # self.myLongTask = TaskThread()

        self.progressBar.setMinimumSize(QtCore.QSize(125, 16777215))
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar,10, 1, 1, 1) 
        self.progressBar.setStyleSheet  ( "QProgressBar  { border: 2px solid #8f8f91; border-radius: 0.5px;  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f6f7fa, stop: 1 #dadbde); min-width: 140px;  min-height: 20px; font-size: 12px; text-align: center;}"
                                             " QProgressBar::chunk { background-color: #5f9ea0 ;  width: 6px;  margin: 0.5px;}")
         

        self.retranslateUi(MplMainWindow)
        QtCore.QMetaObject.connectSlotsByName(MplMainWindow)

    def retranslateUi(self, MplMainWindow):
        _translate = QtCore.QCoreApplication.translate
        MplMainWindow.setWindowTitle(_translate("MplMainWindow", "PyMSIViz"))
        self.groupBox.setTitle(_translate("MplMainWindow", "Settings"))
        self.buttonDrawDate.setText(_translate("MplMainWindow", "Load Data File"))
        self.buttonSpectrum.setText(_translate("MplMainWindow", "Spectrum Processing"))
        self.buttonErase.setText(_translate("MplMainWindow", "Image Processing"))
        self.buttonErase2.setText(_translate("MplMainWindow", "Multi Image Processing"))
        #self.closeButton.setText(_translate("MplMainWindow", "CLOSE"))
  
        # self.histogram.setText(_translate("MplMainWindow", "Histogram"))
       
        self.boxplot.setText(_translate("MplMainWindow", "Box Plot"))
        self.boxplot2.setText(_translate("MplMainWindow", "Multi Box Plot"))
        self.targetALabel.setText(_translate("MplMainWindow","m/z value 1 :"))
        self.widthLabel.setText(_translate("MplMainWindow","tol 1         :"))
        self.targetBLabel.setText(_translate("MplMainWindow","m/z value 2  :"))
        self.widthLabelb.setText(_translate("MplMainWindow","tol 2          :"))
        self.targetCLabel.setText(_translate("MplMainWindow","m/z value 3 :"))
        self.widthLabelc.setText(_translate("MplMainWindow","tol 3          :"))
        self.zLabel.setText(_translate("MplMainWindow","z                 :"))
 
class MplCanvas(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self):
        # setup Matplotlib Figure and Axis
        self.fig = Figure()
        self.fig.set_facecolor("#f6f7fa")
        self.colorbar = self.fig.add_axes([100, 100, 800, 800])                              
        self.ax = self.fig.add_subplot()
        self.ax.set_facecolor("#f6f7fa")

        # initialization of the canvas
        FigureCanvas.__init__(self, self.fig)
        # we define the widget as expandable
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        # notify the system of updated policy
        FigureCanvas.updateGeometry(self)
        
class MplWidgetTest(QWidget):
    """Widget defined in Qt Designer"""
    
    def __init__(self, parent = None):
        # initialization of Qt MainWindow widget
        QWidget.__init__(self, parent)
        # set the canvas to the Matplotlib widget
        self.canvas = MplCanvas()
        # create a NavigatioToolbar
        self.ntb=NavigationToolbar(self.canvas,self)
        self.ntb.setStyleSheet("QToolBar {min-height: 20px; font-size: 20px; }")
        self.ntb.setIconSize(QSize(20, 20))        
        
        # create a vertical box layout
        self.vbl = QVBoxLayout()
        
        # add NavigationToolBar to vertical box
        self.vbl.addWidget(self.ntb)
        self.setLayout(self.vbl)
        
        # add mpl widget to vertical box
        self.vbl.addWidget(self.canvas)

        # set the layout to th vertical box
        self.setLayout(self.vbl)



class DesignerMainWindow(QMainWindow, Ui_MplMainWindow):
    def __init__(self, parent = None):
        super(DesignerMainWindow, self).__init__(parent)
        self.setupUi(self)
        # connect the signals with the slots
        self.buttonDrawDate.clicked.connect(self.openFileNameDialog)
        self.buttonSpectrum.clicked.connect(self.spectrumProcessing)

        self.buttonErase.clicked.connect(self.DataProcessing)
        self.buttonErase2.clicked.connect(self.DataProcessing2)

        # self.histogram.clicked.connect(self.histogram_)
        self.boxplot.clicked.connect(self.boxplot_)
        self.boxplot2.clicked.connect(self.boxplot_2)

        self.clearButton.clicked.connect(self.clear)
        
        self.imzml_filename= None
        # self.colormap = colormap

    def onStart(self): 
        self.progressBar.setRange(0,0)
        self.myLongTask.start()

    def output_convert(self):
        #very long process to convert a txt file to excel
        pass

    def openFileNameDialog(self):
        self.viewFileName.clear()
        
        self.mpl.canvas.ax.clear()
        self.spectrum.canvas.ax.clear()
        self.mpl.canvas.draw()
        self.spectrum.canvas.draw()
                
        self.targetA_textbox.clear()
        self.width_textbox.clear()
        self.z_textbox.clear()
        self.targetB_textbox.clear()
        self.width_textboxb.clear()
        self.targetC_textbox.clear()
        self.width_textboxc.clear()
        self.progressBar.setValue(0)   

        try:
            if self.progressBar_Thread.isRunning():
                self.progressBar_Thread.terminate()
            if self.data_Processing.isRunning():
                self.data_Processing.terminate()
        except: pass
    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.imzml_filename, _ = QFileDialog.getOpenFileName(self,"Open file", os.getcwd() ,"Data Files(*.imzMl);;All Files (*)", options=options)
        self.viewFileName.setText(os.path.basename(self.imzml_filename))
        
    def spectrumProcessing(self):
        self.progressBar.setValue(0)   
        
        try:
            if self.progressBar_Thread.isRunning():
                self.progressBar_Thread.terminate()
            if self.data_Processing.isRunning():
                self.data_Processing.terminate()
        except: pass
       
        mzs_arr=[]
        int_arr=[]
        
        p=ImzMLParser( self.imzml_filename) 

        self.progressBar_Thread = progressBar_Thread()
        self.progressBar_Thread.setTerminationEnabled(True)
        self.progressBar_Thread.bar_signal.connect(lambda x: self.progressBar.setValue(x))
        self.progressBar_Thread.start()
            
        a=0

        for idx, (x,y,z) in enumerate(p.coordinates):
            columnname="c_"+str(a)
            mzs, intensities = p.getspectrum(idx)
            t=len(mzs)
            mzs_arr.append(mzs)
            int_arr.append(intensities)
            #sağa giden her bir sütunun axis=1 olarak ortalaması ile iki yeni sütun ve grafiği        
        df_mzs=pd.DataFrame(mzs_arr)
        df_intensity=pd.DataFrame(int_arr)
        #print(df_mzs.info())
        x=df_mzs.mean(axis=0)
        y=df_intensity.mean(axis=0)
        graphDf=pd.DataFrame(list(zip(x,y)),columns=["x","y"])
        graphDf=graphDf.sort_values(by=['x'])
        
        self.spectrum.canvas.ax.clear()
        self.spectrum.canvas.ax.plot(graphDf.x, graphDf.y)    
        self.spectrum.canvas.ax.set_yticks(np.arange(0, max(y), 100))

        self.spectrum.canvas.ax.set_title('Spectrum',  fontsize = 10, loc='center')      
        self.spectrum.canvas.ax.set_xlabel('m/z',  fontsize = 10)          
        self.spectrum.canvas.ax.set_ylabel('Absolute Instensity',  fontsize = 10)  

        self.spectrum.canvas.figure.subplots_adjust(bottom=0.22)
        self.spectrum.canvas.draw()

        plt.figure("Spectrum view") #pencere ve kaydetme ismi
        plt.title("Spectrum") # grafik başlığı
        plt.xlabel("m/z") 
        plt.ylabel("Absolute intensity")
        plt.plot(graphDf.x, graphDf.y)
    
        
    def DataProcessing(self):
         
        self.progressBar.setValue(0) 

        p=ImzMLParser(self.imzml_filename)
        
        mz_value= float(self.targetA_textbox.text()) #369
        tol=float(self.width_textbox.text()) #0.1
        z=float(self.z_textbox.text()) #1
        
        #mz_value2 = float(self.targetB_textbox.text())
        #tol2 = float(self.width_textboxb.text())       
        #mz_value3 = float(self.targetC_textbox.text())
        #tol3 = float(self.width_textboxc.text())
        self.progressBar_Thread = progressBar_Thread()
        self.progressBar_Thread.setTerminationEnabled(True)
        self.progressBar_Thread.bar_signal.connect(lambda x: self.progressBar.setValue(x))
        self.progressBar_Thread.start()
        
        
        def bisect_spectrum(mzs, mz_value, tol):
                ix_l, ix_u = bisect_left(mzs, mz_value - tol), bisect_right(mzs, mz_value + tol) - 1
                if ix_l == len(mzs):
                    return len(mzs), len(mzs)
                if ix_u < 1:
                    return 0, 0
                if ix_u == len(mzs):
                    ix_u -= 1
                if mzs[ix_l] < (mz_value - tol):
                    ix_l += 1
                if mzs[ix_u] > (mz_value+ tol):
                    ix_u -= 1
                return ix_l, ix_u  
                    
        def getionimage (p, mz_value, tol, z, reduce_func=sum):
                tol1 = abs(tol)
                im = np.zeros((p.imzmldict["max count of pixels y"], p.imzmldict["max count of pixels x"]))
                
                for i, (x, y, z_) in enumerate(p.coordinates):
                    if z_ == 0:
                    
                        UserWarning("z coordinate = 0 present, if you're getting blank images set getionimage(.., .., z=0)")
                    if z_ == z:
                        mzs, ints = map(lambda x: np.asarray(x), p.getspectrum(i))
                        min_i, max_i = bisect_spectrum(mzs, mz_value, tol)
                        im[y - 1, x - 1] = reduce_func(ints[min_i:max_i+1])
                return im   
            
        final1=getionimage(p, mz_value, tol, z, reduce_func=sum)

        final1=final1[~(final1==0).all(1)] #sadece yatay eksende
        final1=final1.T
        final1=final1[~(final1==0).all(1)]
        final1=final1.T #yatay ve dikey eksende

        df=pd.DataFrame(final1, index = None)
        df.to_csv("file_name.csv", index =None)
    
        my_data = genfromtxt('file_name.csv', delimiter=',')
        # plt.imshow(my_data, interpolation ='nearest')
        # plt.show()

        self.mpl.canvas.ax.get_xaxis().set_visible(False)
        self.mpl.canvas.ax.get_yaxis().set_visible(False)

        self.mpl.canvas.ax.clear()
              
        self.progressBar.setValue(100)
        
        inAdi=self.cb2.currentText()

        
        cmapAdi=self.cb.currentText()

        im = self.mpl.canvas.ax.imshow(my_data, aspect = 'auto' , interpolation = inAdi,  cmap=cmapAdi)
        
        cb = self.mpl.canvas.fig.colorbar(im)
        self.mpl.canvas.ax.set_title('m/z value 1 image',  fontsize = 8, loc='right')  
        
        self.mpl.canvas.ax.set_facecolor(plt.rcParams['axes.facecolor'])
        # self.mpl.canvas.ax.set_aspect('equal')

        self.mz_value = self.targetA_textbox.text()
        self.tol = self.width_textbox.text()
        self.z = self.z_textbox.text()
        
        self.mz_value2 = self.targetB_textbox.text()
        self.tol2 = self.width_textboxb.text()

        self.mz_value3 = self.targetC_textbox.text()
        self.tol3 = self.width_textboxc.text()

 
        if all([self.mz_value, self.tol, self.z, 
                # self.mz_value2, self.tol2, self.mz_value3, self.tol3, 
                self.imzml_filename]):

            print(self.cb.currentText())
            print(self.cb2.currentText())

                        
            settings = setting_parameter
            (
                float(self.mz_value),
                float(self.tol),
                float(self.z),

                #float(self.mz_value2),
                #float(self.tol2),                
                #float(self.mz_value3),
                #float(self.tol3),        
                self.cb.currentText,  
                self.cb2.currentText
            )
          
        self.mpl.ntb.update()             
        self.mpl.ntb.push_current()     
        self.mpl.canvas.draw()

        cb.remove()
     
    def DataProcessing2(self):
         
        self.progressBar.setValue(0) 

        p=ImzMLParser(self.imzml_filename)
        
        mz_value= float(self.targetA_textbox.text()) #369
        tol=float(self.width_textbox.text()) #0.1
        z=float(self.z_textbox.text())
        

        mz_value2 = float(self.targetB_textbox.text())
        tol2 = float(self.width_textboxb.text())
        
        mz_value3 = float(self.targetC_textbox.text())
        #tol3 = float(self.width_textboxc.text())
        try:
            if self.width_textboxc.text().strip() == "":
                raise ValueError("Textbox boş. Lütfen bir değer girin.")
            tol3 = float(self.width_textboxc.text())
        except ValueError as e:
            print("Hata:", e)
            
        self.progressBar_Thread = progressBar_Thread()
        self.progressBar_Thread.setTerminationEnabled(True)
        self.progressBar_Thread.bar_signal.connect(lambda x: self.progressBar.setValue(x))
        self.progressBar_Thread.start()
                
        # self.progressBar.setValue(0)
        def bisect_spectrum(mzs, mz_value, tol):
                ix_l, ix_u = bisect_left(mzs, mz_value - tol), bisect_right(mzs, mz_value + tol) - 1
                if ix_l == len(mzs):
                    return len(mzs), len(mzs)
                if ix_u < 1:
                    return 0, 0
                if ix_u == len(mzs):
                    ix_u -= 1
                if mzs[ix_l] < (mz_value - tol):
                    ix_l += 1
                if mzs[ix_u] > (mz_value+ tol):
                    ix_u -= 1
                return ix_l, ix_u     
        def getionimage (p, mz_value, tol, z, reduce_func=sum):
                tol1 = abs(tol)
                im = np.zeros((p.imzmldict["max count of pixels y"], p.imzmldict["max count of pixels x"]))
                
                for i, (x, y, z_) in enumerate(p.coordinates):
                    if z_ == 0:
                    
                        UserWarning("z coordinate = 0 present, if you're getting blank images set getionimage(.., .., z=0)")
                    if z_ == z:
                        mzs, ints = map(lambda x: np.asarray(x), p.getspectrum(i))
                        min_i, max_i = bisect_spectrum(mzs, mz_value, tol)
                        im[y - 1, x - 1] = reduce_func(ints[min_i:max_i+1])
                return im   
        final1=getionimage(p, mz_value, tol, z, reduce_func=sum)
        final1=final1[~(final1==0).all(1)] #sadece yatay eksende
        final1=final1.T
        final1=final1[~(final1==0).all(1)]
        final1=final1.T 

        def bisect_spectrum(mzs, mz_value2, tol2):
                ix_l, ix_u = bisect_left(mzs, mz_value2 - tol2), bisect_right(mzs, mz_value2 + tol2) - 1
                if ix_l == len(mzs):
                    return len(mzs), len(mzs)
                if ix_u < 1:
                    return 0, 0
                if ix_u == len(mzs):
                    ix_u -= 1
                if mzs[ix_l] < (mz_value2 - tol2):
                    ix_l += 1
                if mzs[ix_u] > (mz_value2 + tol2):
                    ix_u -= 1
                return ix_l, ix_u    
        
        def getionimage (p, mz_value2, tol2, z, reduce_func=sum):
        
                tol = abs(tol2)
                im = np.zeros((p.imzmldict["max count of pixels y"], p.imzmldict["max count of pixels x"]))
                
                for i, (x, y, z_) in enumerate(p.coordinates):
                    if z_ == 0:
                    
                        UserWarning("z coordinate = 0 present, if you're getting blank images set getionimage(.., .., z=0)")
                    if z_ == z:
                        mzs, ints = map(lambda x: np.asarray(x), p.getspectrum(i))
                        min_i, max_i = bisect_spectrum(mzs, mz_value2, tol2)
                        im[y - 1, x - 1] = reduce_func(ints[min_i:max_i+1])
                return im
                
        
        final2=getionimage(p, mz_value2, tol2, z, reduce_func=sum)
        
        final2=final2[~(final2==0).all(1)] #sadece yatay eksende
        final2=final2.T
        final2=final2[~(final2==0).all(1)]
        final2=final2.T #yatay ve dikey eksende
       
        def bisect_spectrum(mzs, mz_value3, tol3):
                ix_l, ix_u = bisect_left(mzs, mz_value3 - tol3), bisect_right(mzs, mz_value3 + tol3) - 1
                if ix_l == len(mzs):
                    return len(mzs), len(mzs)
                if ix_u < 1:
                    return 0, 0
                if ix_u == len(mzs):
                    ix_u -= 1
                if mzs[ix_l] < (mz_value3 - tol3):
                    ix_l += 1
                if mzs[ix_u] > (mz_value3 + tol3):
                    ix_u -= 1
                return ix_l, ix_u    
        
        
        def getionimage (p, mz_value3, tol3, z, reduce_func=sum):
        
                tol = abs(tol3)
                im = np.zeros((p.imzmldict["max count of pixels y"], p.imzmldict["max count of pixels x"]))
                
                for i, (x, y, z_) in enumerate(p.coordinates):
                    if z_ == 0:
                    
                        UserWarning("z coordinate = 0 present, if you're getting blank images set getionimage(.., .., z=0)")
                    if z_ == z:
                        mzs, ints = map(lambda x: np.asarray(x), p.getspectrum(i))
                        min_i, max_i = bisect_spectrum(mzs, mz_value3, tol3)
                        im[y - 1, x - 1] = reduce_func(ints[min_i:max_i+1])
                return im
                
        # #%....mz value ve tol giriniz:
        final3=getionimage(p, mz_value3,tol3, z, reduce_func=sum)
        final3=final3[~(final3==0).all(1)] #sadece yatay eksende
        final3=final3.T
        final3=final3[~(final3==0).all(1)]
        final3=final3.T #yatay ve dikey eksende

        self.mpl.canvas.ax.get_xaxis().set_visible(False)
        self.mpl.canvas.ax.get_yaxis().set_visible(False)

        self.mpl.canvas.ax.clear()
              
        inAdi=self.cb2.currentText()

        cmapAdi=self.cb.currentText()

        
        self.progressBar.setValue(100) 


        im = self.mpl.canvas.ax.imshow(final1, aspect = 'auto' , interpolation =inAdi, cmap=cmapAdi)
        cb = self.mpl.canvas.fig.colorbar(im)
        self.mpl.canvas.ax.set_title('m/z value 1 image ',  fontsize = 10, loc='right')  



        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11,3), sharex = True ,sharey=True)
        fig.set_facecolor("#f6f7fa")
        

        ax1.imshow(final1, interpolation =inAdi)
        # im1 = ax1.pcolormesh(final1, cmap=cmapAdi)
        im1 = ax1.contourf(final1, cmap=cmapAdi)
        

        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.setp(ax1.get_yticklabels(), visible=False)
        ax1.set_title('m/z value 1 image',  fontsize = 8, loc='right')  

        
        ax2.imshow(final2, interpolation =inAdi)
        im2 = ax2.pcolormesh(final2, cmap=cmapAdi) # fine features
        plt.setp(ax2.get_xticklabels(), visible=False)
        plt.setp(ax2.get_yticklabels(), visible=False)
        ax2.set_title('m/z value 2 image',  fontsize = 8, loc='right')  

        
        ax3.imshow(final3, interpolation =inAdi)
        im3 = ax3.pcolormesh(final3, cmap=cmapAdi) 
        plt.setp(ax3.get_xticklabels(), visible=False)
        plt.setp(ax3.get_yticklabels(), visible=False)
        ax3.set_title('m/z value 3 image',  fontsize = 8, loc='right')  

 
        
        fig.colorbar(im3, ax=(ax1, ax2, ax3), orientation = 'horizontal', fraction=0.1)
        
        
        plt.show()  
        



        self.mz_value = self.targetA_textbox.text()
        self.tol = self.width_textbox.text()
        self.z= self.z_textbox.text()
        
        self.mz_value2 = self.targetB_textbox.text()
        self.tol2 = self.width_textboxb.text()

        self.mz_value3 = self.targetC_textbox.text()
        self.tol3 = self.width_textboxc.text()


           
 
        if all([self.mz_value, self.tol, self.z, self.mz_value2, self.tol2, self.mz_value3, self.tol3, self.imzml_filename]):

            print(self.cb.currentText())
            print(self.cb2.currentText())

                        
            settings = setting_parameter(
                float(self.mz_value),
                float(self.tol),
                float(self.z),
                float(self.mz_value2),
                float(self.tol2),                
                float(self.mz_value3),
                float(self.tol3),        
                self.cb.currentText())
         

        self.mpl.ntb.update()             
        self.mpl.ntb.push_current()     
        self.mpl.canvas.draw()

        cb.remove()
        
        
        


    def window2(self):        
                 
        self.w = Window2()
        self.w.show()
        
    def boxplot_ (self):
        self.progressBar.setValue(0) 

        p=ImzMLParser(self.imzml_filename)
        mz_value= float(self.targetA_textbox.text()) 
        tol=float(self.width_textbox.text()) 
        z=float(self.z_textbox.text()) 
        
        self.progressBar_Thread = progressBar_Thread()
        self.progressBar_Thread.setTerminationEnabled(True)
        self.progressBar_Thread.bar_signal.connect(lambda x: self.progressBar.setValue(x))
        self.progressBar_Thread.start()
        
        
        def bisect_spectrum(mzs, mz_value, tol):
                ix_l, ix_u = bisect_left(mzs, mz_value - tol), bisect_right(mzs, mz_value + tol) - 1
                if ix_l == len(mzs):
                    return len(mzs), len(mzs)
                if ix_u < 1:
                    return 0, 0
                if ix_u == len(mzs):
                    ix_u -= 1
                if mzs[ix_l] < (mz_value - tol):
                    ix_l += 1
                if mzs[ix_u] > (mz_value + tol):
                    ix_u -= 1
                return ix_l, ix_u     
        def getionimage (p, mz_value, tol, z, reduce_func=sum):
                tol = abs(tol)
                im = np.zeros((p.imzmldict["max count of pixels y"], p.imzmldict["max count of pixels x"]))
                
                for i, (x, y, z_) in enumerate(p.coordinates):
                    if z_ == 0:
                    
                        UserWarning("z coordinate = 0 present, if you're getting blank images set getionimage(.., .., z=0)")
                    if z_ == z:
                        mzs, ints = map(lambda x: np.asarray(x), p.getspectrum(i))
                        min_i, max_i = bisect_spectrum(mzs, mz_value, tol)
                        im[y - 1, x - 1] = reduce_func(ints[min_i:max_i+1])
                return im   
        final1=getionimage(p, mz_value, tol, z, reduce_func=sum)

        int_array = final1. astype(int)


        def remove_ints(final1):
            return final1[~(final1== final1.astype(int))]
        res = remove_ints(final1)

        final_b=res[res != 0]
        final_b=res
        
        self.mpl.canvas.ax.get_xaxis().set_visible(True)
        self.mpl.canvas.ax.get_yaxis().set_visible(True)
        
        self.mpl.canvas.ax.clear()
        
        self.progressBar.setValue(100) 

        self.mpl.canvas.ax.boxplot(final_b, 0, '')
        self.mpl.canvas.ax.set(xlabel=None)
        self.mpl.canvas.ax.set(xticklabels=[])
        self.mpl.canvas.ax.tick_params(bottom=False)
        self.mpl.canvas.ax.set_title('mz value 1 boxplot',  fontsize =8 , loc='right')  


    
        self.mpl.ntb.update()             
        self.mpl.ntb.push_current()     
        self.mpl.canvas.draw()
        
        inAdi=self.cb2.currentText()

        cmapAdi=self.cb.currentText()
        
        im = self.mpl.canvas.ax.imshow(final1, aspect = 'auto' , interpolation = inAdi ,cmap=cmapAdi)
        cb = self.mpl.canvas.fig.colorbar(im)
        cb.remove()  
        

        
    def boxplot_2(self):
           
        self.progressBar.setValue(0) 

        
        
        p=ImzMLParser(self.imzml_filename)
        
        mz_value= float(self.targetA_textbox.text()) #369
        tol=float(self.width_textbox.text()) #0.1
        z=float(self.z_textbox.text()) #0.1


        mz_value2 = float(self.targetB_textbox.text())
        tol2 = float(self.width_textboxb.text())
        
        mz_value3 = float(self.targetC_textbox.text())
        tol3 = float(self.width_textboxc.text())


        self.progressBar_Thread = progressBar_Thread()
        self.progressBar_Thread.setTerminationEnabled(True)
        self.progressBar_Thread.bar_signal.connect(lambda x: self.progressBar.setValue(x))
        self.progressBar_Thread.start()
        
        
        
        
        def bisect_spectrum(mzs, mz_value, tol):
                ix_l, ix_u = bisect_left(mzs, mz_value - tol), bisect_right(mzs, mz_value + tol) - 1
                if ix_l == len(mzs):
                    return len(mzs), len(mzs)
                if ix_u < 1:
                    return 0, 0
                if ix_u == len(mzs):
                    ix_u -= 1
                if mzs[ix_l] < (mz_value - tol):
                    ix_l += 1
                if mzs[ix_u] > (mz_value+ tol):
                    ix_u -= 1
                return ix_l, ix_u     
        def getionimage (p, mz_value, tol, z, reduce_func=sum):
                tol1 = abs(tol)
                im = np.zeros((p.imzmldict["max count of pixels y"], p.imzmldict["max count of pixels x"]))
                
                for i, (x, y, z_) in enumerate(p.coordinates):
                    if z_ == 0:
                    
                        UserWarning("z coordinate = 0 present, if you're getting blank images set getionimage(.., .., z=0)")
                    if z_ == z:
                        mzs, ints = map(lambda x: np.asarray(x), p.getspectrum(i))
                        min_i, max_i = bisect_spectrum(mzs, mz_value, tol)
                        im[y - 1, x - 1] = reduce_func(ints[min_i:max_i+1])
                return im   
        final1=getionimage(p, mz_value, tol, z, reduce_func=sum)
        
        int_array = final1. astype(int)


        def remove_ints(final1):
            return final1[~(final1== final1.astype(int))]
        res = remove_ints(final1)

        final_b=res[res != 0]
        final_b=res



        def bisect_spectrum(mzs, mz_value2, tol2):
                ix_l, ix_u = bisect_left(mzs, mz_value2 - tol2), bisect_right(mzs, mz_value2 + tol2) - 1
                if ix_l == len(mzs):
                    return len(mzs), len(mzs)
                if ix_u < 1:
                    return 0, 0
                if ix_u == len(mzs):
                    ix_u -= 1
                if mzs[ix_l] < (mz_value2 - tol2):
                    ix_l += 1
                if mzs[ix_u] > (mz_value2 + tol2):
                    ix_u -= 1
                return ix_l, ix_u    
        
        def getionimage (p, mz_value2, tol2, z, reduce_func=sum):
        
                tol = abs(tol2)
                im = np.zeros((p.imzmldict["max count of pixels y"], p.imzmldict["max count of pixels x"]))
                
                for i, (x, y, z_) in enumerate(p.coordinates):
                    if z_ == 0:
                    
                        UserWarning("z coordinate = 0 present, if you're getting blank images set getionimage(.., .., z=0)")
                    if z_ == z:
                        mzs, ints = map(lambda x: np.asarray(x), p.getspectrum(i))
                        min_i, max_i = bisect_spectrum(mzs, mz_value2, tol2)
                        im[y - 1, x - 1] = reduce_func(ints[min_i:max_i+1])
                return im
                
        
        final2=getionimage(p, mz_value2, tol2, z, reduce_func=sum)

        int_array = final2. astype(int)


        def remove_ints(final2):
            return final2[~(final2== final2.astype(int))]
        res = remove_ints(final2)

        final_b2=res[res != 0]
        final_b2=res

        
        def bisect_spectrum(mzs, mz_value3, tol3):
                ix_l, ix_u = bisect_left(mzs, mz_value3 - tol3), bisect_right(mzs, mz_value3 + tol3) - 1
                if ix_l == len(mzs):
                    return len(mzs), len(mzs)
                if ix_u < 1:
                    return 0, 0
                if ix_u == len(mzs):
                    ix_u -= 1
                if mzs[ix_l] < (mz_value3 - tol3):
                    ix_l += 1
                if mzs[ix_u] > (mz_value3 + tol3):
                    ix_u -= 1
                return ix_l, ix_u    
        
        
        def getionimage (p, mz_value3, tol3, z, reduce_func=sum):
        
                tol = abs(tol3)
                im = np.zeros((p.imzmldict["max count of pixels y"], p.imzmldict["max count of pixels x"]))
                
                for i, (x, y, z_) in enumerate(p.coordinates):
                    if z_ == 0:
                    
                        UserWarning("z coordinate = 0 present, if you're getting blank images set getionimage(.., .., z=0)")
                    if z_ == z:
                        mzs, ints = map(lambda x: np.asarray(x), p.getspectrum(i))
                        min_i, max_i = bisect_spectrum(mzs, mz_value3, tol3)
                        im[y - 1, x - 1] = reduce_func(ints[min_i:max_i+1])
                return im
                
        # #%....mz value ve tol giriniz:
        final3=getionimage(p, mz_value3,tol3, z, reduce_func=sum)
        int_array = final3. astype(int)


        def remove_ints(final3):
            return final1[~(final3== final3.astype(int))]
        res = remove_ints(final3)

        final_b3=res[res != 0]
        final_b3=res


        # self.mpl.canvas.ax.get_xaxis().set_visible(False)
        # self.mpl.canvas.ax.get_yaxis().set_visible(False)

        self.mpl.canvas.ax.clear()
    


        self.progressBar.setValue(100) 

        self.mpl.canvas.ax.boxplot(final_b, 0, '')
        self.mpl.canvas.ax.set(xlabel=None)
        self.mpl.canvas.ax.set(xticklabels=[])
        self.mpl.canvas.ax.tick_params(bottom=False)
        self.mpl.canvas.ax.set_title('m/z value 1 boxplot',  fontsize = 8, loc='right')  



        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11,2.5),sharex = True,sharey=True)


        ax1.boxplot(final_b, 0, '')
        ax1.set(xlabel=None)
        ax1.set(xticklabels=[])
        ax1.tick_params(bottom=False)
        ax1.set_title('m/z value 1 boxplot',  fontsize = 8, loc='right')  

        ax2.boxplot(final_b2, 0, '')
        ax2.set(xlabel=None)
        ax2.set(xticklabels=[])
        ax2.tick_params(bottom=False)
        ax2.set_title('m/z value 2 boxplot',  fontsize = 8, loc='right')  

        
        ax3.boxplot(final_b3, 0, '')
        ax3.set(xlabel=None)
        ax3.set(xticklabels=[])
        ax3.tick_params(bottom=False)
        ax3.set_title('m/z value 3 boxplot',  fontsize = 8, loc='right')  

           
        plt.show()  
        


        self.mz_value = self.targetA_textbox.text()
        self.tol = self.width_textbox.text()
        
        self.z= self.z_textbox.text()
        
        self.mz_value2 = self.targetB_textbox.text()
        self.tol2 = self.width_textboxb.text()

        self.mz_value3 = self.targetC_textbox.text()
        self.tol3 = self.width_textboxc.text()


           
 
        if all([self.mz_value, self.tol, self.z, self.mz_value2, self.tol2, self.mz_value3, self.tol3, self.imzml_filename]):

            print(self.cb.currentText())
            print(self.cb2.currentText())

                        
            settings = setting_parameter
            (
                
                float(self.mz_value),
                float(self.tol),
                float(self.z),
                float(self.mz_value2),
                float(self.tol2),                
                float(self.mz_value3),
                float(self.tol3),        
                self.cb.currentText(),
                self.cb2.currentText()

            )         
               
            
            
        self.mpl.ntb.update()             
        self.mpl.ntb.push_current()     
        self.mpl.canvas.draw()
                
        inAdi=self.cb2.currentText()

        cmapAdi=self.cb.currentText()
        im = self.mpl.canvas.ax.imshow(final1, aspect = 'auto' , interpolation = inAdi, cmap=cmapAdi)
        cb = self.mpl.canvas.fig.colorbar(im)
        cb.remove()  
            

        
        
    def clear(self):
        
        
        self.progressBar.setValue(0) 
        self.mpl.canvas.ax.clear()
        self.mpl.canvas.draw()
            
        self.spectrum.canvas.ax.clear()
        self.spectrum.canvas.draw()
        
        self.progressBar.setValue(0) 
        
        self.targetA_textbox.clear()
        self.width_textbox.clear()
        
        self.z_textbox.clear()
        
        self.targetB_textbox.clear()
        self.width_textboxb.clear()

        self.targetC_textbox.clear()
        self.width_textboxc.clear()
        self.viewFileName.clear()
        cb.remove()



class setting_parameter():
    def __init__(self, mz_value, tol, z, mz_value2, tol2, mz_value3, tol3, colormap):
        self.mz_value = mz_value
        self.tol =  tol     
        self.z= z
        self.mz_value2 = mz_value2
        self.tol2 =  tol2  
        self.mz_value3 = mz_value3
        self.tol3 =  tol3  
        # self.colormap = colormap



#My Thread



if __name__ == '__main__':
    app=0
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")   
    dmw = DesignerMainWindow()
    # show it
    # dmw.showMaximized()
    dmw.show() 
    sys.exit(app.exec_())
        
        
        
        