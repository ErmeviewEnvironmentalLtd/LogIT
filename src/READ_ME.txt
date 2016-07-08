###############################################################################
#                                                                             #
#                    LogIT - Logger for Isis and Tuflow                       #
#                                                                             #
###############################################################################


Name: LogIT (Logger for Isis and Tuflow) 
Version: ~VERSION~
Author: Duncan Runnacles
Copyright: (C) 2015 Duncan Runnacles
email: duncan.runnacles@thomasmackay.co.uk
License: GPL v2 - See below under section LICENSE

This program is free software; you can redistribute it and/or modify it under 
the terms of the GNU General Public License as published by the Free Software 
Foundation; either version 2 of the license, or (at your option) any later 
version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRENTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with 
this program; if not, write to the Free Software Foundation, Inc., 51 Franklin 
Street, Fifth Floor, Boston, MA 02110-1301, USA.


INSTALLING
=============================

No installation process is required for the software. It should run without any
problems from wherever you place the folder.
To run the program double-click on the "LogIT.exe" executable and the application
should be launched. I recommend that you create a shortcut to "LogIT.exe" and 
place it somewhere away from all the other files to avoid accidentally 
corrupting them. Don't move or change the name of any of the files or folders
within the distibution or LogIT will not work.

If the software does not launch as expected it is likely to be an issue with
your virus software. LogIT requires a couple of windows system files in order
to run which may not be on your computer. These files are included in the 
distribution. Virus software doesn't like programs it doesn't know playing with
system files. If this happens just tell your virus software to allow the
program access and it should work fine. If you wish you can exclude the folder
that you place logit it from the huersistics checks of your antivirus. This 
will stop it from automatially deleting any updates that you recieve, but still
allow it to be scanned like normal. LogIT WILL NOT change any files or 
settings on your computer except: creating a logs folder and a settings file in
the folder containing the executable and creating the databases and excel files
that you request.


EXCEL EXPORT
=============================

There is a VBA macro included in the distribution called LogFormatter.bas.
This can be imported into an Excel Workbook - created using the Export to Excel
function - and used to automatically "prettify" the exported log book.

To use the macro:
1) Open the exported Excel Workbook.
2) Open the Visual Basic window.
3) Right-Click on your log book project.
4) Click "Import File...".
5) Find the LogFormatter.bas file in the LogIT folder and open it.
6) Go back to the Excel Workbook and under developer click "Macros").
7) Depending on whether you have any other Workbooks open or not the Macro 
   will either be caller "formatLogbook" or "LogFormatter.formatLogbook".
   Select it and click "Run".

The jumbled output from the software should now be nicely formatted :)


VERSION HISTORY
=============================

v0.1-Beta:
	- Initial release
	
v0.2-Beta:
	- Added 1D only logging capability.
	- Built database update functionality.
	- Changed Excel exporter to use DatabaseFunction.cur_table list orders for
	  fetching columns rather than writing by column order.
	  
v0.3-Beta:
	- Added ESTRY and BC Database file reading capability.
	- Added Tcf and Ecf tabs to the log tables.
	- Added multiple model load functionality.
	- Added quick reference guide on main page.
	- Added automatically load update log question box when updating database.
	- Added ability to choose logging level in settings menu.
	- Added reload database option to settings menu.
	- Fixed bugs in loading multiple tgc, tbc, etc files at once.
	- Added additional error catching where it was needed.
	- Added role back of database when log update fails at any point.
	- Removed some of the more annoying message boxes. Now writes to statusbar.
	- Updated LogFormatter.bas (version 2) to deal with updated Excel outputs.
	- Updated tab contents.
	
v0.3.1-Beta:
	- Added Remove Associated entries options to RUN table.
	- Added GuiStore module with TableHolder and TableWidget classes. Used to 
	  store regularly access data in the MainGui class.
	- Added LogClasses module with AllLogs and SubLogs classes. Used to store
	  the loaded log entries for easy access and update. Replaces the use of
	  the log_pages dictionary in most parts of the code.
	- Added DatabaseManager class to the DatabaseFunctions module. This
	  encapsulates all of the reading and writing from/to database code. All
	  the module wide functions that performed this have been removed.
	- Major refactoring of the Controller module. Much easier to understand
	  and update now.
	- Fixed lots of bugs.
	- This release has significantly altered parts of the design and 
	  functionality to make it easier to maintain and understand.
	  
