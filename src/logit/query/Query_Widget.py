# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\query\Query_Widget.ui'
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

class Ui_QueryWidget(object):
    def setupUi(self, QueryWidget):
        QueryWidget.setObjectName(_fromUtf8("QueryWidget"))
        QueryWidget.resize(781, 443)
        self.verticalLayout = QtGui.QVBoxLayout(QueryWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.queryTabWidget = QtGui.QTabWidget(QueryWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryTabWidget.sizePolicy().hasHeightForWidth())
        self.queryTabWidget.setSizePolicy(sizePolicy)
        self.queryTabWidget.setObjectName(_fromUtf8("queryTabWidget"))
        self.simpleQueryTab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.simpleQueryTab.sizePolicy().hasHeightForWidth())
        self.simpleQueryTab.setSizePolicy(sizePolicy)
        self.simpleQueryTab.setObjectName(_fromUtf8("simpleQueryTab"))
        self.gridLayout = QtGui.QGridLayout(self.simpleQueryTab)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setSpacing(4)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout_13 = QtGui.QHBoxLayout()
        self.horizontalLayout_13.setSpacing(1)
        self.horizontalLayout_13.setObjectName(_fromUtf8("horizontalLayout_13"))
        self.label_2 = QtGui.QLabel(self.simpleQueryTab)
        self.label_2.setMinimumSize(QtCore.QSize(170, 0))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_13.addWidget(self.label_2)
        self.queryTableCbox = QtGui.QComboBox(self.simpleQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryTableCbox.sizePolicy().hasHeightForWidth())
        self.queryTableCbox.setSizePolicy(sizePolicy)
        self.queryTableCbox.setObjectName(_fromUtf8("queryTableCbox"))
        self.horizontalLayout_13.addWidget(self.queryTableCbox)
        self.verticalLayout_4.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_16 = QtGui.QHBoxLayout()
        self.horizontalLayout_16.setObjectName(_fromUtf8("horizontalLayout_16"))
        self.label_4 = QtGui.QLabel(self.simpleQueryTab)
        self.label_4.setMinimumSize(QtCore.QSize(165, 0))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_16.addWidget(self.label_4)
        self.queryModelTextbox = QtGui.QLineEdit(self.simpleQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryModelTextbox.sizePolicy().hasHeightForWidth())
        self.queryModelTextbox.setSizePolicy(sizePolicy)
        self.queryModelTextbox.setObjectName(_fromUtf8("queryModelTextbox"))
        self.horizontalLayout_16.addWidget(self.queryModelTextbox)
        self.verticalLayout_4.addLayout(self.horizontalLayout_16)
        self.horizontalLayout_17 = QtGui.QHBoxLayout()
        self.horizontalLayout_17.setObjectName(_fromUtf8("horizontalLayout_17"))
        self.label_6 = QtGui.QLabel(self.simpleQueryTab)
        self.label_6.setMinimumSize(QtCore.QSize(165, 0))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.horizontalLayout_17.addWidget(self.label_6)
        self.queryFileTextbox = QtGui.QLineEdit(self.simpleQueryTab)
        self.queryFileTextbox.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryFileTextbox.sizePolicy().hasHeightForWidth())
        self.queryFileTextbox.setSizePolicy(sizePolicy)
        self.queryFileTextbox.setObjectName(_fromUtf8("queryFileTextbox"))
        self.horizontalLayout_17.addWidget(self.queryFileTextbox)
        self.verticalLayout_4.addLayout(self.horizontalLayout_17)
        self.horizontalLayout_18 = QtGui.QHBoxLayout()
        self.horizontalLayout_18.setObjectName(_fromUtf8("horizontalLayout_18"))
        self.runSimpleQueryBut = QtGui.QPushButton(self.simpleQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.runSimpleQueryBut.sizePolicy().hasHeightForWidth())
        self.runSimpleQueryBut.setSizePolicy(sizePolicy)
        self.runSimpleQueryBut.setObjectName(_fromUtf8("runSimpleQueryBut"))
        self.horizontalLayout_18.addWidget(self.runSimpleQueryBut)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_18.addItem(spacerItem)
        self.label_3 = QtGui.QLabel(self.simpleQueryTab)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_18.addWidget(self.label_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_18)
        self.gridLayout.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.queryFilterRunCbox = QtGui.QCheckBox(self.simpleQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryFilterRunCbox.sizePolicy().hasHeightForWidth())
        self.queryFilterRunCbox.setSizePolicy(sizePolicy)
        self.queryFilterRunCbox.setObjectName(_fromUtf8("queryFilterRunCbox"))
        self.verticalLayout_5.addWidget(self.queryFilterRunCbox)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_5 = QtGui.QLabel(self.simpleQueryTab)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout_2.addWidget(self.label_5)
        self.queryRunIdSbox = QtGui.QSpinBox(self.simpleQueryTab)
        self.queryRunIdSbox.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryRunIdSbox.sizePolicy().hasHeightForWidth())
        self.queryRunIdSbox.setSizePolicy(sizePolicy)
        self.queryRunIdSbox.setMinimum(1)
        self.queryRunIdSbox.setMaximum(9999999)
        self.queryRunIdSbox.setObjectName(_fromUtf8("queryRunIdSbox"))
        self.horizontalLayout_2.addWidget(self.queryRunIdSbox)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.queryFileCheck = QtGui.QCheckBox(self.simpleQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryFileCheck.sizePolicy().hasHeightForWidth())
        self.queryFileCheck.setSizePolicy(sizePolicy)
        self.queryFileCheck.setChecked(True)
        self.queryFileCheck.setObjectName(_fromUtf8("queryFileCheck"))
        self.verticalLayout_5.addWidget(self.queryFileCheck)
        self.queryNewSubOnlyCheck = QtGui.QCheckBox(self.simpleQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryNewSubOnlyCheck.sizePolicy().hasHeightForWidth())
        self.queryNewSubOnlyCheck.setSizePolicy(sizePolicy)
        self.queryNewSubOnlyCheck.setObjectName(_fromUtf8("queryNewSubOnlyCheck"))
        self.verticalLayout_5.addWidget(self.queryNewSubOnlyCheck)
        self.queryNewModelOnlyCheck = QtGui.QCheckBox(self.simpleQueryTab)
        self.queryNewModelOnlyCheck.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryNewModelOnlyCheck.sizePolicy().hasHeightForWidth())
        self.queryNewModelOnlyCheck.setSizePolicy(sizePolicy)
        self.queryNewModelOnlyCheck.setObjectName(_fromUtf8("queryNewModelOnlyCheck"))
        self.verticalLayout_5.addWidget(self.queryNewModelOnlyCheck)
        self.gridLayout.addLayout(self.verticalLayout_5, 0, 1, 1, 1)
        self.queryTabWidget.addTab(self.simpleQueryTab, _fromUtf8(""))
        self.FileSummaryTab = QtGui.QWidget()
        self.FileSummaryTab.setObjectName(_fromUtf8("FileSummaryTab"))
        self.horizontalLayout_8 = QtGui.QHBoxLayout(self.FileSummaryTab)
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.verticalLayout_9 = QtGui.QVBoxLayout()
        self.verticalLayout_9.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout_9.setSpacing(4)
        self.verticalLayout_9.setObjectName(_fromUtf8("verticalLayout_9"))
        self.horizontalLayout_15 = QtGui.QHBoxLayout()
        self.horizontalLayout_15.setObjectName(_fromUtf8("horizontalLayout_15"))
        self.label_8 = QtGui.QLabel(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_15.addWidget(self.label_8)
        self.label_9 = QtGui.QLabel(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_15.addWidget(self.label_9)
        self.verticalLayout_9.addLayout(self.horizontalLayout_15)
        self.horizontalLayout_14 = QtGui.QHBoxLayout()
        self.horizontalLayout_14.setObjectName(_fromUtf8("horizontalLayout_14"))
        self.fileQueryAvailableList = QtGui.QListWidget(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQueryAvailableList.sizePolicy().hasHeightForWidth())
        self.fileQueryAvailableList.setSizePolicy(sizePolicy)
        self.fileQueryAvailableList.setMinimumSize(QtCore.QSize(0, 100))
        self.fileQueryAvailableList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.fileQueryAvailableList.setObjectName(_fromUtf8("fileQueryAvailableList"))
        self.horizontalLayout_14.addWidget(self.fileQueryAvailableList)
        self.verticalLayout_7 = QtGui.QVBoxLayout()
        self.verticalLayout_7.setSizeConstraint(QtGui.QLayout.SetNoConstraint)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.fileQueryAddAllBut = QtGui.QPushButton(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQueryAddAllBut.sizePolicy().hasHeightForWidth())
        self.fileQueryAddAllBut.setSizePolicy(sizePolicy)
        self.fileQueryAddAllBut.setObjectName(_fromUtf8("fileQueryAddAllBut"))
        self.verticalLayout_7.addWidget(self.fileQueryAddAllBut)
        self.fileQueryAddSelectedBut = QtGui.QPushButton(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQueryAddSelectedBut.sizePolicy().hasHeightForWidth())
        self.fileQueryAddSelectedBut.setSizePolicy(sizePolicy)
        self.fileQueryAddSelectedBut.setObjectName(_fromUtf8("fileQueryAddSelectedBut"))
        self.verticalLayout_7.addWidget(self.fileQueryAddSelectedBut)
        self.fileQueryRemoveSelectedBut = QtGui.QPushButton(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQueryRemoveSelectedBut.sizePolicy().hasHeightForWidth())
        self.fileQueryRemoveSelectedBut.setSizePolicy(sizePolicy)
        self.fileQueryRemoveSelectedBut.setObjectName(_fromUtf8("fileQueryRemoveSelectedBut"))
        self.verticalLayout_7.addWidget(self.fileQueryRemoveSelectedBut)
        self.fileQueryRemoveAllBut = QtGui.QPushButton(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQueryRemoveAllBut.sizePolicy().hasHeightForWidth())
        self.fileQueryRemoveAllBut.setSizePolicy(sizePolicy)
        self.fileQueryRemoveAllBut.setObjectName(_fromUtf8("fileQueryRemoveAllBut"))
        self.verticalLayout_7.addWidget(self.fileQueryRemoveAllBut)
        self.horizontalLayout_14.addLayout(self.verticalLayout_7)
        self.fileQuerySelectedList = QtGui.QListWidget(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQuerySelectedList.sizePolicy().hasHeightForWidth())
        self.fileQuerySelectedList.setSizePolicy(sizePolicy)
        self.fileQuerySelectedList.setMinimumSize(QtCore.QSize(0, 100))
        self.fileQuerySelectedList.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.fileQuerySelectedList.setObjectName(_fromUtf8("fileQuerySelectedList"))
        self.horizontalLayout_14.addWidget(self.fileQuerySelectedList)
        self.verticalLayout_9.addLayout(self.horizontalLayout_14)
        self.verticalLayout_9.setStretch(0, 3)
        self.horizontalLayout_8.addLayout(self.verticalLayout_9)
        self.verticalLayout_11 = QtGui.QVBoxLayout()
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(_fromUtf8("verticalLayout_11"))
        self.label_13 = QtGui.QLabel(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_13.sizePolicy().hasHeightForWidth())
        self.label_13.setSizePolicy(sizePolicy)
        self.label_13.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.verticalLayout_11.addWidget(self.label_13)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(7)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.verticalLayout_10 = QtGui.QVBoxLayout()
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(_fromUtf8("verticalLayout_10"))
        self.label_10 = QtGui.QLabel(self.FileSummaryTab)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.verticalLayout_10.addWidget(self.label_10)
        self.label_11 = QtGui.QLabel(self.FileSummaryTab)
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.verticalLayout_10.addWidget(self.label_11)
        self.label_12 = QtGui.QLabel(self.FileSummaryTab)
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.verticalLayout_10.addWidget(self.label_12)
        self.horizontalLayout_4.addLayout(self.verticalLayout_10)
        self.verticalLayout_13 = QtGui.QVBoxLayout()
        self.verticalLayout_13.setObjectName(_fromUtf8("verticalLayout_13"))
        self.fileQueryTcfLine = QtGui.QLineEdit(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQueryTcfLine.sizePolicy().hasHeightForWidth())
        self.fileQueryTcfLine.setSizePolicy(sizePolicy)
        self.fileQueryTcfLine.setObjectName(_fromUtf8("fileQueryTcfLine"))
        self.verticalLayout_13.addWidget(self.fileQueryTcfLine)
        self.fileQueryIefLine = QtGui.QLineEdit(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQueryIefLine.sizePolicy().hasHeightForWidth())
        self.fileQueryIefLine.setSizePolicy(sizePolicy)
        self.fileQueryIefLine.setObjectName(_fromUtf8("fileQueryIefLine"))
        self.verticalLayout_13.addWidget(self.fileQueryIefLine)
        self.fileQueryRunOptionsLine = QtGui.QLineEdit(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQueryRunOptionsLine.sizePolicy().hasHeightForWidth())
        self.fileQueryRunOptionsLine.setSizePolicy(sizePolicy)
        self.fileQueryRunOptionsLine.setObjectName(_fromUtf8("fileQueryRunOptionsLine"))
        self.verticalLayout_13.addWidget(self.fileQueryRunOptionsLine)
        self.horizontalLayout_4.addLayout(self.verticalLayout_13)
        self.verticalLayout_11.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.queryFilesHighlightCbox = QtGui.QCheckBox(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.queryFilesHighlightCbox.sizePolicy().hasHeightForWidth())
        self.queryFilesHighlightCbox.setSizePolicy(sizePolicy)
        self.queryFilesHighlightCbox.setChecked(True)
        self.queryFilesHighlightCbox.setObjectName(_fromUtf8("queryFilesHighlightCbox"))
        self.horizontalLayout_3.addWidget(self.queryFilesHighlightCbox)
        self.fileQueryRunBut = QtGui.QPushButton(self.FileSummaryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fileQueryRunBut.sizePolicy().hasHeightForWidth())
        self.fileQueryRunBut.setSizePolicy(sizePolicy)
        self.fileQueryRunBut.setObjectName(_fromUtf8("fileQueryRunBut"))
        self.horizontalLayout_3.addWidget(self.fileQueryRunBut)
        self.verticalLayout_11.addLayout(self.horizontalLayout_3)
        self.verticalLayout_11.setStretch(0, 7)
        self.horizontalLayout_8.addLayout(self.verticalLayout_11)
        self.queryTabWidget.addTab(self.FileSummaryTab, _fromUtf8(""))
        self.complexQueryTab = QtGui.QWidget()
        self.complexQueryTab.setObjectName(_fromUtf8("complexQueryTab"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.complexQueryTab)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.editorLayout = QtGui.QVBoxLayout()
        self.editorLayout.setSpacing(0)
        self.editorLayout.setObjectName(_fromUtf8("editorLayout"))
        self.horizontalLayout.addLayout(self.editorLayout)
        self.complexScriptList = QtGui.QListWidget(self.complexQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.complexScriptList.sizePolicy().hasHeightForWidth())
        self.complexScriptList.setSizePolicy(sizePolicy)
        self.complexScriptList.setMinimumSize(QtCore.QSize(0, 100))
        self.complexScriptList.setObjectName(_fromUtf8("complexScriptList"))
        self.horizontalLayout.addWidget(self.complexScriptList)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.newQueryScriptBut = QtGui.QPushButton(self.complexQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.newQueryScriptBut.sizePolicy().hasHeightForWidth())
        self.newQueryScriptBut.setSizePolicy(sizePolicy)
        self.newQueryScriptBut.setObjectName(_fromUtf8("newQueryScriptBut"))
        self.verticalLayout_2.addWidget(self.newQueryScriptBut)
        self.saveQueryScriptBut = QtGui.QPushButton(self.complexQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveQueryScriptBut.sizePolicy().hasHeightForWidth())
        self.saveQueryScriptBut.setSizePolicy(sizePolicy)
        self.saveQueryScriptBut.setObjectName(_fromUtf8("saveQueryScriptBut"))
        self.verticalLayout_2.addWidget(self.saveQueryScriptBut)
        self.saveAsQueryScriptBut = QtGui.QPushButton(self.complexQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveAsQueryScriptBut.sizePolicy().hasHeightForWidth())
        self.saveAsQueryScriptBut.setSizePolicy(sizePolicy)
        self.saveAsQueryScriptBut.setObjectName(_fromUtf8("saveAsQueryScriptBut"))
        self.verticalLayout_2.addWidget(self.saveAsQueryScriptBut)
        self.loadQueryScriptBut = QtGui.QPushButton(self.complexQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.loadQueryScriptBut.sizePolicy().hasHeightForWidth())
        self.loadQueryScriptBut.setSizePolicy(sizePolicy)
        self.loadQueryScriptBut.setObjectName(_fromUtf8("loadQueryScriptBut"))
        self.verticalLayout_2.addWidget(self.loadQueryScriptBut)
        self.runComplexQueryBut = QtGui.QPushButton(self.complexQueryTab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.runComplexQueryBut.sizePolicy().hasHeightForWidth())
        self.runComplexQueryBut.setSizePolicy(sizePolicy)
        self.runComplexQueryBut.setObjectName(_fromUtf8("runComplexQueryBut"))
        self.verticalLayout_2.addWidget(self.runComplexQueryBut)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.queryTabWidget.addTab(self.complexQueryTab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.queryTabWidget)
        self.tableQueryGroup = QtGui.QGroupBox(QueryWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableQueryGroup.sizePolicy().hasHeightForWidth())
        self.tableQueryGroup.setSizePolicy(sizePolicy)
        self.tableQueryGroup.setTitle(_fromUtf8(""))
        self.tableQueryGroup.setObjectName(_fromUtf8("tableQueryGroup"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.tableQueryGroup)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.verticalLayout.addWidget(self.tableQueryGroup)

        self.retranslateUi(QueryWidget)
        self.queryTabWidget.setCurrentIndex(2)
        QtCore.QObject.connect(self.queryFilterRunCbox, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.queryRunIdSbox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(QueryWidget)

    def retranslateUi(self, QueryWidget):
        QueryWidget.setWindowTitle(_translate("QueryWidget", "Form", None))
        self.label_2.setText(_translate("QueryWidget", "Table", None))
        self.label_4.setText(_translate("QueryWidget", "Where modelfile/run options is", None))
        self.label_6.setText(_translate("QueryWidget", "Where subfile is", None))
        self.runSimpleQueryBut.setText(_translate("QueryWidget", "Run Query", None))
        self.label_3.setText(_translate("QueryWidget", "Include % for wildcard (e.g. to match all \'xxv2.xx\' use %v2%)", None))
        self.queryFilterRunCbox.setText(_translate("QueryWidget", "Filter by Run ID", None))
        self.label_5.setText(_translate("QueryWidget", "Run ID", None))
        self.queryFileCheck.setText(_translate("QueryWidget", "Include subfiles", None))
        self.queryNewSubOnlyCheck.setText(_translate("QueryWidget", "New subfiles only", None))
        self.queryNewModelOnlyCheck.setText(_translate("QueryWidget", "New modelfiles only", None))
        self.queryTabWidget.setTabText(self.queryTabWidget.indexOf(self.simpleQueryTab), _translate("QueryWidget", "Simple Query", None))
        self.label_8.setText(_translate("QueryWidget", "Available Run Id\'s", None))
        self.label_9.setText(_translate("QueryWidget", "Selected Run ID\'s", None))
        self.fileQueryAddAllBut.setToolTip(_translate("QueryWidget", "Add all", None))
        self.fileQueryAddAllBut.setText(_translate("QueryWidget", ">>", None))
        self.fileQueryAddSelectedBut.setToolTip(_translate("QueryWidget", "Add selected", None))
        self.fileQueryAddSelectedBut.setText(_translate("QueryWidget", ">", None))
        self.fileQueryRemoveSelectedBut.setToolTip(_translate("QueryWidget", "Remove selected", None))
        self.fileQueryRemoveSelectedBut.setText(_translate("QueryWidget", "<", None))
        self.fileQueryRemoveAllBut.setToolTip(_translate("QueryWidget", "Remove all", None))
        self.fileQueryRemoveAllBut.setText(_translate("QueryWidget", "<<", None))
        self.label_13.setText(_translate("QueryWidget", "Click ID in list boxes to show summary details", None))
        self.label_10.setText(_translate("QueryWidget", "Tcf", None))
        self.label_11.setText(_translate("QueryWidget", "Ief", None))
        self.label_12.setText(_translate("QueryWidget", "Run Options", None))
        self.queryFilesHighlightCbox.setText(_translate("QueryWidget", "Highlight new files", None))
        self.fileQueryRunBut.setText(_translate("QueryWidget", "Run Query", None))
        self.queryTabWidget.setTabText(self.queryTabWidget.indexOf(self.FileSummaryTab), _translate("QueryWidget", "Model File Query", None))
        self.newQueryScriptBut.setText(_translate("QueryWidget", "New Script", None))
        self.saveQueryScriptBut.setText(_translate("QueryWidget", "Save Script", None))
        self.saveAsQueryScriptBut.setText(_translate("QueryWidget", "Save As Script", None))
        self.loadQueryScriptBut.setText(_translate("QueryWidget", "Load Script", None))
        self.runComplexQueryBut.setText(_translate("QueryWidget", "Run Query", None))
        self.queryTabWidget.setTabText(self.queryTabWidget.indexOf(self.complexQueryTab), _translate("QueryWidget", "Custom Query", None))

