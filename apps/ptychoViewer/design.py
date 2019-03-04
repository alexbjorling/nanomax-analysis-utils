# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

#from PyQt5 import QtCore, QtGui, QtWidgets
from silx.gui import qt as QtCore
QtGui = QtCore
QtWidgets = QtCore


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1082, 678)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/logos/icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.filenameBox = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.filenameBox.sizePolicy().hasHeightForWidth())
        self.filenameBox.setSizePolicy(sizePolicy)
        self.filenameBox.setMinimumSize(QtCore.QSize(100, 0))
        self.filenameBox.setBaseSize(QtCore.QSize(200, 0))
        self.filenameBox.setPlaceholderText("")
        self.filenameBox.setObjectName("filenameBox")
        self.gridLayout.addWidget(self.filenameBox, 0, 0, 1, 1)
        self.browseButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.browseButton.sizePolicy().hasHeightForWidth())
        self.browseButton.setSizePolicy(sizePolicy)
        self.browseButton.setMaximumSize(QtCore.QSize(1000000, 16777215))
        self.browseButton.setObjectName("browseButton")
        self.gridLayout.addWidget(self.browseButton, 0, 1, 1, 1)
        self.loadButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadButton.sizePolicy().hasHeightForWidth())
        self.loadButton.setSizePolicy(sizePolicy)
        self.loadButton.setMaximumSize(QtCore.QSize(10000, 16777215))
        self.loadButton.setAutoDefault(True)
        self.loadButton.setDefault(True)
        self.loadButton.setObjectName("loadButton")
        self.gridLayout.addWidget(self.loadButton, 0, 2, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setFocusPolicy(QtCore.Qt.TabFocus)
        self.tabWidget.setObjectName("tabWidget")
        self.object = QtWidgets.QWidget()
        self.object.setObjectName("object")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.object)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.objectWidget = ObjectView(self.object)
        self.objectWidget.setObjectName("objectWidget")
        self.horizontalLayout.addWidget(self.objectWidget)
        self.tabWidget.addTab(self.object, "")
        self.probe = QtWidgets.QWidget()
        self.probe.setObjectName("probe")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.probe)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.focusSlider = QtWidgets.QSlider(self.probe)
        self.focusSlider.setOrientation(QtCore.Qt.Horizontal)
        self.focusSlider.setObjectName("focusSlider")
        self.gridLayout_3.addWidget(self.focusSlider, 0, 2, 1, 1)
        self.focusButton = QtWidgets.QPushButton(self.probe)
        self.focusButton.setObjectName("focusButton")
        self.gridLayout_3.addWidget(self.focusButton, 0, 3, 1, 1)
        self.horizontalFocusView = PropagationView(self.probe)
        self.horizontalFocusView.setObjectName("horizontalFocusView")
        self.gridLayout_3.addWidget(self.horizontalFocusView, 3, 2, 1, 2)
        self.verticalFocusView = PropagationView(self.probe)
        self.verticalFocusView.setObjectName("verticalFocusView")
        self.gridLayout_3.addWidget(self.verticalFocusView, 2, 2, 1, 2)
        self.probePlot = ProbeView(self.probe)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.probePlot.sizePolicy().hasHeightForWidth())
        self.probePlot.setSizePolicy(sizePolicy)
        self.probePlot.setMinimumSize(QtCore.QSize(200, 0))
        self.probePlot.setMaximumSize(QtCore.QSize(600, 16777214))
        self.probePlot.setObjectName("probePlot")
        self.gridLayout_3.addWidget(self.probePlot, 2, 0, 1, 1)
        self.probePlot2 = ProbeView(self.probe)
        self.probePlot2.setMinimumSize(QtCore.QSize(200, 0))
        self.probePlot2.setMaximumSize(QtCore.QSize(600, 16777215))
        self.probePlot2.setObjectName("probePlot2")
        self.gridLayout_3.addWidget(self.probePlot2, 3, 0, 1, 1)
        self.tabWidget.addTab(self.probe, "")
        self.fourier = QtWidgets.QWidget()
        self.fourier.setObjectName("fourier")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.fourier)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.tabWidget.addTab(self.fourier, "")
        self.gridLayout_2.addWidget(self.tabWidget, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1082, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.filenameBox, self.browseButton)
        MainWindow.setTabOrder(self.browseButton, self.loadButton)
        MainWindow.setTabOrder(self.loadButton, self.tabWidget)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "NanoMAX Ptycho Viewer"))
        self.filenameBox.setText(_translate("MainWindow", "<input file>"))
        self.browseButton.setToolTip(_translate("MainWindow", "<html><head/><body><p>Browse for data files</p></body></html>"))
        self.browseButton.setText(_translate("MainWindow", "Browse..."))
        self.loadButton.setToolTip(_translate("MainWindow", "<html><head/><body><p>Go!</p></body></html>"))
        self.loadButton.setText(_translate("MainWindow", "Load"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.object), _translate("MainWindow", "Object"))
        self.focusButton.setText(_translate("MainWindow", "Autofocus"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.probe), _translate("MainWindow", "Probe"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.fourier), _translate("MainWindow", "Fourier shell correlation"))

from widgets.ObjectView import ObjectView
from widgets.Probe import ProbeView, PropagationView
import design_rc
