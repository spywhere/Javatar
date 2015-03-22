## Javatar Class ideas

#### MergeDict
Merge 2 dictionaries together and use as a single dictionary
TODO:

- Must create an abstract class

#### Settings
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

#### Timer
For startup time counting and future use

#### Project
For store/retrieve project data (such as source folders, root package)

#### Status
##### Status(key, value, delay)
Set the value to key and cycle status from all keys

#### Validator
Get current state of Sublime Text (such as is project, is view opened)

#### ThreadProgress
TODO:

- Create an abstract class

#### News
Check and show news

#### Shell
TODO:

- Create an abstract class

#### Snippets
Add more field data %handler:[HandlerFunction]% to allows custom action on each snippets

#### Macro
##### Macro(key="")
Get macro output

```
Macro(key="test %project_dir%")
# test /user/spywhere/...
```

#### Logger
Log messages in proper situation (debug, info, error, warning)

#### Constant
Provides all constants throughout the Javatar (such as version, news, etc.)