v0.3.2-Beta:
	- Bug fix in multiple model loader. Issue with logic in finding whether a
	  log entry exists or not.
	- Better use of error messages in this now as well.
	- Some checks on database schema now included when using "Delete associated
	  entries". Won't allow this on entries added in an old db version.

v0.4.0-Beta:
	- Using tmactools v0.4_Beta.
	- New iteration due to major changes in LogBuilder module.
	- Uses new setup of TmacToolsLibrary, which has had a complete re-write of
	  the tuflow loader and some significant changes to the isis functionality.
	- Added drag and drop functionality to the multiple model load file
	  selection table.
	- Added Copy logs to clipboard menu item. Automatically zips up the log
	  files and copies them to the system clipboard for easy extraction.
	- Added multiple row update functionality to view tables. All selected
	  rows can now be updated at once. Rows that have been edited but not 
	  updated will now be highlighted green.
	- Added RUN_OPTIONS, IEF_DIR and TCF_DIR columns to RUN table.
	- Added check for missing model files (tgc, tbc, etc) when loading a model.
	  If these are not found the load will continue and will note which ones
	  cannot be found to display to user after load.
	- Added widget loading capability to the MainGUI. Should help to reduce 
	  code bloat within the class when adding additional features. 
	- Added ModelExtractor module. This can be used to extract the files
	  associated with a particular model into an output directory.
	- Added update Ief/Tcf location to the RUN table right-click menu.
	- Added extract model to the RUN table right-click menu.
	- Removed update row option from right-click menu as this has been replaced
	  by the more useful update multiple rows functionality.
	- Added functionality to update existing settings files when loaded with
	  any missing members. If new members are added to the settings file it 
	  should gracefully add them and allow user to continue using settings.
	- Added progress bar to status bar. Have also removed the multiple model
	  load progress bar; it uses the status bar version instead.
	- Updated LogFormatter to v3 to accomodate new rows in the RUN table.

v0.4.1-Beta:
	- Added app_metrics module to track tool usage.
	- Added version check and autoinstall feature.

v0.4.2-Beta:
	- Fixed bug in multi model loader error reporting.
	- Added globalsettings module to store version and download info.

v0.4.3-Beta:
	- Fixed bug in model loader return values.
	- Added __DEV_MODE__ variable to global settings and added checks on it 
	  for using app_logger and setting default logging level.
	- Added a base level except catch to the loaders that launches a critical
	  error to user, so they at least know what's going on if it happens.

