HISEScript-Sublime

is a little project trying to integrate HISE (hise.audio, https://github.com/christophhart/HISE) JS API into the Sublime Text

Instalation:
copy contents of the Repository into the ST Packages folder

Usage:

* Read the message about wrong path
* set the path via changing the settings file (from Preferences menu) ```"hise_path": "C:/HISE-master"```
* reload API and make sure error hasn't appear
* Choose HISEScript syntax in View menu
* Enjoy and contribute ))

# keybindings:
You can also see documentation on method. Paste folowing string in Your key-bindings: ```{"keys": ["ctrl+alt+d"], "command": "hise_show_doc"},```

![doc](hisedoc.png?raw=true "Documentation")

![complete](hisecomplete.gif?raw=true "Completion")