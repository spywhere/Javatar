## Javatar Coding Guideline

*This document will be affected after the first release of Javatar*

#### Recommended plugins when working with Javatar code
- EditorConfig
   - Auto set the indentation, line ending configurations
- UnitTesting
   - For test the UnitTest test cases before push to remote
- Terminality
   - For running UnitTest easier by just pressing a key

#### Coding

**TL;DR** Just code like the rest of the plugin

- Conventions
  - Commands start with `Javatar`
  - Use `QuickMenu` as much as possible (except make the changes hard to edit in the future)
  - Threads must be inside a `threads` directory in which all related threads combine into one class with their responder as a file name *[1]*
  - Variable, function/method, and source code file names in `underscore_case`
  - Class names in `TitleCase`
  - Sublime Text's imports on top, follows by standard Python's imports and then required imports (sequence is required but sorting is optional)
   - Use 4 spaces as 1 indent
   - Preferred 80x80 code size per method/function or smaller
   - Preferred `{` on the same line as assignment and `}` aligned with the assignment *[2]*
   - Preferred `dict` over `tuple` or `list` when work with strings to make code more readable and also support localization (if any)
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
   - `extensions`
     - A collection of 3rd-party package extensions
   - `grammars`
     - A collection of language grammars that required within a plugin
   - `menu`
     - A collection of menus that are used within a plugin
   - `messages`
     - A release changelog and installation messages will put in here
   - `parser`
     - A subtree of `GrammarParser` repository 
   - `QuickMenu`
     - A subtree of `QuickMenu` repository 
   - `snippets`
     - A collection of Javatar snippets that are used within a plugin
   - `syntax`
     - A collection of syntaxes that are used within a plugin
   - `tests`
     - A UnitTest test cases and its stubs
   - `threads`
     - A collection of threads that are used within a plugin
   - `utils`
     - A collection of small classes to helps with `core` classes
     - Any (very) small functions should be put inside `utils` class instead of create an explicit class for it

#### Version Control (git)

**Update:** On 23 March 2015, Javatar now using `master` branch instead of `develop` branch. This will make git seem frequently update instead of sudden update and easy to track on the website. This also reduce unneccessary branching (previously `master` and `release` is exactly the same).

- **Do not** commit any *developers' notes* outside `master`, `feature` and `experiment`
- Branches
  - `release` is for public deployments. This branch **should not** contains any error or any uncomplete feature
  - `hotfix` is for `release` bug fixes. This branch should contains **only** bug fixes for `release`
  - `develop` branch is now deprecated. **No one** should work on this branch anymore.
  - `master` is for development releases. This branch **should not** contains any error but has new features that will become `release`
   - `feature` is for feature developments. This branch **should not** push to remote repo. Any new feature under development should be working in this branch
   - `experiment` is for idea testings. This branch will **only** merge into `feature` branch. Any developer who **do not** familier with git should be working on this branch
  - `release` is for release milestones. **No one** should be working on this branch
- Merge, Rebase and Pull Requests
  - `hotfix` should be **branched** from `release` and will be **merged** into `master` and `release` once the fix is done
  - `master` will be **merged** into `release` once the features is considered a new release
  - `feature` will be **rebase** onto `master` once the feature is finished
   - `experiment` preferred to **merged** into `feature` once the experiment considered a good feature to have
  - `release` will be merged after `master` has been passed the tests
  - All pull requests **must** pass the tests **before** merge into `master` or `release`
  - `release` must contains a tag

---
*[1]*: PackagesInstallerThread, PackagesLoaderThread, etc. are reside in a `packages_manager.py` file since PackagesManager is using these threads hence it is a responder for the threads.

*[2]*: Example:

```
visibility_map = {
    ...
}
```