v0.4.4-Beta:
    - Updated to latest release of TmacToolsLibrary. This fixes a couple
      of small bugs but doesn't have a big impact.
    - Updated the look and feel and fixed some issues with the layouts.
    - Fixed bug in database versioning that meant an older version of the 
      database didn't realised it needed to update.
      THIS MEANS THAT LOG DATABASES WILL NEED UPDATING.
    - Fixed bug in multiple model loader file list. When dragging more
      than one file it was deleting items in the row. Multiple selection
      is now disabled. To remove multiple entries a checkbox can be
      selected.
    - Added release notes dialog on startup after new version installed. 
      Launches a dialog to show version updates to user.
    - Added feature to automatically check for new version on startup.
    - Added current model load tab to settings. It will now remember if
      you were using the single or multiple model load tab last time.
    - Fixed an issue with reading results and check files with the 
      model extractor tool. Now deals with absolute paths.
      This has also been applied to the logger. It will now record the 
      absolute path of the results location in the log if different
      from the main model directory.
    - Improved path display in model extractor input/output textboxes and
      the summary output display. They are now normalised for the OS and
      can be copied and pasted directly into Explorer.
    - Fixed a few more things in the way error handling is dealt with.
      This still needs some work though. Sorry :(

v0.4.5-Beta:
    - Mostly same as last release but with a big fix for a problem in
      loading the results.
    - Updated to latest release of TmacToolsLibrary. This fixes a couple
      of small bugs but doesn't have a big impact.
    - Updated the look and feel and fixed some issues with the layouts.

v0.5.0-Beta:
    - Added IefResolver module. This can now be found under the Tools menu. It
      tries to automatically convert the paths in an .ief file from it's old
      location to the new one. It may not work if the folder structure has been
      changed since the ief file has been setup. It works by updating the root
      folder for the paths to match the new location.
      E.g. if the model folders are now placed in C:\consultancy\mymodels\projectname\model
      and the paths have O:\something\oldplace\model the IefResolver will change
      the portion of the path before model to match the new location. It's a bit
      cleverer than that, but you get it. 
    - Bug fix for a problem in loading the results caused by an edge case that
      was returning an instance of SomeFile instead of the results path string.
    - Made horizontal scrolling in tables a bit easier to use by allowing by
      pixel movement instead of by item.

v0.5.1-Beta:
    - Fixed bug in ISIS only model loader. Could not load ISIS only models because
      of a change in the way the LogBuilder class works.
    - Removed selection box for loading models. LogIT will now work out whether 
      you are trying to load a 1D only 2D only or 1D/2D model automatically.

v0.6.0-Beta:
    - Big change to single model load user interface. Got rid of all of the 
      ugly tables and replaced it with a navigable tree. Same colour schemes
      etc still apply.
    - Moved New Entry tab into a separate widget to attempt to reduce the amount
      of code in the LogIT.py.
    - Fixed bug in new version downloader copy settings process. It should now
      copy settings across properly.
    - Added additional message to new version downloader to let the user know if
      it has been successfull and instruct on what to do next.
    - Some more work on fixing result/check/log paths so that they load properly. 
      There is probably still some work to do here.
    - Update Model Extractor tool. Now copes much better with the different 
      formats for check file paths.

v0.6.1-Beta:
    - Bugfix for Ief Resolver and Model loader.

v0.6.2-Beta:
    - Bugfix for loading a 1D only model when 2D scheme is set to None. Previously
      this wasn't checked and if a tcf file was found in the ief file it was loaded
      into the database. This was happening even if the use of 2d was deactivated.
      The active status is now checked and only 1D components are loaded if it is
      not active.
    - Set 2d results location back to being the folder only and not folder plus
      the tcf filename. This is because results locations can hold additional
      sub area outputs etc as well.
    - Started to implement some unit tests to try and get better at catching
      a few of the regression that seem to be prevailant in the last few releases.
      This will also help to identify and solve some of the problems with the
      slightly unhelpful error messages that are being launched.

v0.6.3-Beta:
    - Improved reporting of missing model files (.tgc/.tbc, etc) from loading
      a tuflow model. There was an issue in the SHIP library and in the way logit
      was trying to report these. They should now be listed when not found.
    - Moved the LogBuilder functionality from module functions to a class to make
      error handling and reporting of warnings a bit cleaner and easier to maintain.
    - Fixed some bugs in the Ief Resolver. These include an oversight in finding
      the correct reference file for the .tcf or .dat file used to work out the
      main containing foler. If there was another file with the same name higher in
      the directory it would pick this one. It now uses a slightly more clever
      approach to rank the liklehood of any particular file being the correct one.
      Improvements also made to the second pass attempt at locating files.
    - Some improvements in error handling in the model logger. These are still not
      perfect, but they should be a bit better than they were. Tests are in place
      that can be updated to help improve this when problems are reported.
    - Added a lot more unittests. These now include some checks for the 
      Ief Resolver and the Model Extractor widgets. Although the coverage is not 
      perfect at the moment most of the basic functionality of the model loaders
      and outputs is there. Further tests will be added when bugs are identified. 
      These should help to avoid as many regressions in the future.

v0.7.0-Beta:
    - [Feature] Added Run Summary widget (Beta). You can load a Tuflow .tlf file and 
      display the current status and key outputs summarised in a table and graph.
      You can also add a log entry into the summary table automatically by
      right clicking on the RUN table entry and selecting Add to Run Summary.
    - [Feature] Added mass balance and run status columns to the to RUN table in
      the log database. These will be automatically added to the log by reading
      the '_TUFLOW Simulations.log' file when loading a model, if it is complete. If
      the run hasn't finished at the time of loading they will not be entered, but
      can be added at any time by using the right click menu in the RUN table and
      selecting Update Status, or update the whole table under the Settings >> 
      Tools menu.
    - IMPORTANT: The new column's will require updating your databases.
    - [BugFix] The Exit menu item and some keyboard shortcuts were broken. I think
      these have all been fixed now.
    - [Feature] Added lots of new keyboard shortcuts. You can find out most of them
      from the Help tab of by hovering over the buttons / looking at the menu items.
      A nonobvious one is the use of F5 to reload the current row in the Run
      Summary Tool table.
    - Implemented a proper standardised interface for all all widgets (tabs). This
      has unfortunately meant that the settings loading has been broken and an
      update will reset settings (not the log database). It will help make it more
      stable in the future and easier to maintain though.
    - Increased and improved the testing framework. Coverage is now pretty good.
      All new features are being added by default and I'm making my way slowly
      through the rest of the code base. Most of mission critical stuff is now
      tested, at least rudimentally.
    - Improvements to the way that settings are stored. It should make them a lot
      more stable and less prone to break when updated...except this once when they
      will definitely completely break. There should be a bit more consitency in 
      how file paths are remembered now. e.g. if you load an .ief file in one tool
      the same directory will be used in another next time.
    - Lots, and lots and lots of bug fixes.

v0.7.1-Beta:
    - [Bugfix] Issue with creating new log database.

v0.7.2-Beta:
    - [Bugfix] Error in 1D only load.
    - [Bugfix] Issue with creating new log database.

v0.7.3-Beta:
    - This is a minor release to update the database before a major upgrade from
      the SHIP library is introduced in the next version. Next version will 
      possibly be an unstable release so database compatibility with this one will
      make it possible to switch back if needed.
    - Updated database to version 8.
    - Added TEF column to RUN table.

v0.7.4-Beta:
    - Added some additional database tables and some changes to the user interface
      to maintain complience with the next release.
    - [Bugfix] problem with multiple model loader when one of the files already
      exists in the database.

v0.8.0-Beta:
    - [Feature] Added support for scenarios and events when logging. Providing run
      options, either in the UI or the FMP run form will cause only the
      corresponding files to be logged.
    - [Feature] Added suppoer for scenario and events when using the model extractor.
      It is now possible to select a 'Harcode output files' option. This will 
      re-write the control files to only use the file and variable calls within
      the specified scenarios and events. None of the if else logic will be kept
      in the output files.
    - [Feature] Added improved support for .trd files (following update for SHIP
      library) and added them as a table to the database.
    - Updated LogFormatter.bas VBA file to work with new TEF and TRD tables.
    - Updated to new version of SHIP library with support for scenario and event
      logic.
    - Added scenario run options input box to New Entry and Model Extractor.
    - Added some additional database tables and some changes to the user interface
    - [Bugfix] problem with multiple model loader when one of the files already
      exists in the database.
    - [Feature] Added TEF column to RUN table.
    - [Feature] Added TRD column to RUN table.
    - [Bugfix] Run Summary not picking up when FMP crashes. Calling it complete
      instead. Fix should work, but time toerances may need some adjusting later.

v0.8.1-Beta:
    - [Feature] Added automatic update functinoality to Run Summary tool.
    - [Feature] Added view FMP runform for completed runs to the Run Summary tool.
      It isn't possible to view this during a run unfortunately because FMP only
      writes it to file on completion. Other ways of visualising this data are 
      doable, possibly, by would require a lot more work.

v0.8.2-Beta:
    - [Bugfix] Run options being incorrectly read sometimes when read from the
      FMP .ief form.
    - [Bugfix] Run options not being displayed in the Single Model Load review
      table.
    - [Feature] Added automatic update functinoality to Run Summary tool.
    - [Feature] Added view FMP runform for completed runs to the Run Summary tool.
      It isn't possible to view this during a run unfortunately because FMP only
      writes it to file on completion. Other ways of visualising this data are 
      doable, possibly, by would require a lot more work.
    - [Feature] Added support for scenarios and events when logging. Providing run
      options, either in the UI or the FMP run form will cause only the
      corresponding files to be logged.
    - [Feature] Added suppoer for scenario and events when using the model extractor.
      It is now possible to select a 'Harcode output files' option. This will 
      rewrite the control files to only use the file and variable calls within
      the specified scenarios and events. None of the if else logic will be kept
      in the output files.
    - [Feature] Added improved support for .trd files (following update for SHIP
      library) and added them as a table to the database.
    - Updated LogFormatter.bas VBA file to work with new TEF and TRD tables.
    - Updated to new version of SHIP library with support for scenario and event
      logic.
    - Added scenario run options input box to New Entry and Model Extractor.
    - Added some additional database tables and some changes to the user interface
    - [Bugfix] problem with multiple model loader when one of the files already
      exists in the database.
    - [Feature] Added TEF column to RUN table.
    - [Feature] Added TRD column to RUN table.
    - [Bugfix] Run Summary not picking up when FMP crashes. Calling it complete
      instead. Fix should work, but time toerances may need some adjusting later.

v0.8.3-Beta:
    - [Bugfix] Issue with updating .ieds files in the Ief Resolver tool.

v0.8.4-Beta:
    - [Feature] Much improved edit saving capabilities in the main logs tab. You
      can update all edits in the table (without needing to select) or update all
      edits in all tables at once. 
    - [Feature] Message box launched when moving away from the logs with unsaved
      edits. This offers to save any changes before they are lost.
    - [Bugfix] Issue with updating .ieds files in the Ief Resolver tool.

##~##

LICENSE
=============================

 GNU GENERAL PUBLIC LICENSE
                       Version 2, June 1991

 Copyright (C) 1989, 1991 Free Software Foundation, Inc.,
 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The licenses for most software are designed to take away your
freedom to share and change it.  By contrast, the GNU General Public
License is intended to guarantee your freedom to share and change free
software--to make sure the software is free for all its users.  This
General Public License applies to most of the Free Software
Foundation's software and to any other program whose authors commit to
using it.  (Some other Free Software Foundation software is covered by
the GNU Lesser General Public License instead.)  You can apply it to
your programs, too.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
this service if you wish), that you receive source code or can get it
if you want it, that you can change the software or use pieces of it
in new free programs; and that you know you can do these things.

  To protect your rights, we need to make restrictions that forbid
