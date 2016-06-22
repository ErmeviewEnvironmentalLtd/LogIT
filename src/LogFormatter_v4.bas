Attribute VB_Name = "LogFormatter"
'##############################################################################
'
' LogFormatter
' ================
'
' Used for formatting the log pages after they have been exported from the
' LogIT software to Excel.
'
' Add this module to an excel spreadsheet and call the formatLogbook()
' subroutine. It should automatically format the logbook into a bit more of a
' user-friendly setup, with pretty colours and borders and all that jazz.
'
' Author: Duncan Runnacles
' Date: 17/11/2014
' Version: 3.0
'
'##############################################################################

Option Explicit

' Global sheet names
Dim run_sheet As Worksheet
Dim tgc_sheet As Worksheet
Dim tbc_sheet As Worksheet
Dim dat_sheet As Worksheet
Dim bc_sheet As Worksheet
Dim ecf_Sheet As Worksheet
Dim tcf_sheet As Worksheet
Dim tef_sheet As Worksheet


' Sets up the log book with the custom colours and formatting
' for each of the worksheets that exist
Sub formatLogbook()
    
    Application.ScreenUpdating = False
    
    Dim has_run As Boolean
    has_run = sheetExists("RUN")
    If has_run Then
        setupRunSheet
    End If

    Dim has_tgc As Boolean
    has_tgc = sheetExists("TGC")
    If has_tgc Then
        setupTgcSheet
    End If

    Dim has_tbc As Boolean
    has_tbc = sheetExists("TBC")
    If has_tbc Then
        setupTbcSheet
    End If

    Dim has_dat As Boolean
    has_dat = sheetExists("DAT")
    If has_dat Then
        setupDatSheet
    End If

    Dim has_bc As Boolean
    has_bc = sheetExists("BC_DBASE")
    If has_bc Then
        setupBcSheet
    End If
    
    Dim has_ecf As Boolean
    has_ecf = sheetExists("ECF")
    If has_ecf Then
        setupEcfSheet
    End If
    
    Dim has_tcf As Boolean
    has_tcf = sheetExists("TCF")
    If has_tcf Then
        setupTcfSheet
    End If
    
    Dim has_tef As Boolean
    has_tef = sheetExists("TEF")
    If has_tef Then
        setupTefSheet
    End If
    
    ' Zoom out a little bit on all of the sheets and then set the active sheet
    ' as the Run sheet
    setZoomLevel
    run_sheet.Activate
    
    Application.ScreenUpdating = True
    
End Sub

' Sets the tab of the given worksheet to the colour depicted by the given
' values of red, green and blue.
Private Sub setTabColours(wsheet As Worksheet, red As Integer, _
                            green As Integer, blue As Integer)

    On Error Resume Next
        wsheet.Tab.Color = RGB(red, green, blue)

End Sub

Private Sub setZoomLevel()
    Dim ws As Worksheet

    For Each ws In Worksheets
        ws.Select
        ActiveWindow.Zoom = 75
    Next ws
End Sub

' Run worksheet
Private Sub setupRunSheet()
    
    ' Get the run sheet and add some rows at the top for a header
    Set run_sheet = Application.ActiveWorkbook.Sheets("RUN")
    run_sheet.Activate
    run_sheet.Rows(1).Select
    Selection.Resize(8).Insert Shift:=xlDown
    
    ' Create the header labels
    run_sheet.Range("A1").Value = "Project Number:"
    run_sheet.Range("A2").Value = "Project Name:"
    run_sheet.Range("A3").Value = "Modellers:"
    run_sheet.Range("A5").Value = "Description:"
    run_sheet.Range("A7").Value = "Modelling Log:"

    ' Setup cell header colours
    run_sheet.Range("A9:I9").Interior.Color = RGB(204, 255, 255) ' Turquise
    run_sheet.Range("J9:L9").Interior.Color = RGB(153, 204, 255) ' Blue
    run_sheet.Range("M9:U9").Interior.Color = RGB(153, 204, 0) ' Green
    run_sheet.Range("V9:Z9").Interior.Color = RGB(204, 255, 204) ' Light Green
    
    ' Fit the title contents
    Dim used_range As Range
    Set used_range = run_sheet.Range("A9:B9")
    used_range.ColumnWidth = 20
    Set used_range = run_sheet.Range("C9")
    used_range.ColumnWidth = 15
    Set used_range = run_sheet.Range("D9:Z9")
    used_range.ColumnWidth = 20
    
    ' Set bold titles
    Set used_range = run_sheet.Range("A1:A8")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With
    
    Set used_range = run_sheet.Range("B1:B8")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With

    Set used_range = run_sheet.Range("A9:Z9")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With
    
    ' Freeze the panes
    run_sheet.Range("C10").Select
    ActiveWindow.FreezePanes = True
    
    Call setTabColours(run_sheet, 255, 255, 255)

