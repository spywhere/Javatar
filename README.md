## Javatar

### Status: Beta

A Sublime Text 3 Plugin for Java Development

====

### Table of Contents
* Features
* Important Updates
* Screenshots
* Command Categories
* Javatar Builds
* Javatar Calls
* Advanced Creations
* Javatar Operations
* Project Settings
* Default Package Detection
* Installation
* Settings
* Key Bindings
* Build System
* Javatar Shell
* Javatar Snippets
* Javatar Packages
* Additional Packages
* Package Channels
* Statistics and Usages Policy
* Actions History

===

### Features
* [+] Package, Subpackage creation
* [+] Class (also Abstract), Interface, Enumerator snippets with package/class auto-complete
* [+] Project/Package/Class Build
* [+] Package path in status bar
* [+] External libraries packages
* [*] Internal Console with input supports
* [*] Organize Imports
* [*] Rename/Move packages/classes
* [-] JAR file export (included executable)
* [-] Dynamic method call auto-complete

[+] Available on Stable Channel<br />
[*] Partial available on Development Channel<br />
[-] Planned

====

### Important Updates/Changelogs

From 11 Apr 2014, Javatar will "NOT" include any packages inside its package. This helps install and update Javatar faster but still maintaining default features. Javatar will automatically download and install necessary packages (Java SE) at startup since users install Javatar usually already connected to the internet.

##### Development Build
* New feature, Run main class. Can be accessed via *Development Section... > Builds: Run Main Class* (more details on Javatar Shell)
* To force quit your application when run, just close the console view.
* Java's StackTrace highlighting

