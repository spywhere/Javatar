## Javatar

### Status: Alpha

A Sublime 3 Plugin for Java Development

### Features
 * [+] Package, SubPackage creation
 * [+] Class, Interface, Enumerator snippets with packge/class auto-complete
 * [*] Project Compile
 * [-] JAR file export (included executable)
 * [+] Package path in status bar

[+] Fully working<br />
[*] Work in progress<br />
[-] Unavailable at this moment

### Commands
* Call
	* Call is used to insert any information about package and class
	* Mostly accessed by shortcut keys (see below)
* Package/SubPackage/Class Creation
	* Package/SubPackage/Class can be create via command palette only
	
#### Commands List

The following commands can be accessed via *Command Palette* (Control+Shift+P or Super+Shift+P)

* Javatar Call
* Create Package
* Create SubPackage
* Create Class/Interface/Enumerator

*All commands will be prefixed by "Javatar: " in order to prevent conflict with another plugins*


#### Javatar Call

Javatar Call is used to insert any information about packages and class like full package path and class name at your cursor point. Javatar Call supports 4 type of data you can insert which are `Full Package Path`, `Current Package Name`, `Class Name` and `Full Class Name`

#### Advanced Creation

In class creation mode (included interface, enum, etc.), all classes will be created relative to current package only. If you want to create from default package (root package), you must specify `~` sign before class name. It's also able to create class corresponded to package path as example below

Input: `Alpha`<br />
Result: `Class "Alpha" is created in current package`

Input: `~Beta`<br />
Result: `Class "Beta" is created in default package`

Input: `me.spywhere.Alpha`<br />
Result: `Class "Alpha" is created in "(current package).me.spywhere" package`

Input: `~me.spywhere.Beta`<br />
Result: `Class "Beta" is created in "me.spywhere.Beta"`

### Important Info

Javatar will specify default package from project folder which contains current working file. If project folder is not found, it will specify current package as `(Unknown Package)`. Create packages/classes within unknown package will cause Javatar to create packages/classes within the same folder as current file.

### Installation
You can install Javatar via [Sublime Package Control](http://wbond.net/sublime_packages/package_control) or by clone this repository into your *Sublime Text 3 / Packages* folder

	cd PACKAGES_PATH
	git clone git://github.com/spywhere/Javatar.git
	
PACKAGES_PATH is related to folder which can be accessed via the *Preference > Browse Packages...*

### Settings
Settings are accessed via the *Preferences > Package Settings > Javatar* or via command palette by type *"Javatar Preference"*

Default settings should not be modified. However, you can copy the relevant settings into Javatar's user settings file

#### Key Bindings
You can access keymap via the preference menu or via command palette same as settings

**Default Key Binding**

*All commands start with `Key+Shift+K` then follows by their shortcut key*

* Open Javatar Call : `Key+Shift+J`
	* This will open quick panel to select which data you want to insert
* Insert full package path: `Key+Shift+P`
	* **Example:**
	* Package.SubPackage
* Insert current package name: `Key+Shift+S`
	* **Example:**
	* SubPackage
* Insert current class name: `Key+Shift+C`
	* **Example:**
	* Class
* Insert full class path: `Key+Shift+F`
	* **Example:**
	* Package.SubPackage.Class


`Key` can be related to Windows *`Control`* or OS X *`Command`*

### Snippets Macros

The following macros are used inside Javatar snippet file (*.javatar) which will be parsed by plugin and Sublime Text

* %package_path% = Package path
* %file% = File path
* %file_name% = File name
* %class% = Class name
* %package% = Package code (`package java.utils;`)
* All Sublime Text's snippet macros can be used within Javatar snippets. For example: ${1} or ${2://Comment}