anyone to deny you these rights or to ask you to surrender the rights.
These restrictions translate to certain responsibilities for you if you
distribute copies of the software, or if you modify it.

  For example, if you distribute copies of such a program, whether
gratis or for a fee, you must give the recipients all the rights that
you have.  You must make sure that they, too, receive or can get the
source code.  And you must show them these terms so they know their
rights.

  We protect your rights with two steps: (1) copyright the software, and
(2) offer you this license which gives you legal permission to copy,
distribute and/or modify the software.

  Also, for each author's protection and ours, we want to make certain
that everyone understands that there is no warranty for this free
software.  If the software is modified by someone else and passed on, we
want its recipients to know that what they have is not the original, so
that any problems introduced by others will not reflect on the original
authors' reputations.

  Finally, any free program is threatened constantly by software
patents.  We wish to avoid the danger that redistributors of a free
program will individually obtain patent licenses, in effect making the
program proprietary.  To prevent this, we have made it clear that any
patent must be licensed for everyone's free use or not licensed at all.

  The precise terms and conditions for copying, distribution and
modification follow.

                    GNU GENERAL PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. This License applies to any program or other work which contains
a notice placed by the copyright holder saying it may be distributed
under the terms of this General Public License.  The "Program", below,
refers to any such program or work, and a "work based on the Program"
means either the Program or any derivative work under copyright law:
that is to say, a work containing the Program or a portion of it,
either verbatim or with modifications and/or translated into another
language.  (Hereinafter, translation is included without limitation in
the term "modification".)  Each licensee is addressed as "you".

