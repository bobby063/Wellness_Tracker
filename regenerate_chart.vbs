CreateObject("WScript.Shell").Run "cmd /c """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & "\regenerate_chart.bat"""", 0, False