End Sub


' Tgc worksheet
Private Sub setupTgcSheet()
    
    ' Get the Tgc sheet and add the header title
    Set tgc_sheet = Application.ActiveWorkbook.Sheets("TGC")
    tgc_sheet.Activate
    tgc_sheet.Rows(1).Select
    Selection.Resize(1).Insert Shift:=xlDown
    tgc_sheet.Range("A1").Value = "TUFLOW Geometry Control File"
    
    ' Then add the background colour to the title cells
    tgc_sheet.Range("A2:F2").Interior.Color = RGB(153, 204, 0) ' Green
    
    ' Fit the title contents
    Dim used_range As Range
    Set used_range = tgc_sheet.Range("A2:B2")
    used_range.ColumnWidth = 10
    Set used_range = tgc_sheet.Range("C2:E2")
    used_range.ColumnWidth = 30
    Set used_range = tgc_sheet.Range("F2")
    used_range.ColumnWidth = 70
    
    
    ' Set bold titles
    Set used_range = tgc_sheet.Range("A1:F2")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With
    
    ' Freeze the panes
    tgc_sheet.Range("D3").Select
    ActiveWindow.FreezePanes = True
    
    Call setTabColours(tgc_sheet, 153, 204, 0)

End Sub


' Tbc worksheet
Private Sub setupTbcSheet()
    
    ' Get the tbc sheet and add the header row
    Set tbc_sheet = Application.ActiveWorkbook.Sheets("TBC")
    tbc_sheet.Activate
    tbc_sheet.Rows(1).Select
    Selection.Resize(1).Insert Shift:=xlDown
    tbc_sheet.Range("A1").Value = "TUFLOW Boundary Control File"
    
    ' Change the background colour of the titles
    tbc_sheet.Range("A2:F2").Interior.Color = RGB(153, 204, 0) ' Green
    
    ' Fit the title contents
    Dim used_range As Range
    Set used_range = tbc_sheet.Range("A2:B2")
    used_range.ColumnWidth = 10
    Set used_range = tbc_sheet.Range("C2:E2")
    used_range.ColumnWidth = 30
    Set used_range = tbc_sheet.Range("F2")
    used_range.ColumnWidth = 70
    
    ' Set bold titles
    Set used_range = tbc_sheet.Range("A1:F2")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With
    
    ' Freeze the panes
    tbc_sheet.Range("D3").Select
    ActiveWindow.FreezePanes = True
    
    Call setTabColours(tbc_sheet, 153, 204, 0)

End Sub


' Dat worksheet
Private Sub setupDatSheet()
    
    ' Get the dat sheet and add a row at the top with header title
    Set dat_sheet = Application.ActiveWorkbook.Sheets("DAT")
    dat_sheet.Activate
    dat_sheet.Rows(1).Select
    Selection.Resize(1).Insert Shift:=xlDown
    dat_sheet.Range("A1").Value = "ISIS Datafile Development Log"
    
    ' Setup title row colours
    dat_sheet.Range("A2:E2").Interior.Color = RGB(153, 204, 255) ' Blue
    
    ' Fit the title contents
    Dim used_range As Range
    Set used_range = dat_sheet.Range("A2:B2")
    used_range.ColumnWidth = 10
    Set used_range = dat_sheet.Range("C2")
    used_range.ColumnWidth = 20
    Set used_range = dat_sheet.Range("D2:E2")
    used_range.ColumnWidth = 40
    
    
    ' Set bold titles
    Set used_range = dat_sheet.Range("A1:E2")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With
    
    ' Freeze the panes
    dat_sheet.Range("D3").Select
    ActiveWindow.FreezePanes = True
    
    Call setTabColours(dat_sheet, 153, 204, 255)
    dat_sheet.Select
    dat_sheet.Move After:=Sheets(1)

End Sub


' Boundary condition worksheet
Private Sub setupBcSheet()
    
     ' Get the tbc sheet and add the header row
    Set bc_sheet = Application.ActiveWorkbook.Sheets("BC_DBASE")
    bc_sheet.Activate
    bc_sheet.Rows(1).Select
    Selection.Resize(1).Insert Shift:=xlDown
    bc_sheet.Range("A1").Value = "TUFLOW Boundary Conditions File"
    
    ' Change the background colour of the titles
    bc_sheet.Range("A2:F2").Interior.Color = RGB(153, 204, 0) ' Green
    
    ' Fit the title contents
    Dim used_range As Range
    Set used_range = bc_sheet.Range("A2:B2")
    used_range.ColumnWidth = 10
    Set used_range = bc_sheet.Range("C2:E2")
    used_range.ColumnWidth = 30
    Set used_range = bc_sheet.Range("F2")
    used_range.ColumnWidth = 70
    
    ' Set bold titles
    Set used_range = bc_sheet.Range("A1:F2")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With
    
    ' Freeze the panes
    bc_sheet.Range("D3").Select
    ActiveWindow.FreezePanes = True
    
    Call setTabColours(bc_sheet, 153, 204, 0)