Activities other than copying, distribution and modification are not
covered by this License; they are outside its scope.  The act of
running the Program is not restricted, and the output from the Program
is covered only if its contents constitute a work based on the
Program (independent of having been made by running the Program).
Whether that is true depends on what the Program does.

  1. You may copy and distribute verbatim copies of the Program's
source code as you receive it, in any medium, provided that you
conspicuously and appropriately publish on each copy an appropriate
copyright notice and disclaimer of warranty; keep intact all the
notices that refer to this License and to the absence of any warranty;
and give any other recipients of the Program a copy of this License
along with the Program.

You may charge a fee for the physical act of transferring a copy, and
you may at your option offer warranty protection in exchange for a fee.

  2. You may modify your copy or copies of the Program or any portion
of it, thus forming a work based on the Program, and copy and
distribute such modifications or work under the terms of Section 1
above, provided that you also meet all of these conditions:

    a) You must cause the modified files to carry prominent notices
    stating that you changed the files and the date of any change.

    b) You must cause any work that you distribute or publish, that in
    whole or in part contains or is derived from the Program or any
    part thereof, to be licensed as a whole at no charge to all third
    parties under the terms of this License.

    c) If the modified program normally reads commands interactively
    when run, you must cause it, when started running for such
    interactive use in the most ordinary way, to print or display an
    announcement including an appropriate copyright notice and a
    notice that there is no warranty (or else, saying that you provide
    a warranty) and that users may redistribute the program under
    these conditions, and telling the user how to view a copy of this
    License.  (Exception: if the Program itself is interactive but
    does not normally print such an announcement, your work based on
    the Program is not required to print an announcement.)

