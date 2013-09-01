## Javatar

### Status: Beta

A Sublime Text 3 Plugin for Java Development

### Features
 * [+] Package, SubPackage creation
 * [+] Class (also Abstract), Interface, Enumerator snippets with packge/class auto-complete
 * [+] Project Compile
 * [-] JAR file export (included executable)
 * [*] Rename/Move packages/classes
 * [+] Package path in status bar

[+] Fully working<br />
[*] Work in progress<br />
[-] Unavailable at this moment

### Screenshots

#### Creating packages in action
![CreatePackage](http://spywhere.github.io/images/CreatePackage.gif)
#### Creating classes in action
![CreateClass](http://spywhere.github.io/images/CreateClass.gif)
#### Creating other classes in action
![CreateOther](http://spywhere.github.io/images/CreateOther.gif)
#### Class operations in action
![Operation](http://spywhere.github.io/images/Operations.gif)

### Commands
* Build
	* Build is mostly use for project or package build since class build can be accessed by default shortcut key (Control+B or Command+B)
	* Build commands can be accessed via command palette only
* Call
	* Call is used to insert any information about package and class
	* Mostly accessed by shortcut keys (see below)
* Packages/Classes Creation
	* Packages/Classes can be create via command palette only
* Packages/Classes Operation
	* Operation is used to edit current java file like correcting invalid class name or package path

#### Commands List

The following commands can be accessed via *Command Palette* (Control+Shift+P or Super+Shift+P)

* Build...
* Call...
* Create new...
* Operations...
* Create Package
* Create (Abstract) Class/Interface/Enumerator

*All commands will be prefixed by "Javatar: " in order to prevent conflict with another plugins*<br />
*Did you know? You can type "Javatar:" in command palette to see all available commands*

#### Javatar Call

Javatar Call is used to insert any information about packages and class like full package path and class name at your cursor point. Javatar Call supports 4 type of data you can insert which are `Full Package Path`, `Current Package Name`, `Class Name` and `Full Class Name`

#### Javatar Operations

Javatar Operations is a command that helps you edit current java file. Javatar Operations supports only one operation at this moment (more to come soon!) which is `Correct Class`

**Operations List**

* Correct Class
	* Change class name correspond to file name and change package to proper package location

#### Advanced Creation

In creation mode, all packages/classes will be created relative to current package. If you want to create from default package (root package), you must specify `~` (tilde) before package/class name. It's also able to create packages/classes corresponded to package path as example below

Input: `Alpha`<br />
Result as Class: `Class "Alpha" is created in current package`<br />
Result as Package: `Package "Alpha" is created in current package`

Input: `~Beta`<br />
Result as Class: `Class "Beta" is created in default package`<br />
Result as Package: `Package "Beta" is created in default package`

Input: `me.spywhere.Alpha`<br />
Result as Class: `Class "Alpha" is created in "(current package).me.spywhere" package`<br />
Result as Package: `Package "Alpha" is created in "(current package).me.spywhere" package`

Input: `~me.spywhere.Beta`<br />
Result as Class: `Class "Beta" is created in "me.spywhere"`<br />
Result as Package: `Package "Beta" is created in "me.spywhere"`

### Default Package Detection

Javatar will specify default package from project folder in your project file. If project file is not found, it will specify current folder which contains current working file as default package. If current folder is not found, it will specify current package as `(Unknown Package)`. Create packages/classes within unknown package will cause Javatar to refuse to create packages/classes. In that case, mostly because file is not on the disk yet.

### Installation
You can install Javatar via [Sublime Package Control](https://sublime.wbond.net/installation) or by clone this repository into your *Sublime Text 3 / Packages* folder

	cd PACKAGES_PATH
	git clone git://github.com/spywhere/Javatar.git
	
PACKAGES_PATH is related to folder which can be accessed via the *Preference > Browse Packages...*

### Settings
Settings are accessed via the *Preferences > Package Settings > Javatar* or via command palette by type *"Preference Javatar"*

Default settings should not be modified. However, you can copy the relevant settings into Javatar's user settings file

#### Key Bindings
You can access keymap via the preference menu or via command palette same as settings

**Default Key Binding**

*All commands start with `Key+Shift+K` then follows by their shortcut key*

* Build... : `Key+Shift+B`
	* This will open quick panel to select which build you want to perform
* Call... : `Key+Shift+J`
	* This will open quick panel to select which data you want to insert
* Create new... : `Key+Shift+L`
	* This will open quick panel to select which class you want to create
* Operations... : `Key+Shift+O`
	* This will open quick panel to select which operation you want to perform
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

### Build System

Javatar's build system use Sublime Text execute command to build your classes. Javatar build parameters are based on default Sublime Text's JavaC build settings. You can change the build command via Javatar settings file

*Please note that Javatar project/package build cannot show any compilation errors (or may show only last built class) since it build all your classes in order*

### Snippets

Javatar snippets is a dynamic snippet which will change part of the file to correspond with package path and class name. By using macros, you can specify which part of the file you want to fill the data to.

You can make your own snippet to use within Javatar by create a new file ends with `.javatar`

Snippet class tag (for more informations about snippet tags, see below) will be used as a type of classes which show in input panel when create a new file (`%type% Name:`), on error dialog (`%type% %name% already exists`) and in status bar when file was created (`%type% %name% is created within package %package%`).

Example of Javatar's snippets is inside Javatar's snippets folder (`PACKAGE_PATH/Javatar/snippets` or similar)

#### Snippet Tags

The following tags are used inside Javatar snippet files (*.javatar) which will be used by Javatar to display proper command to the user

* %class:*TYPE OF CLASS*%
* %description:*DESCRIPTION TO SHOW UNDER CREATION COMMAND*%

##### Usage of snippet tags in action
![CreateNewSS](http://spywhere.github.io/images/CreateNewSS.jpg)


#### Snippet Macros

The following macros are used inside Javatar snippet files (*.javatar) which will be parsed by Javatar and Sublime Text

* %package_path% = Package path
* %class% = Class name
* %file% = File path
* %file_name% = File name (equivalent to `%class%.java`)
* %package% = Package code (for example `package java.utils;` or same as `package %package_path%;`)
* All Sublime Text's snippet macros can be used within Javatar snippets. For example: ${1} or ${2://Comment}