##### Stable Build
* Project/Package/Class Build improvements (now support multiple files building and error logs) *Please report an issue if you found something broken (this feature using internal shell so it might not work same as Sublime Text's shell)*
* New build type, Working Classes
* Building output highlighting
* Fixed Javatar Calls cannot find the right package name and class name
* Package channel must be specified 'dev' in order to subscribe to development channel instead of anything else except 'stable'
* Class name detection improvements
* Java file validation improvements
* Building system now completely changed to internal building system (more details on Build System section below)
* Some code tweaks

====

### Screenshots
##### Creating packages in action
![CreatePackage](http://spywhere.github.io/images/PackageCreate.gif)
##### Creating classes in action
![CreateClass](http://spywhere.github.io/images/ClassCreate.gif)
##### Creating other classes in action
![CreateOther](http://spywhere.github.io/images/OtherClassCreate.gif)
##### Class operations in action
![Operation](http://spywhere.github.io/images/Operations.gif)

====

### Command Categories
* Build:
	* Build classes within package or project
	* More details on Javatar Builds
* Call:
	* Insert class and package informations such as current class path, class name or package name
	* More details on Javatar Calls
* Creation:
	*  Packages and classes creation
	* More details on Advanced Creations
* Operation:
	* Do class or package operation such as organize imports, rename class or package
	* More details on Javatar Operations
* Project Settings: Accessed via quick menu only
	* Adjust settings for current project
	* More details on Project Settings
* Packages Manager: Accessed via quick menu only
	* Download, install or uninstall Javatar packages and Tools for package creators.
	* More details on Additional Packages

====

### Javatar Builds
Javatar use its own build system which based on default Sublime Text's JavaC build settings.

===

### Javatar Calls
Javatar Calls are use to insert class or package informations at cursor point. Javatar supports 4 types of informations to insert which are `Full Package Path`, `Current Package Path`, `Full Class Name` and `Class Name`.

===

### Advanced Creations
In create menu, all packages and classes will be created relative to current package unless specified by `~` (tilde) before package or class path. See examples below...

Input: `Alpha`<br />
Result as Class: `Class "Alpha" is created in current pacakge`<br />
Result as Package: `Package "Alpha" is created in current package`

Input: `~Beta`<br />
Result as Class: `Class "Beta" is created in default pacakge`<br />
Result as Package: `Package "Beta" is created in default package`

Input: `me.spywhere.Alpha`<br />
Result as Class: `Class "Alpha" is created in "(current package).me.spywhere" package`<br />
Result as Package: `Package "Alpha" is created in "(current package).me.spywhere" package`

Input: `~me.spywhere.Beta`<br />
Result as Class: `Class "Beta" is created in "me.spywhere"`<br />
Result as Package: `Package "Beta" is created in "me.spywhere"`

===

### Javatar Operations
Javatar Operations help you do class or package operations, such as organize imports or rename class easier. Currently, Javatar has 2 operations, `Correct Class` and `Organize Imports`.

##### Correct Class
Javatar will search for current package and your class name based on file name and location of current file and correct it on first class.

##### Organize Imports
Javatar will automatically imports all necessary packages and remove unused packages for you. This is done within 7 sub-steps.

1. Javatar gathering imports informations from current file
2. Javatar let's you select a package that has the same class
3. Javatar imports "default imports" and Java's packages
4. Javatar asks you to enter package name for missing classes
5. Javatar asks for package name that you want to enter manually
6. Javatar clear all imports in current file
7. Javatar imports all packages that has been processed within step 1-4

====

### Project Settings
Project Settings section contains per-project settings. Currently, Javatar supported only 1 settings, `Set Source Folder`.

##### Set Source Folder
As default, Javatar will specified a default package (mostly) based-on current working folder or folder contains current working file (more details on next section). Many projects might use multiple folders and some of them are not source folder. Set source folder helps solve this issue by let you select which folder to specified as Source Folder (or default package as Javatar use).

===

###  Default Package Detection
Javatar will specify default package with these steps...

1. Source Folder specified in current project file (when open project)
2. Project folder in current project file (when open project or folder)
3. Folder contains current file (when open file)
4. Specify current package as `(Unknown Package)`

Javatar will refuse to create packages or classes within unknown package. In this case, mostly because current file is not on the disk yet.

====

### Installation
##### Package Control (Recommended)
Open command palette and type `Install Package` then type `Javatar` and hit Enter/Return. Package Control will automatically download, install and update for you.

##### "git" Command
Open your favourite Terminal application, browse to PACKAGES_PATH and run this command.

	git clone git://github.com/spywhere/Javatar.git

##### Manual Install
Download .zip file from Javatar repository and browse to PACKAGES_PATH, extract .zip file and rename folder to `Javatar`, restart Sublime Text if you are currently open.

**Note!** PACKAGES_PATH is referred to folder which can be accessed via the *Preferences > Browse Packages...*

====

### Settings
Settings can be accessed via the *Preferences > Package Settings > Javatar* or via command palette by type *"Preference Javatar"*.

Default settings should not be modified. However, you can copy the relevant settings into Javatar's user settings file.

====

### Key Bindings
Key bindings can be accessed via the preference menu or via command palette same as settings.

##### Default Key Binding
*All commands start with `Key+Shift+K` then follows by their shortcut key.*

* Browse Commands... : `Key+Shift+K`
	* This will open quick panel, showing you all commands available to use.
* Help and Support... : `Key+Shift+H`
	* This will open quick panel, showing you all utilities that help solve the issue. (mostly requested to do by developer)
* Builds... : `Key+Shift+B`
	* This will open quick panel to select which build you want to perform.
* Calls... : `Key+Shift+J`
	* This will open quick panel to select which information you want to insert.
* Operations... : `Key+Shift+O`
	* This will open quick panel to select which operation you want to perform.
* Create new... : `Key+Shift+N`
    * This will open quick panel, showing you all possible types to create.
* Create new package : `Key+Shift+P`
	* This will open input panel, just like when you create a new package.
* Organize Imports : `Key+Shift+I` (Only on development channel)
	* This will organize imports on current file.

`Key` is `Control` on Windows, `Super` on Linux and `Command` on OS X

====

### Build System
Javatar's build system use its internal shell to build your classes. Javatar build parameters are based on default Sublime Text's JavaC build settings. You can change the build command via Javatar settings file.

While building, Javatar will show building progress in Sublime Text's status bar. If it found any error while building, Javatar will show you a new view contains all errors and will keep on printing until building is complete. To cancel building in progress, just close a error logs view and Javatar will stop building your classes immediately.

**Please note that Javatar cannot be stopped if there is no error occurred**

===

### Javatar Shell

Javatar shell is working like proper shell terminal. The difference between Javatar's shell and another shells is Javatar's shell will send your input by pressing Enter/Return (that give you ability to reedit your content on current line).

**We cannot gurranteed that output or input is corrected when you are enter while terminal is printing an output from the shell. Since, Javatar's shell is not set the view to Read-Only while printing**

===

### Javatar Snippets

Javatar snippets is a dynamic snippet which will change part of the file to correspond with package path and class name. By using macros, you can specify which part of the file you want to fill the data to.

You can make your own snippets to use within Javatar by create a new file ends with `.javatar`

Snippet class tags (for more informations about snippet tags, see below) will be used as a type of classes which show in input panel when create a new file (`%type% Name:`), on error dialog (`%type% %name% already exists`) and in status bar when file was created (`%type% %name% is created within package %package%`).

Example of Javatar's snippets is inside Javatar's snippets folder (`PACKAGES_PATH/Javatar/snippets` or similar)

#### Snippet Tags

The following tags are used inside Javatar snippet files (*.javatar) which will be used by Javatar to display proper command to the user

* %class:*TYPE OF CLASS*%
* %description:*DESCRIPTION TO SHOW UNDER CREATION COMMAND*%

##### Usage of snippet tags in action
![CreateNewSS](http://spywhere.github.io/images/CreateNewSS.png)


#### Snippet Macros
The following macros are used inside Javatar snippet files (*.javatar) which will be parsed by Javatar and Sublime Text.

* %package_path% = Package path
* %class% = Class name
* %file% = File path
* %file_name% = File name (equivalent to `%class%.java`)
* %package% = Package code (for example `package java.utils;` or same as `package %packages_path%;`)
* All Sublime Text's snippet macros can be used within Javatar snippets. For example: ${1} or ${2://Comment}

===

### Javatar Packages
Javatar required packages file (*.javatar-packages) to correctly import necessary Java's packages. These files contain all classes, fields, methods and packages to use with Javatar.

Javatar Packages file is a JSON file. You can read more details about each key and value in Proto.javatar-packages located within Javatar's Java folder (can be accessed via *Preferences > Package Settings > Proto.javatar-packages* or via command palette by type *"Javatar Proto"*).

However, their are 2 special keys that are not normally used within Javatar Packages which are...

* experiment
	* Set this to `true` to exclude this package from Javatar's packages list.
* always_import
	* Set this to `true` to always import this package even no class is used (this will import as `package.*`).

Both keys are boolean type and also optional to use.

Example of Javatar Packages is located inside Javatar's Java folder (`PACKAGES_PATH/Javatar/Java`)

===

### Additional Packages
By default, Javatar is not include any additional packages inside its package. This helps Javatar faster to install/update from Package Control but that not provides any support for some features (for example, Organize Imports). To solve this problem, Javatar will automatically download and install necessary packages when startup. For other packages, you can download and install using *Packages Manager... > Install Packages...* menu.

===

### Package Channels
#### Stable Channel
Stable channel is a default channel for every user who installed Javatar. This channel will release only fully working features and hide all incomplete features.

#### Development Channel
Development channel is a optional channel for user who want to try upcoming features which may not fully working or need improvements. All upcoming features will appear in *Javatar: Browse Commands > Development Section* only.

Please note that stable channel update notes also apply on development channel too.

#### Package Updates Notifications
In order to notice important notes to all users, in stable channel or development channel or both, Javatar use custom notification system which will notice you *only once* when Javatar is ready to use. You can opt out this notification by settings `message_id` to `-1` in Javatar's user settings file, note that you can see update notes in README file or you will miss further important update notes.
 
===
 
### Statistics and Usages Policy
From 13 Apr 2014, Javatar will collect statistics and usages of Javatar to help improve the package features. Data we have collected are your Javatar's settings and Sublime Text informations. To disable automatic sending statistics and usages, set `send_stats_and_usages` to `false` and Javatar will not send any statistics and usages anymore. However, additional packages statistics still collected for packages improvements and selections.

===

### Actions History
Actions History tracks how you use Javatar and helps solve the problem. By provides useful informations as request by developer (only when you submit an issue). A Javatar Action History Report will looks similar to this when using it properly...

	## Javatar Report
	### System Informations
	* Javatar Version: `14.04.15.00.29b`
	* Sublime Version: `3059`
	* Package Path: `/Users/USER_NAME/Library/Application Support/Sublime Text 3/Packages`
	* Javatar Channel: `stable`
	* Sublime Channel: `stable`
	* Is Debug Mode: `False`
	* Platform: `osx`
	* As Packages: `True`
	* Package Control: `True`
	* Architecture: `x64`
	* Javatar's Parent Folder: `Javatar`
	* Is Project: `True`
	* Is File: `True`
	* Is Java: `True`
	
	### Action List
	1. Startup
	2. Reset all settings
	3. Reset all snippets
	4. Reset all default packages
	5. Read settings
	6. Load snippets
	7. Check news
	8. Ready
	9. Javatar snippet AbstractClass.javatar loaded
	10. Analyse snippet [file=Packages/Javatar/snippets/AbstractClass.javatar]
	11. Javatar snippet Class.javatar loaded
	12. Analyse snippet [file=Packages/Javatar/snippets/Class.javatar]
	13. Javatar snippet Enumerator.javatar loaded
	14. Analyse snippet [file=Packages/Javatar/snippets/Enumerator.javatar]
	15. Javatar snippet Interface.javatar loaded
	16. Analyse snippet [file=Packages/Javatar/snippets/Interface.javatar]
	17. Load Java default packages
	18. Javatar default package Proto.javatar-packages loaded
	19. Analyse package [file=Packages/Javatar/Java/Proto.javatar-packages]
	20. Javatar default package JavaSE8.javatar-packages loaded
	21. Analyse package [file=Packages/User/JavaSE8.javatar-packages]
	22. Check packages update

Javatar **do not** automatically send these informations. You have to reply an issue with these informations yourself.

Actions History can be disabled by settings `enable_actions_history` to `false`

===