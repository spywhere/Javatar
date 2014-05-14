## QuickMenu

A quick panel utility for Sublime Text 3 packages

![QuickMenu](http://spywhere.github.io/images/QuickMenu.png)

### Features
 * Submenu, Redirecting items
 * Dynamic menu system

### Installation and Package Integration
Place this file inside `QuickMenu` folder in your package project and import into your package by using `from QuickMenu.QuickMenu import *` or similar.

You should include all QuickMenu files in your project since this packages is only for package developer.

**IMPORTANT: QuickMenu is not update itself when use. Please check this repository for an update.**

### Setup Menus
To setup a menu, you will need a menu and variable to store an instance of QuickMenu.

	qm = None

To create a menu just using Dict with one element with your menu name as a key with a list of item inside.

	menu = {
		"<Menu Name>": {
			"items": <List of item you want to display just like in quick panel>
		}
	}
	
and when you are ready to show it just using...

	if self.qm is None:
		self.qm = QuickMenu(self.menu)
	self.qm.show(self.window) # for WindowCommand
	# or
	self.qm.show(sublime.active_window()) # for another type of command
	
**IMPORTANT: Every menu must have "main" as a startup menu**

### Setup Menu Interaction
Once you have a menu to display, you will need some interactions with it, like go to submenu or run commands. To make items interactible, add a new list named "actions" into your menu.

	menu = {
		"<Menu Name>": {
			"items": <List of items you want to display just like in quick panel>
			"actions": [<List of actions order by item's index>]
		}
	}

and then add an action order by your item's index. (Action format see below)

### Action Format
Item action can be use in many ways. These are all possible actions can be used by your items...

* Open a submenu
* Select an item from other submenu (redirect)
* Show a message dialog
* Show an error dialog
* Run command (with arguments)

#### Submenu
To make items go to a submenu, use a Dict with string named "name"...

	{
		"name": "<Menu Name>"
	}

#### Redirecting
To make items redirect itself to another item on the same or different submenu, use a Dict with following format...

	{
		"name": "<Menu Name>",
		"item": <A index of item starts from 1>
	}

#### Message Dialog
To make items show a message dialog, use a Dict with following format...

	{
		"command": "message_dialog",
		"args": "<Your text goes here>"
	}
	
#### Error Dialog
To make items show an error dialog, use a Dict with following format...

	{
		"command": "error_dialog",
		"args": "<Your text goes here>"
	}
	
#### Run Command
To make items run a command, use a Dict with following format...

	{
		"command": "<Your command goes here>",
		"args": <A Dict of arguments>
	}
	
### Example
You can see and try an example of QuickMenu within file named "QuickMenu_main.py" or type `QuickMenu: Example Code` in command pallete.

### API
#### Constructor
	QuickMenu(defaultMenu=[], silentMode=False, saveSelected=True, maxRecursionLevel=50)
* defaultMenu
	* Default menu Dict to display (starts with menu named "main")
* silentMode
	* Set to 'False' to show all messages if invalid item or invalid menu is selected
* saveSelected
	* Set to 'True' to remember selected item
* maxRecursionLevel
	* Stop the self recursion menu if it goes deep to this number.

#### Methods
##### Set a new default value
	set(key, value)
* key
	* A key to set ("menu" to set a new defaultMenu, "silent" to set a new silentMode or "max_level" to set a new maxRecursionLevel)
* value
	* A new value to be set

##### Set a new menu
	setMenu(name, menu)
* name
	* A name of menu to be set
* menu
	* A new menu to be set

##### Set items
	setItem(menu, items, actions)
* menu
	* A name of menu to be set
* items
	* Items list to be set
* actions
	* Action list to be set with items
##### Add items
	addItems(menu, items, actions)
* menu
	* A name of menu to be set
* items
	* Items list to be set
* actions
	* Action list to be set with items

##### Show a menu
	show(window=None, on_done=None, menu=None, action=None, flags=0, on_highlight=None)
* window
	* A window to show quick panel
* on_done
	* A callback when item is selected (must received one argument as a Dict)
* menu
	* A passing menu
* action
	* A passing action
* flags
	* A quick panel's flags
* on_highlight
	* A callback when highlight an item 

### License

	::QuickMenu::
	
	The MIT License (MIT)
	
	Copyright (c) 2014 Sirisak Lueangsaksri
	
	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:
	
	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.
	
	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.