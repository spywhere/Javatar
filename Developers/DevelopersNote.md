## Javatar Developers' Note

### First release remaining features
- Selectable Output Console View

### New Features:
- Documentation
  - Coding Guideline
  - New JavatarDoc
  - Code Comment
- Code Core
  - Maven support
  - Git feature branching
  - Fully pep8 compatible (if possible)
  - Unit tests - small functions are easier to test
  - Logging Utilities
  - Work-based class design
  - Shell Manager
  - Status Manager
- Features
  - Language Localization
  - Multiple Source Folders
  - Organize Imports with static imports
  - Rename/Move packages or classes [*1*]
  - .jar file export (includes executable .jar) [*2*]
  - Dynamic method call auto-complete
  - Generate all interfaces method when create an inherited class
  - Class Finding (`Ctrl+H` in eclipse)
  - JUnit support
  - JVM Language compatible (not soon)

### Feature Description
##### Git feature branching
- `master` for production release
- `hotfix` for bug fixes
- `dev` for next release
- `feature` for new features that will be added to `dev`
- `experiment` for an experiment that might be added to `feature`

##### Logging Utilities
Debug, Error, Warning, Info logging class. Amount is based on settings.

##### Work-based class design
Create a class based on its work.

- `utils/java.py` Java Utilities
- `commands/operations/organize_imports.py` Organize Imports command
- etc.

##### Multiple Source Folder
Allows user to use multiple folders as source folders

##### Shell Manager
Manage shell instances and show proper status bar text (# Javatar Shell(s) is running...)

##### Status Manager
Manage multiple status text by cycle it properly
Might add [#/#] before status text to indicate multiple statuses

##### Selectable Output Console View
Output console in another view settings

```
"output_console_group": [
    //In [Group:View] or [Group] format
    //Prioritize from top to bottom
    0:0
    0
    1:1
    2:2
]
```

##### Organize Imports
TODO:

- Performances
- Option to create new classes or enter manually when class not found
- [Done/Need Check] duplicate imports between default imports and same package classes (prefer same package)
- Import classes from external .jar/classes files [*3*]
- Custom default import settings

Allow to include a javatar-packages files into project (at least easier for bukkit autocomplete)

Allow a new javatar format for packaging a custom jar file (at least easier for bukkit plugin jar file)

##### .jar File Export
Create .jar using "jar" command
[http://docs.oracle.com/javase/7/docs/technotes/tools/windows/jar.html](http://docs.oracle.com/javase/7/docs/technotes/tools/windows/jar.html)

##### Class Finding
Search for class in project

##### Dynamic method call auto-complete
Using "javap" to decompile .class file and get some informations about it

Exclude package - Exclude all classes inside (increase searching speed and performance)

<hr>
*1*: Auto-refactor is not included<br>
*2*: Export as executable JAR may delay after normal JAR export feature is finished<br>
*3*: Import from external .jar/classes is not supported
