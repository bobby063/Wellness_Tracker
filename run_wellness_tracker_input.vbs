CreateObject("WScript.Shell").Run "cmd /c """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\run_wellness_tracker_input.bat""", 0, False

 