End Sub

' Tbc worksheet
Private Sub setupEcfSheet()
    
    ' Get the tbc sheet and add the header row
    Set ecf_Sheet = Application.ActiveWorkbook.Sheets("ECF")
    ecf_Sheet.Activate
    ecf_Sheet.Rows(1).Select
    Selection.Resize(1).Insert Shift:=xlDown
    ecf_Sheet.Range("A1").Value = "ESTRY Control File"
    
    ' Change the background colour of the titles
    ecf_Sheet.Range("A2:F2").Interior.Color = RGB(153, 204, 0) ' Green
    
    ' Fit the title contents
    Dim used_range As Range
    Set used_range = ecf_Sheet.Range("A2:B2")
    used_range.ColumnWidth = 10
    Set used_range = ecf_Sheet.Range("C2:E2")
    used_range.ColumnWidth = 30
    Set used_range = ecf_Sheet.Range("F2")
    used_range.ColumnWidth = 70
    
    ' Set bold titles
    Set used_range = ecf_Sheet.Range("A1:F2")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With
    
    ' Freeze the panes
    ecf_Sheet.Range("D3").Select
    ActiveWindow.FreezePanes = True
    
    Call setTabColours(ecf_Sheet, 153, 204, 0)

End Sub

' Tbc worksheet
Private Sub setupTcfSheet()
    
    ' Get the tbc sheet and add the header row
    Set tcf_sheet = Application.ActiveWorkbook.Sheets("TCF")
    tcf_sheet.Activate
    tcf_sheet.Rows(1).Select
    Selection.Resize(1).Insert Shift:=xlDown
    tcf_sheet.Range("A1").Value = "TUFLOW Control File"
    
    ' Change the background colour of the titles
    tcf_sheet.Range("A2:F2").Interior.Color = RGB(153, 204, 0) ' Green
    
    ' Fit the title contents
    Dim used_range As Range
    Set used_range = tcf_sheet.Range("A2:B2")
    used_range.ColumnWidth = 10
    Set used_range = tcf_sheet.Range("C2:E2")
    used_range.ColumnWidth = 30
    Set used_range = tcf_sheet.Range("F2")
    used_range.ColumnWidth = 70
    
    ' Set bold titles
    Set used_range = tcf_sheet.Range("A1:F2")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With
    
    ' Freeze the panes
    tcf_sheet.Range("D3").Select
    ActiveWindow.FreezePanes = True
    
    Call setTabColours(tcf_sheet, 153, 204, 0)

End Sub

' Tef worksheet
Private Sub setupTefSheet()
    
    ' Get the tbc sheet and add the header row
    Set tef_sheet = Application.ActiveWorkbook.Sheets("TEF")
    tcf_sheet.Activate
    tcf_sheet.Rows(1).Select
    Selection.Resize(1).Insert Shift:=xlDown
    tcf_sheet.Range("A1").Value = "TUFLOW Event File"
    
    ' Change the background colour of the titles
    tcf_sheet.Range("A2:F2").Interior.Color = RGB(153, 204, 0) ' Green
    
    ' Fit the title contents
    Dim used_range As Range
    Set used_range = tef_sheet.Range("A2:B2")
    used_range.ColumnWidth = 10
    Set used_range = tef_sheet.Range("C2:E2")
    used_range.ColumnWidth = 30
    Set used_range = tef_sheet.Range("F2")
    used_range.ColumnWidth = 70
    
    ' Set bold titles
    Set used_range = tef_sheet.Range("A1:F2")
    With used_range
        .Font.Bold = True
        .BorderAround Weight:=xlMedium
    End With
    
    ' Freeze the panes
    tef_sheet.Range("D3").Select
    ActiveWindow.FreezePanes = True
    
    Call setTabColours(tef_sheet, 153, 204, 0)

End Sub


' Checks if a worksheet exists at the given name or not
' @param shtName: the Worksheet name to check.
' @param wb=ActiveWorkbook: the workbook to find the Worksheet in
' @return: True if Worksheet name exists or False otherwise.
Function sheetExists(shtName As String, Optional wb As Workbook) As Boolean
     Dim sht As Worksheet

     If wb Is Nothing Then Set wb = ThisWorkbook
     On Error Resume Next
     Set sht = wb.Sheets(shtName)
     On Error GoTo 0
     sheetExists = Not sht Is Nothing
     
 End Function
 
