## Javatar Coding Guideline

*This document will be affected after the first release of Javatar*

#### Recommended plugins when working with Javatar code
- EditorConfig
   - Auto set the indentation, line ending configurations
- UnitTesting
   - For test the UnitTest test cases before push to remote
- Terminality
   - For running UnitTest easier by just pressing key

#### Coding

**TL;DR** Just code like the rest of the plugin

- Conventions
   - Commands starts with `Javatar`
   - Use `QuickMenu` as much as possible (except make the changes hard to edit in the future)
   - Variable name, function/method name, and source code file name in `underscore_case`
   - Class name in `TitleCase`
   - Sublime Text's imports on top follows by default imports then required imports
   - Use 4 spaces as 1 indent
   - Preferred 80x80 code size per method/function or smaller
   - Preferred `{` on the same line as assignment and `}` aligned with the assignment *[1]*
   - Preferred `Dict` over `Tuple` or `List` when work with strings to make code more readable and also support localization (if any)
   - Comment the code as a summarize of functionality of that method/class (if that method/class contains parameters, each parameter should be described too)

- Project Structure
   - `commands`
     - A collection of commands which sub-structure inherit from menu
   - `core`
     - A collection of classes which planned in ClassIdeas
     - All classes should be a feature-related class, a data structure class or a class that is required to be used earlier on startup
   - `Developers`
     - All development-related files will put in here
     - This folder structure intend for developers' use only
     - **Beware!** That this folder must not push to `master` or `release` branch
   - `grammars`
     - A collection of language grammars that required within plugin
   - `menu`
     - A collection of menus that will be used within plugin
   - `messages`
     - A release changelog and installation messages will put in here
   - `parser`
     - A subtree of `GrammarParser` repository 
   - `QuickMenu`
     - A subtree of `QuickMenu` repository 
   - `snippets`
     - A collection of Javatar snippets that will be used within plugin
   - `syntax`
     - A collection of syntaxes that are used within plugin
   - `tests`
     - A UnitTest test cases and its stubs
   - `utils`
     - A collection of small classes to helps with `core` classes
     - Any (very) small functions should be put inside `utils` class instead of create an explicit class for it

#### Version Control (git)

- **Do not** commit any *developers' notes* outside `develop`, `feature` and `experiment`
- Branches
   - `master` is for public deployments. This branch **should not** contains any error or any uncomplete feature
   - `hotfix` is for `master` bug fixes. This branch should contains **only** bug fixes for `master`
   - `develop` is for development releases. This branch **should not** contains any error but has new features that will become `release`
   - `feature` is for feature developments. This branch **should not** push to remote repo. Any new feature under development should be working in this branch
   - `experiment` is for idea testings. This branch will **only** merge into `feature` branch. Any developer who **do not** familier with git should be working on this branch
   - `release` is for release milestones. This is the **only branch** that will be merged into `master`. **No one** should be working on this branch
- Merge, Rebase and Pull Requests
   - `hotfix` should be **branched** from `master` and will be **merged** into `master`, `release` and `develop` once the fix is done
   - `develop` will be **merged** into `release` once the features is considered a new release
   - `feature` will be **rebase** onto `develop` once the feature is finished
   - `experiment` preferred to **merged** into `feature` once the experiment considered a good feature to have
   - `release` and `master` will be merged after `develop` has been passed the tests
   - All pull requests **must** pass the tests **before** merge into `develop`, `release` or `master`
   - `master` and `release` must contains a tag

---
*[1]*: Example:

```
visibility_map = {
    ...
}
```
