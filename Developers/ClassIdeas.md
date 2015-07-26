## Javatar Class ideas

#### MergeDict [Implemented but without abstract class]
Merge 2 dictionaries together and use as a single dictionary

TODO:

- Must create an abstract class

#### Settings [Implemented]
##### Settings(key=None, global=None, local=None)
Get the settings by default (`key` selector), global settings (`global` selector) or local settings (`local` selector)

Set the settings by set value to key as a tuple/list

##### Example

Get JDK installation paths

```
jdks = Settings(key="jdk_installation_path")
```

Set new source folders

```
Settings(key=("source_folders", ["/user/spywhere/"]))
```

#### Parser
Get any parser-related informations (like class name, package)

##### Parser()
Parse current document (if not yet) and pass document info

#### Timer [Implemented]
For startup time counting and future use

#### Project [Implemented as StateProperty]
For store/retrieve project data (such as source folders, root package)

#### Status [Implemented as StatusManager]
##### Status(key, value, delay)
Set the value to key and cycle status from all keys

#### Validator [Implemented as StateProperty]
Get current state of Sublime Text (such as is project, is view opened)

#### ThreadProgress [Refactored but require rewrite for more suitable]
TODO:

- Create an abstract class for each type

#### News
Check and show news

#### Shell [Use GenericShell instead]
TODO:

- Create an abstract class

#### Snippets
Add more field data %handler:[HandlerFunction]% to allows custom action on each snippets

#### Macro [See Terminality implementation]
##### Macro(key="")
Get macro output

```
Macro(key="test %project_dir%")
# test /user/spywhere/...
```

#### Logger [Implemented]
Log messages in proper situation (debug, info, error, warning)

#### Constant [Implemented]
Provides all constants throughout the Javatar (such as version, news, etc.)
