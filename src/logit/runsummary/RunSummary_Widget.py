# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '..\LogIt\src\logit\runsummary\RunSummary_Widget.ui'
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

class Ui_RunSummaryWidget(object):
    def setupUi(self, RunSummaryWidget):
        RunSummaryWidget.setObjectName(_fromUtf8("RunSummaryWidget"))
        RunSummaryWidget.resize(740, 577)
        self.verticalLayout_2 = QtGui.QVBoxLayout(RunSummaryWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.simGraphGroup = QtGui.QGroupBox(RunSummaryWidget)
        self.simGraphGroup.setObjectName(_fromUtf8("simGraphGroup"))
        self.verticalLayout = QtGui.QVBoxLayout(self.simGraphGroup)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.simGraphGraphics = PlotWidget(self.simGraphGroup)
        self.simGraphGraphics.setObjectName(_fromUtf8("simGraphGraphics"))
        self.verticalLayout.addWidget(self.simGraphGraphics)
        self.verticalLayout_2.addWidget(self.simGraphGroup)
        self.runStatusGroup = QtGui.QGroupBox(RunSummaryWidget)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial 12"))
        font.setPointSize(9)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.runStatusGroup.setFont(font)
        self.runStatusGroup.setObjectName(_fromUtf8("runStatusGroup"))
        self.gridLayout_2 = QtGui.QGridLayout(self.runStatusGroup)
        self.gridLayout_2.setContentsMargins(-1, 16, -1, -1)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.runStatusTable = QtGui.QTableWidget(self.runStatusGroup)
        self.runStatusTable.setObjectName(_fromUtf8("runStatusTable"))
        self.runStatusTable.setColumnCount(7)
        self.runStatusTable.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.runStatusTable.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.runStatusTable.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.runStatusTable.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.runStatusTable.setHorizontalHeaderItem(3, item)
        item = QtGui.QTableWidgetItem()
        self.runStatusTable.setHorizontalHeaderItem(4, item)
        item = QtGui.QTableWidgetItem()
        self.runStatusTable.setHorizontalHeaderItem(5, item)
        item = QtGui.QTableWidgetItem()
        self.runStatusTable.setHorizontalHeaderItem(6, item)
        self.runStatusTable.horizontalHeader().setStretchLastSection(True)
        self.gridLayout_2.addWidget(self.runStatusTable, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.runStatusGroup)

        self.retranslateUi(RunSummaryWidget)
        QtCore.QMetaObject.connectSlotsByName(RunSummaryWidget)

    def retranslateUi(self, RunSummaryWidget):
        RunSummaryWidget.setWindowTitle(_translate("RunSummaryWidget", "Form", None))
        self.simGraphGroup.setTitle(_translate("RunSummaryWidget", "Simulation graph", None))
        self.runStatusGroup.setTitle(_translate("RunSummaryWidget", "Run status", None))
        item = self.runStatusTable.horizontalHeaderItem(0)
        item.setText(_translate("RunSummaryWidget", "GUID", None))
        item = self.runStatusTable.horizontalHeaderItem(1)
        item.setText(_translate("RunSummaryWidget", "TCF_NAME", None))
        item = self.runStatusTable.horizontalHeaderItem(2)
        item.setText(_translate("RunSummaryWidget", "COMPLETION", None))
        item = self.runStatusTable.horizontalHeaderItem(3)
        item.setText(_translate("RunSummaryWidget", "MAX_MB", None))
        item = self.runStatusTable.horizontalHeaderItem(4)
        item.setText(_translate("RunSummaryWidget", "MAX_DDV", None))
        item = self.runStatusTable.horizontalHeaderItem(5)
        item.setText(_translate("RunSummaryWidget", "STATUS", None))
        item = self.runStatusTable.horizontalHeaderItem(6)
        item.setText(_translate("RunSummaryWidget", "RUN_OPTIONS", None))

from pyqtgraph import PlotWidget