These requirements apply to the modified work as a whole.  If
identifiable sections of that work are not derived from the Program,
and can be reasonably considered independent and separate works in
themselves, then this License, and its terms, do not apply to those
sections when you distribute them as separate works.  But when you
distribute the same sections as part of a whole which is a work based
on the Program, the distribution of the whole must be on the terms of
this License, whose permissions for other licensees extend to the
entire whole, and thus to each and every part regardless of who wrote it.

Thus, it is not the intent of this section to claim rights or contest
your rights to work written entirely by you; rather, the intent is to
exercise the right to control the distribution of derivative or
collective works based on the Program.

In addition, mere aggregation of another work not based on the Program
with the Program (or with a work based on the Program) on a volume of
a storage or distribution medium does not bring the other work under
the scope of this License.

  3. You may copy and distribute the Program (or a work based on it,
under Section 2) in object code or executable form under the terms of
Sections 1 and 2 above provided that you also do one of the following:

    a) Accompany it with the complete corresponding machine-readable
    source code, which must be distributed under the terms of Sections
    1 and 2 above on a medium customarily used for software interchange; or,

    b) Accompany it with a written offer, valid for at least three
    years, to give any third party, for a charge no more than your
    cost of physically performing source distribution, a complete
    machine-readable copy of the corresponding source code, to be
    distributed under the terms of Sections 1 and 2 above on a medium
    customarily used for software interchange; or,

    c) Accompany it with the information you received as to the offer
    to distribute corresponding source code.  (This alternative is
    allowed only for noncommercial distribution and only if you
    received the program in object code or executable form with such
    an offer, in accord with Subsection b above.)

The source code for a work means the preferred form of the work for
making modifications to it.  For an executable work, complete source
code means all the source code for all modules it contains, plus any
associated interface definition files, plus the scripts used to
control compilation and installation of the executable.  However, as a
special exception, the source code distributed need not include
anything that is normally distributed (in either source or binary
form) with the major components (compiler, kernel, and so on) of the
operating system on which the executable runs, unless that component
itself accompanies the executable.

If distribution of executable or object code is made by offering
access to copy from a designated place, then offering equivalent
access to copy the source code from the same place counts as
distribution of the source code, even though third parties are not
compelled to copy the source along with the object code.

  4. You may not copy, modify, sublicense, or distribute the Program
except as expressly provided under this License.  Any attempt
otherwise to copy, modify, sublicense or distribute the Program is
void, and will automatically terminate your rights under this License.
However, parties who have received copies, or rights, from you under
this License will not have their licenses terminated so long as such
parties remain in full compliance.

  5. You are not required to accept this License, since you have not
signed it.  However, nothing else grants you permission to modify or
distribute the Program or its derivative works.  These actions are
prohibited by law if you do not accept this License.  Therefore, by
modifying or distributing the Program (or any work based on the
Program), you indicate your acceptance of this License to do so, and
all its terms and conditions for copying, distributing or modifying
the Program or works based on it.

  6. Each time you redistribute the Program (or any work based on the
Program), the recipient automatically receives a license from the
original licensor to copy, distribute or modify the Program subject to
these terms and conditions.  You may not impose any further
restrictions on the recipients' exercise of the rights granted herein.
You are not responsible for enforcing compliance by third parties to
this License.

  7. If, as a consequence of a court judgment or allegation of patent
