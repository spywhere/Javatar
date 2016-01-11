## Javatar Developers' Note

### TODO:

### New Features:
- Documentation
  - New JavatarDoc
  - Javatar Tutorial Videos (if free to do so)
  - [WIP] Code Comment
- Code Core
  - [Done] Travis support
  - [Done] Code Quality (Static Analysis)
  - [WIP] UnitTests - small functions are easier to test
  - [Done] Shell Manager (use MultiThreadProgress instead)
  - [Done] Work-based class design
  - [Done] Git feature branching
  - [Done] Fully pep8 compatible (if possible)
  - [Done] Logging Utilities
  - [Done] Status Manager
- Features
  - [Done] *Remove* Javatar calls (not so useful)
  - [Done] *Remove* Package channel
  - [Done] Better build system
  - [Done] Code linting (via SublimeLinter)
  - [Done] Multiple source folders
  - [Done] Library path supports
  - [WIP] Organize Imports with grouping
  - [Done] Run main class without open the main class
  - [WIP] Extension API
  - [Optional] QuickMenu collect user selections (for stats)
  - [Optional/Major Impact] Rename/Move packages or classes [*1*]
  - .jar file export (includes executable .jar) [*2*]
  - [Done] Build only changed files
  - [Cancelled] Dynamic method call auto-complete
  - Generate all interface methods when create an inherited class
  - Class Finding (`Ctrl+H` in eclipse)
  - [Extension] JUnit support [FAQ](http://junit.org/faq.html)
  - [Optional] Language Localization (not soon except requested)
  - [Done] Action History capture all exception (so it can helps with issues)

### Disclaimer
Final version of features might be differ from the one in this document.

### Feature Description
##### Git feature branching
See ***Coding Guideline*** for more informations

##### Logging Utilities
Debug, Error, Warning, Info logging class. Amount is based on settings.

Errors should be show sequentially after all messages has been show.
Idea:

- Message weight (eg. show error a bit longer than normal message)
- Log all exceptions

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
Must work synchronizely with logging system

Manage multiple status text by cycle it properly

Might add [#/#] before status text to indicate multiple statuses

##### Better Build System
Current build system compile Java file one at a time on a parallel thread. A new one should be able to compile multiple files at once and also possible to compile on a parallel thread. This will decrease time to compile and also improve performance while compiling files.

##### Code Linting
SublimeLinter's JavaC linting treat the Java source code as one, separated, no dependencies file. This make complex source code that involved import external libraries linting error.

##### Organize Imports
TODO:

- Performances
- Option to create new classes or enter manually when class not found
- [Done by let user select it themselve] duplicate imports between default imports and same package classes
- Import classes from external .jar/classes files
- Custom default import settings

##### .jar File Export
Create .jar using "jar" command
[http://docs.oracle.com/javase/7/docs/technotes/tools/windows/jar.html](http://docs.oracle.com/javase/7/docs/technotes/tools/windows/jar.html)

##### Class Finding
Search for class in project

##### Dynamic method call auto-complete
Use external .jar helper file to get class informations. See *JavatarAutocomplete* project

<hr>
*1*: Auto-refactor (references update) is not included
*2*: Export as executable JAR may delay after normal JAR export feature is finished

