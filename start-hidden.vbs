Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
appDir = fso.GetParentFolderName(WScript.ScriptFullName)
exePath = fso.BuildPath(appDir, "dist\RemoteInputBoard.exe")
shell.CurrentDirectory = fso.BuildPath(appDir, "dist")
shell.Run """" & exePath & """", 0, False
