# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\LogIT_UI_qt5.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(804, 631)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(450, 550))
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/Logit_Logo2_25x25.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setIconSize(QtCore.QSize(25, 25))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setMinimumSize(QtCore.QSize(0, 0))
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setObjectName("tabWidget")
        self.helpTab = QtWidgets.QWidget()
        self.helpTab.setObjectName("helpTab")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.helpTab)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.textEdit = QtWidgets.QTextEdit(self.helpTab)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        self.textEdit.setFont(font)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_15.addWidget(self.textEdit)
        self.tabWidget.addTab(self.helpTab, "")
        self.viewLogTab = QtWidgets.QWidget()
        self.viewLogTab.setObjectName("viewLogTab")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.viewLogTab)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.logViewTab = QtWidgets.QTabWidget(self.viewLogTab)
        self.logViewTab.setToolTip("")
        self.logViewTab.setTabPosition(QtWidgets.QTabWidget.North)
        self.logViewTab.setDocumentMode(False)
        self.logViewTab.setObjectName("logViewTab")
        self.modelViewTab = QtWidgets.QWidget()
        self.modelViewTab.setObjectName("modelViewTab")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.modelViewTab)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.selectModelGroup = QtWidgets.QGroupBox(self.modelViewTab)
        self.selectModelGroup.setMaximumSize(QtCore.QSize(16777215, 50))
        self.selectModelGroup.setTitle("")
        self.selectModelGroup.setObjectName("selectModelGroup")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.selectModelGroup)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.selectModelGroup)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.modelSelectCbox = QtWidgets.QComboBox(self.selectModelGroup)
        self.modelSelectCbox.setMinimumSize(QtCore.QSize(200, 0))
        self.modelSelectCbox.setObjectName("modelSelectCbox")
        self.horizontalLayout.addWidget(self.modelSelectCbox)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_5.addWidget(self.selectModelGroup)
        self.tableModelGroup = QtWidgets.QGroupBox(self.modelViewTab)
        self.tableModelGroup.setTitle("")
        self.tableModelGroup.setObjectName("tableModelGroup")
        self.tableModelGroupLayout = QtWidgets.QVBoxLayout(self.tableModelGroup)
        self.tableModelGroupLayout.setObjectName("tableModelGroupLayout")
        self.verticalLayout_5.addWidget(self.tableModelGroup)
        self.logViewTab.addTab(self.modelViewTab, "")
        self.verticalLayout_10.addWidget(self.logViewTab)
        self.tabWidget.addTab(self.viewLogTab, "")
        self.verticalLayout_2.addWidget(self.tabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 804, 18))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuExport = QtWidgets.QMenu(self.menuFile)
        self.menuExport.setToolTip("")
        self.menuExport.setStatusTip("")
        self.menuExport.setWhatsThis("")
        self.menuExport.setObjectName("menuExport")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuTools = QtWidgets.QMenu(self.menuSettings)
        self.menuTools.setObjectName("menuTools")
        self.menuLoggingLevel = QtWidgets.QMenu(self.menuSettings)
        self.menuLoggingLevel.setObjectName("menuLoggingLevel")
        self.menuTools_2 = QtWidgets.QMenu(self.menubar)
        self.menuTools_2.setObjectName("menuTools_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.statusbar.setFont(font)
        self.statusbar.setAutoFillBackground(True)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExportToExcel = QtWidgets.QAction(MainWindow)
        self.actionExportToExcel.setObjectName("actionExportToExcel")
        self.actionLoad = QtWidgets.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionNewModelLog = QtWidgets.QAction(MainWindow)
        self.actionNewModelLog.setObjectName("actionNewModelLog")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionUpdateDatabaseSchema = QtWidgets.QAction(MainWindow)
        self.actionUpdateDatabaseSchema.setEnabled(True)
        self.actionUpdateDatabaseSchema.setObjectName("actionUpdateDatabaseSchema")
        self.actionSaveSetupAs = QtWidgets.QAction(MainWindow)
        self.actionSaveSetupAs.setObjectName("actionSaveSetupAs")
        self.actionLoadSetup = QtWidgets.QAction(MainWindow)
        self.actionLoadSetup.setObjectName("actionLoadSetup")
        self.actionLogWarning = QtWidgets.QAction(MainWindow)
        self.actionLogWarning.setCheckable(True)
        self.actionLogWarning.setChecked(False)
        self.actionLogWarning.setObjectName("actionLogWarning")
        self.actionLogInfo = QtWidgets.QAction(MainWindow)
        self.actionLogInfo.setCheckable(True)
        self.actionLogInfo.setObjectName("actionLogInfo")
        self.actionLogDebug = QtWidgets.QAction(MainWindow)
        self.actionLogDebug.setCheckable(True)
        self.actionLogDebug.setObjectName("actionLogDebug")
        self.actionReloadDatabase = QtWidgets.QAction(MainWindow)
        self.actionReloadDatabase.setObjectName("actionReloadDatabase")
        self.actionCopyLogsToClipboard = QtWidgets.QAction(MainWindow)
        self.actionCopyLogsToClipboard.setObjectName("actionCopyLogsToClipboard")
        self.actionCheckForUpdates = QtWidgets.QAction(MainWindow)
        self.actionCheckForUpdates.setObjectName("actionCheckForUpdates")
        self.actionResolveIefddFiles = QtWidgets.QAction(MainWindow)
        self.actionResolveIefddFiles.setObjectName("actionResolveIefddFiles")
        self.actionResolveIefFiles = QtWidgets.QAction(MainWindow)
        self.actionResolveIefFiles.setObjectName("actionResolveIefFiles")
        self.actionUpdateAllRunStatus = QtWidgets.QAction(MainWindow)
        self.actionUpdateAllRunStatus.setObjectName("actionUpdateAllRunStatus")
        self.actionNewdb = QtWidgets.QAction(MainWindow)
        self.actionNewdb.setObjectName("actionNewdb")
        self.actionSetdb = QtWidgets.QAction(MainWindow)
        self.actionSetdb.setObjectName("actionSetdb")
        self.actionCleanDatabase = QtWidgets.QAction(MainWindow)
        self.actionCleanDatabase.setObjectName("actionCleanDatabase")
        self.actionExportToJson = QtWidgets.QAction(MainWindow)
        self.actionExportToJson.setObjectName("actionExportToJson")
        self.menuExport.addAction(self.actionExportToExcel)
        self.menuExport.addAction(self.actionExportToJson)
        self.menuFile.addAction(self.actionNewModelLog)
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.menuExport.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionLoadSetup)
        self.menuFile.addAction(self.actionSaveSetupAs)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionCopyLogsToClipboard)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menuTools.addAction(self.actionUpdateDatabaseSchema)
        self.menuTools.addAction(self.actionUpdateAllRunStatus)
        self.menuTools.addAction(self.actionCleanDatabase)
        self.menuLoggingLevel.addAction(self.actionLogWarning)
        self.menuLoggingLevel.addAction(self.actionLogInfo)
        self.menuLoggingLevel.addAction(self.actionLogDebug)
        self.menuSettings.addAction(self.menuTools.menuAction())
        self.menuSettings.addAction(self.menuLoggingLevel.menuAction())
        self.menuSettings.addSeparator()
        self.menuSettings.addAction(self.actionReloadDatabase)
        self.menuTools_2.addAction(self.actionResolveIefFiles)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuTools_2.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        self.logViewTab.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.tabWidget, self.logViewTab)
        MainWindow.setTabOrder(self.logViewTab, self.textEdit)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "LogIT"))
        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Arial\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><img src=\":/icons/Logit_Logo2_75x75.png\" /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt; font-weight:600; color:#0055ff;\">LogIT ~VERSION~</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600; text-decoration: underline;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600; text-decoration: underline;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; text-decoration: underline; color:#0055ff;\">Info</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:600; text-decoration: underline;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Name: LogIT (Logger for Isis and Tuflow) </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Version: ~VERSION~</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Author: Duncan Runnacles</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Copyright: (C) 2016 Duncan Runnacles</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">email: duncan.runnacles@thomasmackay.co.uk</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">License: GPL v2 - Available at: http://www.gnu.org/licenses/gpl-2.0.html</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7pt;\">This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the license, or (at your option) any later version.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7pt;\">This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRENTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7pt;\">You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; text-decoration: underline; color:#0055ff;\">Summary</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600; text-decoration: underline;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">LogIT provides an interface for logging run specific information from ISIS / Flood Modeller Pro and TUFLOW models. It supports loading of ISIS Event Files (*.ief) and TUFLOW run files (*.tcf). Once one of these files has been provided LogIT will read all .ecf, .tgc, etc files and any GIS or data files that they contain.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Once a model has been loaded it will read key model information into tables that can be amended and added to the database. The database can be exported to Excel format at any time.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; text-decoration: underline; color:#0055ff;\">Instructions</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600; text-decoration: underline; color:#0055ff;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Create a database:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Before a model log can be loaded you need to create a log database. This can be done through the File &gt; Create New Model Log menu (Ctrl+N).</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">A different database can be loaded at any time using the File &gt; Load Model Log menu (Ctrl-O).</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">LogIT will attempt to load the last used database when you open the software.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Load Model:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Prior to loading the model you can enter the Input Log Variables. These will then be included in the Variable tables once the model is loaded. They will also be remembered when LogIT is restarted.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">To load a model file click the Load Model button (Ctrl-L).</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The key variables from the model will be entered into the Variables tables on the Single Model Load tab. </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Some of the cells in the table are editable. These cells will be coloured green. If a file already exists in the database it cannot be re-entered, so the filename will be coloured red.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Add Log Entry:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">When you have finished editing the log entry you can enter it in the database by clicking the Add New Log Entry button.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This will store the log entry exactly as shown in the Variables tables into the log database and show the updated log in the View Log tab tables.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Adding Multiple Models at once:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">You can add multiple models on the Multiple Model Load Tab.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Click the &quot;+&quot; button (Ctrl-M) to browse for model files. Remove files by selecting the checkbox\'s and clicking the &quot;X&quot; button (Ctrl-X).</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Click the Add All Log Entries button to load listed files to the log.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If there are any errors they will be output to the Error Logs box and can be copied to the clipboard if required.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Editing Existing Log Entries:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">It is possible to edit log entries that have already been added to the log database in the View Log tab. However only certain cells are editable.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">To edit a cell: double click the required cell and edit the entry. Once you have completed all required edits select the rows to update and select Update Row(s) from the right-click menu.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Delete Log Entry:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Deleting entries from the log database can be done in the View Log tab tables. To delete an entry in any of the log pages right click the row and select Delete Row (<span style=\" font-weight:600;\">you almost never want to do this</span> - see comment on Delete Associated Entries below).</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">It is possible to safely delete an entire log entry (i.e. any associated dat, tgc, etc entries that are not referenced by another run) by selecting Delete Associated entries. This is only available on the Run table menu.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Update Ief Location / Update Tcf Location:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Available on the right-click menu of the Run table.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If selected you can update the location of the Ief or Tcf files associated with the selected log entry. This may be useful if you have moved the files somewhere else or the log was built with an older version of LogIT and does not include this information in the table.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The IEF_DIR and TCF_DIR log entries that will be updated are used by some other tools in the software. Certain functionality will require that they exist.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Exporting to Excel:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Exporting the log databse to Excel format can be done through the File &gt; Export &gt; Excel Menu (Ctrl+E).</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This will export all of the existing database tables to an Excel Workbook. A Worksheet will be created for each of the exported database tables.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Note: the LogFormatter.bas file is no longer maintained - contact me if you think it should be updated again!</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">There is an Excel VBA Module called LogFormatter.bas available in the distribution folder for &quot;pretifying&quot; the exported Workbook. To use it:</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">1) Open the exported Excel Workbook.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">2) Open the Visual Basic window.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">3) Right-Click on your log book project.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">4) Click &quot;Import File...&quot;.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">5) Find the LogFormatter_vX.bas file in the LogIT folder and open it.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">6) Go back to the Excel Workbook and under developer click &quot;Macros&quot;).</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">7) Depending on whether you have any other Workbooks open or not the Macro </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">   will either be caller &quot;formatLogbook&quot; or &quot;LogFormatter.formatLogbook&quot;.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">   Select it and click &quot;Run&quot;.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The jumbled output from the software should now be nicely formatted :)</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Update Database Schema:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">When a new version of LogIT is released there may be changes to the way that the log database is setup. If this happens the database must be updated in order to use the new version. Settings &gt; Tools &gt; Update Database Schema will make a backup of the existing database and attempt to update it.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Load/Save Setup:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">When you start LogIT it will attempt to load the settings that you last used from a local file. These include Input variables, log database, etc.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If you have particular setups for certain logs, such as different Isis or Tuflow versions, you can save a settings file and load it at any time using File &gt; Load Setup and File &gt; Save Setup As...</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Change the logging level</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The logging output to the console can be changed with:</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Settings &gt; Set Logging Level &gt; Warning\\Info\\Debug.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Warning will issue all errors.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Info will output anything helpful that\'s going on.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Debug will output obscure errors and lots of rubbish.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; text-decoration: underline; color:#0055ff;\">Querying the Database</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">LogIT contains a suite of fairly powerful tools for querying the log data in the database. These tools allow you to check the setup of either an individual run, or groups of runs easily.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">There is a Query submenu on the right-click menu for both the Run and Models tables. This contains shortcuts for several common queries. Running these will open the Simple Query tab on the Query page and create a table of the results. It will also set the search parameters to those used in the query to help better understand how it works. There is a File Summary menu item that can be used to summarise and compare the model files (dat, ied, tgc, tbc, etc) used in the currently selected runs. To use this you must highlight the entire rows by clicking on the row headers to the left of the table. This functionality can also be accessed through the Model File Query tab.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Query tab contains a set of different tools for examining the content of the database. These are as follows:</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Simple Query:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Used for basic interogation of the database. You can select specific tables or data types, refine the search by run id or text values and choose whether to include subfiles (files within control files). By selecting New files only the entry will only be returned if it is the first instance entered into the database (e.g. if multiple runs use the same .tgc file only the first run to be entered would have this .tgc\'s new file status set to True).</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Model Files Query:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Used for comparing the main model files (control files, ieds, dats) included in the run data. You can select specific runs from the Run table and export them here using the File Summary menu item, or select specific run id\'s from a list. This is useful for comparing which files were used in which run.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Note that you can also export the selection from the Simple Query tab when setting the table to RUN Options or RUN Events. This will allow you to use text query refinements on the simple query tab for these tables and identify only certain run options or event information and then export those tables to this tab using the File Summary item on the right-click menu.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Custom Query:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">A scripting query that uses standard SQL (specifically Sqlite) to interrogate the database. You can write, save, and load sql scripts in the editor, and have more fine-grained control over database queries.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The editor includes syntax highlighting to help identify typos in table and column names. For information on the configuration of the database, useful when constructing your queries, you can launch an image of the database design from the right-click menu in the script editor.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Note that the script editor can only be used for retrieving records from the database, not updating it. This is to try and avoid any corruption of the database schema.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; text-decoration: underline; color:#0055ff;\">Updating LogIT</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">LogIT will automatically tell you if an update is available when it is launched. It will then ask if you would like to download the new version. If you say yes it will download and unzip the new version into a folder adjacent to the current installation. It will also attempt to copy over any settings file that you have in the install directory. If you choose not to install at that time you can launch the process when you want by using the Settings &gt; Check for Updates menu item.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; text-decoration: underline; color:#0055ff;\">Additional Tools</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">LogIT includes the following additional tools:</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Model Extractor - </span><span style=\" font-weight:600; font-style:italic; color:#0055ff;\">Beta</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Model Extractor can be used to extract the files associated with a particular model into a specified output directory. This is useful if you need to deliver a model to someone. It saves having to go through the model folders and locating associated files, as LogIT does it automatically. All paths within both the ISIS and Tuflow models will be updated to be relative to the output folder, so that the model can be moved anywhere and will still run.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">A model can be loaded from the Browse... button on the Model Extractor tab or by using right-click on the RUN table and selecting Extract Model.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">It is currently still being built and checked so it should be used with care and extracted contents should be quality controlled after running the tool.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#0055ff;\">Ief Resolver - </span><span style=\" font-weight:600; font-style:italic; color:#0055ff;\">Beta</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Ief Resolver can be used to automatically update the absolute file paths in an ISIS/FMP .ief file. When a model is moved from one location to another (e.g. from one computer to another the absolute file paths stored in the .ief file will no longer point to the correct location of the file. This tool can be used to automatically update the paths in the .ief to work in the new location.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The Ief Resolver can be found under the Tools menu.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; text-decoration: underline; color:#0055ff;\">Current Limitations</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600; text-decoration: underline;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">LogIT uses the SHIP Library to read and write from Tuflow and ISIS/FMP files (You can get the <a href=\"https://github.com/duncan-r/SHIP\"><span style=\" text-decoration: underline; color:#0000ff;\">SHIP API</span></a> code on GitHub). When reading data files, such as materials.csv or boundary conditions.csv files, it expects the format to match that set out in the Tuflow Manual. Tuflow is more forgiving and will allow files to be setup differently if certain headers are given. If these files are not setup as shown in the manual they will not be correctly read. This should cause a warning to be noted, but is worth keeping an eye on.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; text-decoration: underline; color:#0055ff;\">Common Errors</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600; text-decoration: underline;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Some common errors can occur when loading files. These are outlined here.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Load Error - Unable to load model from file at: filename:</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">This can be caused by several issues that may be bugs. A common cause is trying to load a model from an IEF file which has unfindable paths. Check the log for the error; if it says &quot;Tcf file referenced by ief does not exist at: filename&quot; make sure that filename exists and is findable. </p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">When something like this happens you should check the error logs for further details. You can find them in the logs folder.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600; text-decoration: underline; color:#0055ff;\">Reporting Bugs</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:600; text-decoration: underline;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If you find an error that is not included in the Common Errors list above please report it as a bug to duncan.runnacles@thomasmackay.co.uk.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Click File &gt; Copy Logs to Clipboard (Ctrl-Z). This should automatically zip up the log files and copy them to the system clipboard so that you can paste them into an email client, or a folder somewhere, to send with the bug report. If for some reason this does not work, there should be a folder called /logs/ in the same folder as the executable. If this folder is empty there has been a problem with setting up the logging on your computer (probably due to access rights or a virus checker not allowing LogIT to write to disc; If this is the case a warning will be sent to the console saying &quot;Unable to create log file directory&quot;). To get the log entry you can try and reproduce the error and copy the text from the console window. </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Any other details about the contents and setup of the model that you are trying to log should also be included in the bug report. It may be easier to just send the ief/tcf/tgc/tbc/trd files if you are happy to do it. </p></body></html>"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.helpTab), _translate("MainWindow", "Help"))
        self.label.setText(_translate("MainWindow", "File type"))
        self.logViewTab.setTabText(self.logViewTab.indexOf(self.modelViewTab), _translate("MainWindow", "Model Files"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.viewLogTab), _translate("MainWindow", "View Log"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuExport.setTitle(_translate("MainWindow", "Export"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuTools.setTitle(_translate("MainWindow", "Tools"))
        self.menuLoggingLevel.setToolTip(_translate("MainWindow", "<html><head/><body><p>Set the logging output level for the console.</p></body></html>"))
        self.menuLoggingLevel.setTitle(_translate("MainWindow", "Set Logging Level"))
        self.menuTools_2.setTitle(_translate("MainWindow", "Tools"))
        self.actionExportToExcel.setText(_translate("MainWindow", "Excel"))
        self.actionExportToExcel.setToolTip(_translate("MainWindow", "Export model log database to Excel (*.xls) Workbook"))
        self.actionExportToExcel.setStatusTip(_translate("MainWindow", "Export model log database to Excel (*.xls) Workbook"))
        self.actionExportToExcel.setWhatsThis(_translate("MainWindow", "Export model log database to Excel (*.xls) Workbook"))
        self.actionLoad.setText(_translate("MainWindow", "Load Model Log"))
        self.actionLoad.setToolTip(_translate("MainWindow", "Load existing model log from file"))
        self.actionLoad.setStatusTip(_translate("MainWindow", "Load existing model log from file"))
        self.actionLoad.setWhatsThis(_translate("MainWindow", "Load existing model log from file"))
        self.actionNewModelLog.setText(_translate("MainWindow", "Create New Model Log"))
        self.actionNewModelLog.setToolTip(_translate("MainWindow", "Create new model log database"))
        self.actionNewModelLog.setStatusTip(_translate("MainWindow", "Create new model log database"))
        self.actionNewModelLog.setWhatsThis(_translate("MainWindow", "Create new model log database"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionExit.setToolTip(_translate("MainWindow", "Quit LogIT"))
        self.actionExit.setStatusTip(_translate("MainWindow", "Quit LogIT"))
        self.actionExit.setWhatsThis(_translate("MainWindow", "Quit LogIT"))
        self.actionUpdateDatabaseSchema.setText(_translate("MainWindow", "Update Database Schema"))
        self.actionUpdateDatabaseSchema.setToolTip(_translate("MainWindow", "Update an existing database to the format used with the latest version of LogIT"))
        self.actionUpdateDatabaseSchema.setStatusTip(_translate("MainWindow", "Update an existing database to the format used with the latest version of LogIT"))
        self.actionUpdateDatabaseSchema.setWhatsThis(_translate("MainWindow", "Update an existing database to the format used with the latest version of LogIT"))
        self.actionSaveSetupAs.setText(_translate("MainWindow", "Save Setup As..."))
        self.actionSaveSetupAs.setToolTip(_translate("MainWindow", "Save current setup of LogIT (Input Variables, connected database, etc) to file."))
        self.actionSaveSetupAs.setStatusTip(_translate("MainWindow", "Save current setup of LogIT (Input Variables, connected database, etc) to file."))
        self.actionSaveSetupAs.setWhatsThis(_translate("MainWindow", "Save current setup of LogIT (Input Variables, connected database, etc) to file."))
        self.actionLoadSetup.setText(_translate("MainWindow", "Load Setup"))
        self.actionLoadSetup.setToolTip(_translate("MainWindow", "Load setup of LogIT (Input Variables, connected database, etc) from file."))
        self.actionLoadSetup.setStatusTip(_translate("MainWindow", "Load setup of LogIT (Input Variables, connected database, etc) from file."))
        self.actionLoadSetup.setWhatsThis(_translate("MainWindow", "Load setup of LogIT (Input Variables, connected database, etc) from file."))
        self.actionLogWarning.setText(_translate("MainWindow", "Warning"))
        self.actionLogWarning.setStatusTip(_translate("MainWindow", "Output warnings/errors only"))
        self.actionLogInfo.setText(_translate("MainWindow", "Info"))
        self.actionLogInfo.setStatusTip(_translate("MainWindow", "Output warnings/errors to console + additional information"))
        self.actionLogDebug.setText(_translate("MainWindow", "Debug"))
        self.actionLogDebug.setStatusTip(_translate("MainWindow", "Output all information to console - only useful for bug reports."))
        self.actionReloadDatabase.setText(_translate("MainWindow", "Reload Database"))
        self.actionReloadDatabase.setStatusTip(_translate("MainWindow", "Reload the currently used database and refresh the log views."))
        self.actionCopyLogsToClipboard.setText(_translate("MainWindow", "Copy Logs to Clipboard"))
        self.actionCopyLogsToClipboard.setStatusTip(_translate("MainWindow", "Zip up log files and copy them to clipboard for pasting"))
        self.actionCopyLogsToClipboard.setWhatsThis(_translate("MainWindow", "Zip up log files and copy them to clipboard for pasting"))
        self.actionCheckForUpdates.setText(_translate("MainWindow", "Check for Updates"))
        self.actionResolveIefddFiles.setText(_translate("MainWindow", "Resolve Ief Files"))
        self.actionResolveIefFiles.setText(_translate("MainWindow", "Ief Path Resolver"))
        self.actionUpdateAllRunStatus.setText(_translate("MainWindow", "Update All Run Status"))
        self.actionNewdb.setText(_translate("MainWindow", "newdb"))
        self.actionSetdb.setText(_translate("MainWindow", "setdb"))
        self.actionCleanDatabase.setText(_translate("MainWindow", "Clean Database"))
        self.actionExportToJson.setText(_translate("MainWindow", "JSON"))
        self.actionExportToJson.setToolTip(_translate("MainWindow", "Export to JSON file"))
import LogIT_RC_qt5_rc
