# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newentry\NewEntry_Widget.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_NewEntryWidget(object):
    def setupUi(self, NewEntryWidget):
        NewEntryWidget.setObjectName(_fromUtf8("NewEntryWidget"))
        NewEntryWidget.resize(972, 784)
        self.verticalLayout = QtGui.QVBoxLayout(NewEntryWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scrollArea = QtGui.QScrollArea(NewEntryWidget)
        self.scrollArea.setMinimumSize(QtCore.QSize(400, 400))
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 937, 824))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_19 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_19.setObjectName(_fromUtf8("verticalLayout_19"))
        self.verticalLayout_22 = QtGui.QVBoxLayout()
        self.verticalLayout_22.setObjectName(_fromUtf8("verticalLayout_22"))
        self.instructionsTextBrowser = QtGui.QTextBrowser(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.instructionsTextBrowser.sizePolicy().hasHeightForWidth())
        self.instructionsTextBrowser.setSizePolicy(sizePolicy)
        self.instructionsTextBrowser.setMinimumSize(QtCore.QSize(600, 250))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        self.instructionsTextBrowser.setFont(font)
        self.instructionsTextBrowser.setObjectName(_fromUtf8("instructionsTextBrowser"))
        self.verticalLayout_22.addWidget(self.instructionsTextBrowser)
        self.inputVarGroup = QtGui.QGroupBox(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.inputVarGroup.sizePolicy().hasHeightForWidth())
        self.inputVarGroup.setSizePolicy(sizePolicy)
        self.inputVarGroup.setMinimumSize(QtCore.QSize(600, 100))
        self.inputVarGroup.setMaximumSize(QtCore.QSize(16777215, 130))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.inputVarGroup.setFont(font)
        self.inputVarGroup.setObjectName(_fromUtf8("inputVarGroup"))
        self.gridLayout_4 = QtGui.QGridLayout(self.inputVarGroup)
        self.gridLayout_4.setObjectName(_fromUtf8("gridLayout_4"))
        self.modellerLabel = QtGui.QLabel(self.inputVarGroup)
        self.modellerLabel.setObjectName(_fromUtf8("modellerLabel"))
        self.gridLayout_4.addWidget(self.modellerLabel, 0, 0, 1, 1)
        self.modellerTextbox = QtGui.QLineEdit(self.inputVarGroup)
        self.modellerTextbox.setMaximumSize(QtCore.QSize(250, 16777215))
        self.modellerTextbox.setObjectName(_fromUtf8("modellerTextbox"))
        self.gridLayout_4.addWidget(self.modellerTextbox, 0, 1, 1, 1)
        self.isisVersionLabel = QtGui.QLabel(self.inputVarGroup)
        self.isisVersionLabel.setObjectName(_fromUtf8("isisVersionLabel"))
        self.gridLayout_4.addWidget(self.isisVersionLabel, 0, 2, 1, 1)
        self.isisVersionTextbox = QtGui.QLineEdit(self.inputVarGroup)
        self.isisVersionTextbox.setMaximumSize(QtCore.QSize(250, 16777215))
        self.isisVersionTextbox.setObjectName(_fromUtf8("isisVersionTextbox"))
        self.gridLayout_4.addWidget(self.isisVersionTextbox, 0, 3, 1, 1)
        spacerItem = QtGui.QSpacerItem(209, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem, 0, 4, 1, 1)
        self.eventNameLabel = QtGui.QLabel(self.inputVarGroup)
        self.eventNameLabel.setObjectName(_fromUtf8("eventNameLabel"))
        self.gridLayout_4.addWidget(self.eventNameLabel, 1, 0, 1, 1)
        self.eventNameTextbox = QtGui.QLineEdit(self.inputVarGroup)
        self.eventNameTextbox.setMaximumSize(QtCore.QSize(250, 16777215))
        self.eventNameTextbox.setObjectName(_fromUtf8("eventNameTextbox"))
        self.gridLayout_4.addWidget(self.eventNameTextbox, 1, 1, 1, 1)
        self.tuflowVersionLabel = QtGui.QLabel(self.inputVarGroup)
        self.tuflowVersionLabel.setObjectName(_fromUtf8("tuflowVersionLabel"))
        self.gridLayout_4.addWidget(self.tuflowVersionLabel, 1, 2, 1, 1)
        self.tuflowVersionTextbox = QtGui.QLineEdit(self.inputVarGroup)
        self.tuflowVersionTextbox.setMaximumSize(QtCore.QSize(250, 16777215))
        self.tuflowVersionTextbox.setObjectName(_fromUtf8("tuflowVersionTextbox"))
        self.gridLayout_4.addWidget(self.tuflowVersionTextbox, 1, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(209, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 1, 4, 1, 1)
        self.verticalLayout_22.addWidget(self.inputVarGroup)
        self.loadModelTab = QtGui.QTabWidget(self.scrollAreaWidgetContents)
        self.loadModelTab.setTabShape(QtGui.QTabWidget.Rounded)
        self.loadModelTab.setObjectName(_fromUtf8("loadModelTab"))
        self.loadSingleModelTab = QtGui.QWidget()
        self.loadSingleModelTab.setObjectName(_fromUtf8("loadSingleModelTab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.loadSingleModelTab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.loadModelGroup = QtGui.QGroupBox(self.loadSingleModelTab)
        self.loadModelGroup.setMinimumSize(QtCore.QSize(500, 100))
        self.loadModelGroup.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial 12"))
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.loadModelGroup.setFont(font)
        self.loadModelGroup.setStyleSheet(_fromUtf8(""))
        self.loadModelGroup.setObjectName(_fromUtf8("loadModelGroup"))
        self.gridLayout = QtGui.QGridLayout(self.loadModelGroup)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.loadModelComboLabel = QtGui.QLabel(self.loadModelGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadModelComboLabel.sizePolicy().hasHeightForWidth())
        self.loadModelComboLabel.setSizePolicy(sizePolicy)
        self.loadModelComboLabel.setMinimumSize(QtCore.QSize(390, 0))
        self.loadModelComboLabel.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.loadModelComboLabel.setFont(font)
        self.loadModelComboLabel.setObjectName(_fromUtf8("loadModelComboLabel"))
        self.gridLayout.addWidget(self.loadModelComboLabel, 0, 0, 1, 1)
        self.loadModelTextbox = QtGui.QLineEdit(self.loadModelGroup)
        self.loadModelTextbox.setMinimumSize(QtCore.QSize(390, 20))
        self.loadModelTextbox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.loadModelTextbox.setObjectName(_fromUtf8("loadModelTextbox"))
        self.gridLayout.addWidget(self.loadModelTextbox, 1, 0, 1, 2)
        self.loadModelButton = QtGui.QPushButton(self.loadModelGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(55)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadModelButton.sizePolicy().hasHeightForWidth())
        self.loadModelButton.setSizePolicy(sizePolicy)
        self.loadModelButton.setMinimumSize(QtCore.QSize(90, 20))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.loadModelButton.setFont(font)
        self.loadModelButton.setObjectName(_fromUtf8("loadModelButton"))
        self.gridLayout.addWidget(self.loadModelButton, 1, 2, 1, 1)
        self.horizontalLayout_3.addWidget(self.loadModelGroup)
        spacerItem2 = QtGui.QSpacerItem(13, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.submitSingleModelGroup = QtGui.QGroupBox(self.loadSingleModelTab)
        self.submitSingleModelGroup.setEnabled(False)
        self.submitSingleModelGroup.setMinimumSize(QtCore.QSize(190, 0))
        self.submitSingleModelGroup.setMaximumSize(QtCore.QSize(300, 16777215))
        self.submitSingleModelGroup.setObjectName(_fromUtf8("submitSingleModelGroup"))
        self.verticalLayout_23 = QtGui.QVBoxLayout(self.submitSingleModelGroup)
        self.verticalLayout_23.setObjectName(_fromUtf8("verticalLayout_23"))
        self.submitSingleModelLabel = QtGui.QLabel(self.submitSingleModelGroup)
        self.submitSingleModelLabel.setObjectName(_fromUtf8("submitSingleModelLabel"))
        self.verticalLayout_23.addWidget(self.submitSingleModelLabel)
        self.addSingleLogEntryButton = QtGui.QPushButton(self.submitSingleModelGroup)
        self.addSingleLogEntryButton.setMinimumSize(QtCore.QSize(0, 25))
        self.addSingleLogEntryButton.setMaximumSize(QtCore.QSize(150, 25))
        self.addSingleLogEntryButton.setSizeIncrement(QtCore.QSize(50, 30))
        self.addSingleLogEntryButton.setObjectName(_fromUtf8("addSingleLogEntryButton"))
        self.verticalLayout_23.addWidget(self.addSingleLogEntryButton)
        self.horizontalLayout_3.addWidget(self.submitSingleModelGroup)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.modelEntryTreeView = QtGui.QTreeView(self.loadSingleModelTab)
        self.modelEntryTreeView.setObjectName(_fromUtf8("modelEntryTreeView"))
        self.verticalLayout_2.addWidget(self.modelEntryTreeView)
        self.loadModelTab.addTab(self.loadSingleModelTab, _fromUtf8(""))
        self.multiModelLoadTab = QtGui.QWidget()
        self.multiModelLoadTab.setObjectName(_fromUtf8("multiModelLoadTab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.multiModelLoadTab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.chooseMultipleModelsGroupBox = QtGui.QGroupBox(self.multiModelLoadTab)
        self.chooseMultipleModelsGroupBox.setAutoFillBackground(False)
        self.chooseMultipleModelsGroupBox.setObjectName(_fromUtf8("chooseMultipleModelsGroupBox"))
        self.gridLayout_5 = QtGui.QGridLayout(self.chooseMultipleModelsGroupBox)
        self.gridLayout_5.setObjectName(_fromUtf8("gridLayout_5"))
        self.label = QtGui.QLabel(self.chooseMultipleModelsGroupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_5.addWidget(self.label, 0, 0, 1, 1)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.verticalLayout_21 = QtGui.QVBoxLayout()
        self.verticalLayout_21.setObjectName(_fromUtf8("verticalLayout_21"))
        self.addMultiModelButton = QtGui.QPushButton(self.chooseMultipleModelsGroupBox)
        self.addMultiModelButton.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/add_icon_25x25.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.addMultiModelButton.setIcon(icon)
        self.addMultiModelButton.setObjectName(_fromUtf8("addMultiModelButton"))
        self.verticalLayout_21.addWidget(self.addMultiModelButton)
        self.removeMultiModelButton = QtGui.QPushButton(self.chooseMultipleModelsGroupBox)
        self.removeMultiModelButton.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/images/delete_icon_25x25.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.removeMultiModelButton.setIcon(icon1)
        self.removeMultiModelButton.setObjectName(_fromUtf8("removeMultiModelButton"))
        self.verticalLayout_21.addWidget(self.removeMultiModelButton)
        spacerItem3 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_21.addItem(spacerItem3)
        self.horizontalLayout_5.addLayout(self.verticalLayout_21)
        self.gridLayout_5.addLayout(self.horizontalLayout_5, 1, 0, 1, 1)
        self.gridLayout_2.addWidget(self.chooseMultipleModelsGroupBox, 0, 0, 2, 1)
        self.submitMultiModelGroup = QtGui.QGroupBox(self.multiModelLoadTab)
        self.submitMultiModelGroup.setEnabled(False)
        self.submitMultiModelGroup.setMinimumSize(QtCore.QSize(160, 0))
        self.submitMultiModelGroup.setMaximumSize(QtCore.QSize(360, 100))
        self.submitMultiModelGroup.setObjectName(_fromUtf8("submitMultiModelGroup"))
        self.gridLayout_3 = QtGui.QGridLayout(self.submitMultiModelGroup)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.submitMultiModelLabel = QtGui.QLabel(self.submitMultiModelGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.submitMultiModelLabel.sizePolicy().hasHeightForWidth())
        self.submitMultiModelLabel.setSizePolicy(sizePolicy)
        self.submitMultiModelLabel.setMaximumSize(QtCore.QSize(16777215, 100))
        self.submitMultiModelLabel.setWordWrap(True)
        self.submitMultiModelLabel.setObjectName(_fromUtf8("submitMultiModelLabel"))
        self.gridLayout_3.addWidget(self.submitMultiModelLabel, 0, 0, 1, 2)
        self.addMultiLogEntryButton = QtGui.QPushButton(self.submitMultiModelGroup)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.addMultiLogEntryButton.sizePolicy().hasHeightForWidth())
        self.addMultiLogEntryButton.setSizePolicy(sizePolicy)
        self.addMultiLogEntryButton.setMinimumSize(QtCore.QSize(0, 25))
        self.addMultiLogEntryButton.setMaximumSize(QtCore.QSize(150, 25))
        self.addMultiLogEntryButton.setSizeIncrement(QtCore.QSize(50, 30))
        self.addMultiLogEntryButton.setObjectName(_fromUtf8("addMultiLogEntryButton"))
        self.gridLayout_3.addWidget(self.addMultiLogEntryButton, 1, 0, 1, 1)
        spacerItem4 = QtGui.QSpacerItem(228, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem4, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.submitMultiModelGroup, 0, 1, 1, 1)
        self.multiModelLoadErrorGroup = QtGui.QGroupBox(self.multiModelLoadTab)
        self.multiModelLoadErrorGroup.setMaximumSize(QtCore.QSize(360, 16777215))
        self.multiModelLoadErrorGroup.setObjectName(_fromUtf8("multiModelLoadErrorGroup"))
        self.verticalLayout_27 = QtGui.QVBoxLayout(self.multiModelLoadErrorGroup)
        self.verticalLayout_27.setObjectName(_fromUtf8("verticalLayout_27"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.multiModelErrorCopyButton = QtGui.QPushButton(self.multiModelLoadErrorGroup)
        self.multiModelErrorCopyButton.setObjectName(_fromUtf8("multiModelErrorCopyButton"))
        self.horizontalLayout_6.addWidget(self.multiModelErrorCopyButton)
        self.multiModelErrorClearButton = QtGui.QPushButton(self.multiModelLoadErrorGroup)
        self.multiModelErrorClearButton.setObjectName(_fromUtf8("multiModelErrorClearButton"))
        self.horizontalLayout_6.addWidget(self.multiModelErrorClearButton)
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem5)
        self.verticalLayout_27.addLayout(self.horizontalLayout_6)
        self.multiModelLoadErrorTextEdit = QtGui.QTextEdit(self.multiModelLoadErrorGroup)
        self.multiModelLoadErrorTextEdit.setMinimumSize(QtCore.QSize(150, 250))
        self.multiModelLoadErrorTextEdit.setMaximumSize(QtCore.QSize(350, 16777215))
        self.multiModelLoadErrorTextEdit.setObjectName(_fromUtf8("multiModelLoadErrorTextEdit"))
        self.verticalLayout_27.addWidget(self.multiModelLoadErrorTextEdit)
        self.gridLayout_2.addWidget(self.multiModelLoadErrorGroup, 1, 1, 1, 1)
        self.chooseMultipleModelsGroupBox.raise_()
        self.multiModelLoadErrorGroup.raise_()
        self.submitMultiModelGroup.raise_()
        self.loadModelTab.addTab(self.multiModelLoadTab, _fromUtf8(""))
        self.verticalLayout_22.addWidget(self.loadModelTab)
        self.verticalLayout_19.addLayout(self.verticalLayout_22)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(NewEntryWidget)
        self.loadModelTab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(NewEntryWidget)

    def retranslateUi(self, NewEntryWidget):
        NewEntryWidget.setWindowTitle(_translate("NewEntryWidget", "Form", None))
        self.instructionsTextBrowser.setHtml(_translate("NewEntryWidget", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/icons/images/Logit_Logo2_75x75.png\" /><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt;\">  </span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">LogIT is an automatic logging tool for ISIS/Flood Modeller Pro and TUFLOW.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">Duncan R. 2015.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:6pt; font-weight:600; color:#ffffff;\">l</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:14pt; font-weight:600; color:#0055ff;\">Using LogIT</span><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600; color:#0055ff;\"> </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-weight:600;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">1) Create new log database:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> File &gt; Create New Model Log.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">2) Input Log Variables box:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> Insert global log details.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">3) Single / Multiple model load</span><span style=\" font-family:\'MS Shell Dlg 2\';\">: Choose tab and follow the choices below.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">Single Model Load:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">1) Model Type:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> Choose either TUFLOW or ISIS from Load Model dropdown.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">2) Load Model:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> Click Load Model button in Load Model box; browse models.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">3) Edit variables:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> if you want (green are editable).</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">4) Add to log:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> Click Add New Log Entry.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">Multiple Model Load:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">1) Model Type:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> Choose either TUFLOW or ISIS from Load Model dropdown.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">2) Select models:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> Click &quot;+&quot; button to add files.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\';\">         -&gt; Click &quot;X&quot; to remove files.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">3) Add models:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> Click Add All Log Entries.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\';\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">View Log:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> Click View Log tab</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-weight:600;\">Edit Log:</span><span style=\" font-family:\'MS Shell Dlg 2\';\"> Right-click rows in log.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:12pt; font-weight:600; color:#aa0000;\">For more information see the Help tab.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\'; font-size:8pt;\"><br /></p></body></html>", None))
        self.inputVarGroup.setTitle(_translate("NewEntryWidget", "Input Log Variables", None))
        self.modellerLabel.setText(_translate("NewEntryWidget", "Modeller", None))
        self.isisVersionLabel.setText(_translate("NewEntryWidget", "Isis Version", None))
        self.eventNameLabel.setText(_translate("NewEntryWidget", "Event Name", None))
        self.tuflowVersionLabel.setText(_translate("NewEntryWidget", "Tuflow Version", None))
        self.loadModelGroup.setTitle(_translate("NewEntryWidget", "Load Model ", None))
        self.loadModelComboLabel.setText(_translate("NewEntryWidget", "Select an ISIS/FMP ief file or a TUFLOW tcf file to load", None))
        self.loadModelButton.setToolTip(_translate("NewEntryWidget", "Load an IEF or TCF file (Ctrl-L)", None))
        self.loadModelButton.setText(_translate("NewEntryWidget", "Load Model...", None))
        self.submitSingleModelGroup.setTitle(_translate("NewEntryWidget", "Submit Model", None))
        self.submitSingleModelLabel.setToolTip(_translate("NewEntryWidget", "<html><head/><body><p>Button will be activated when a model has been loaded.</p></body></html>", None))
        self.submitSingleModelLabel.setText(_translate("NewEntryWidget", "Click Button to submit the currently \n"
"loaded model to the log database.", None))
        self.addSingleLogEntryButton.setToolTip(_translate("NewEntryWidget", "Add loaded model data to database (Ctrl-A)", None))
        self.addSingleLogEntryButton.setText(_translate("NewEntryWidget", "Add New Log Entry", None))
        self.loadModelTab.setTabText(self.loadModelTab.indexOf(self.loadSingleModelTab), _translate("NewEntryWidget", "Single Model Load", None))
        self.chooseMultipleModelsGroupBox.setTitle(_translate("NewEntryWidget", "Select Multiple Models", None))
        self.label.setText(_translate("NewEntryWidget", "Select the models that you would like to load into the log database using the list below. Add additional models using the add button (+) and remove models using the delete button (x). You can add multiple models at once by holding Ctrl or Shift while clicking with the mouse, and remove multiple models by selecting the check box to the left of the entry and clicking the remove button.\n"
"When done click the Add All Log Entries button. Any errors will be written to the Error Logs window to the right.", None))
        self.submitMultiModelGroup.setToolTip(_translate("NewEntryWidget", "<html><head/><body><p>Button will be activated when a model has been added to the list.</p></body></html>", None))
        self.submitMultiModelGroup.setTitle(_translate("NewEntryWidget", "Submit Model", None))
        self.submitMultiModelLabel.setText(_translate("NewEntryWidget", "Click Button to submit all of the models in the list to the database.", None))
        self.addMultiLogEntryButton.setToolTip(_translate("NewEntryWidget", "Add loaded model data to database (Ctrl-A)", None))
        self.addMultiLogEntryButton.setText(_translate("NewEntryWidget", "Add All Log Entries", None))
        self.multiModelLoadErrorGroup.setTitle(_translate("NewEntryWidget", "Error logs", None))
        self.multiModelErrorCopyButton.setText(_translate("NewEntryWidget", "Copy to Clipboard", None))
        self.multiModelErrorClearButton.setText(_translate("NewEntryWidget", "Clear", None))
        self.loadModelTab.setTabText(self.loadModelTab.indexOf(self.multiModelLoadTab), _translate("NewEntryWidget", "Multiple Model Load", None))

import LogIT_RC_rc
