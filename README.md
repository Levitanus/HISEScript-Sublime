# HISEScript-Sublime

is a little project trying to integrate HISE (hise.audio, https://github.com/christophhart/HISE) JS API into the Sublime Text

## Instalation:
copy contents of the Repository into the ST Packages folder

Usage:

* Read the message about wrong path
* set the path via changing the settings file (from Preferences menu) ```"hise_path": "C:/HISE-master"```
* reload API and make sure error hasn't appear
* Choose HISEScript syntax in View menu
* Enjoy and contribute ))

![doc](hisedoc.png?raw=true "Documentation")

![new_syntax](NewSyntax.png?raw=true "NewSyntax")

![completions](hise_completions.png?raw=true "Completions")

## keybindings:
You can also see documentation on method. Paste folowing string in Your key-bindings: 

    {"keys": ["ctrl+alt+d"], "command": "hise_show_doc"}

## settings:

has to be placed to the setting file, opened via package menu.

HISE source folder to parse available classes

    "hise_path": "C:/HISE-master"

Optionally supress completions from sublime-completion files

    "hise_supress_completions": false


## version history

### 28.11.2018

**added:**

* namespaces
* locals
* snippets:
    * callbacks mandatory
    * callback of control
    * include
* setting ``"hise_supress_completions": false``
* Math, Array, String objects now parsed from source

**changed:**

* Now syntax is copy of standart Javascript with additions to native scopes, not just added scopes.