infringement or for any other reason (not limited to patent issues),
conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot
distribute so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you
may not distribute the Program at all.  For example, if a patent
license would not permit royalty-free redistribution of the Program by
all those who receive copies directly or indirectly through you, then
the only way you could satisfy both it and this License would be to
refrain entirely from distribution of the Program.

If any portion of this section is held invalid or unenforceable under
any particular circumstance, the balance of the section is intended to
apply and the section as a whole is intended to apply in other
circumstances.

It is not the purpose of this section to induce you to infringe any
patents or other property right claims or to contest validity of any
such claims; this section has the sole purpose of protecting the
integrity of the free software distribution system, which is
implemented by public license practices.  Many people have made
generous contributions to the wide range of software distributed
through that system in reliance on consistent application of that
system; it is up to the author/donor to decide if he or she is willing
to distribute software through any other system and a licensee cannot
impose that choice.

This section is intended to make thoroughly clear what is believed to
be a consequence of the rest of this License.

  8. If the distribution and/or use of the Program is restricted in
certain countries either by patents or by copyrighted interfaces, the
original copyright holder who places the Program under this License
may add an explicit geographical distribution limitation excluding
those countries, so that distribution is permitted only in or among
countries not thus excluded.  In such case, this License incorporates
the limitation as if written in the body of this License.

  9. The Free Software Foundation may publish revised and/or new versions
of the General Public License from time to time.  Such new versions will
be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

Each version is given a distinguishing version number.  If the Program
specifies a version number of this License which applies to it and "any
later version", you have the option of following the terms and conditions
either of that version or of any later version published by the Free
Software Foundation.  If the Program does not specify a version number of
this License, you may choose any version ever published by the Free Software
Foundation.

  10. If you wish to incorporate parts of the Program into other free
programs whose distribution conditions are different, write to the author
to ask for permission.  For software which is copyrighted by the Free
Software Foundation, write to the Free Software Foundation; we sometimes
make exceptions for this.  Our decision will be guided by the two goals
of preserving the free status of all derivatives of our free software and
of promoting the sharing and reuse of software generally.

                            NO WARRANTY

  11. BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY
FOR THE PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW.  EXCEPT WHEN
OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES
PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED
OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.  THE ENTIRE RISK AS
TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU.  SHOULD THE
PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING,
REPAIR OR CORRECTION.

  12. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR
REDISTRIBUTE THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES,
INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING
OUT OF THE USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED
TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY
YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER
PROGRAMS), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE
POSSIBILITY OF SUCH DAMAGES.

                     END OF TERMS AND CONDITIONS

            How to Apply These Terms to Your New Programs

  If you develop a new program, and you want it to be of the greatest
possible use to the public, the best way to achieve this is to make it
free software which everyone can redistribute and change under these terms.

  To do so, attach the following notices to the program.  It is safest
to attach them to the start of each source file to most effectively
convey the exclusion of warranty; and each file should have at least
the "copyright" line and a pointer to where the full notice is found.

    <one line to give the program's name and a brief idea of what it does.>
    Copyright (C) <year>  <name of author>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

Also add information on how to contact you by electronic and paper mail.

If the program is interactive, make it output a short notice like this
when it starts in an interactive mode:

    Gnomovision version 69, Copyright (C) year name of author
    Gnomovision comes with ABSOLUTELY NO WARRANTY; for details type `show w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `show c' for details.

The hypothetical commands `show w' and `show c' should show the appropriate
parts of the General Public License.  Of course, the commands you use may
be called something other than `show w' and `show c'; they could even be
mouse-clicks or menu items--whatever suits your program.

You should also get your employer (if you work as a programmer) or your
school, if any, to sign a "copyright disclaimer" for the program, if
necessary.  Here is a sample; alter the names:

  Yoyodyne, Inc., hereby disclaims all copyright interest in the program
  `Gnomovision' (which makes passes at compilers) written by James Hacker.

  <signature of Ty Coon>, 1 April 1989
  Ty Coon, President of Vice

This General Public License does not permit incorporating your program into
proprietary programs.  If your program is a subroutine library, you may
consider it more useful to permit linking proprietary applications with the
library.  If this is what you want to do, use the GNU Lesser General
Public License instead of this License.