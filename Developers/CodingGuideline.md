## Javatar Coding Guideline

*This document will be affected after the first release of Javatar*

#### Coding

- Conventions
  - Commands start with `Javatar`
  - Use `QuickMenu` as much as possible (except make the changes hard to edit in the future)
  - Variable, function/method, and source code file names in `underscore_case`
  - Class names in `TitleCase`
  - Sublime Text's imports on top, follows by standard Python's imports and then required imports (sequence is required but sorting is optional)
  - Use 4 spaces as 1 indent
  - Preferred 80x80 code size per method/function or smaller
  - Preferred `{` on the same line as assignment and `}` aligned with the assignment *[1]*
  - Preferred `Dict` over `Tuple` or `List` to make code more readable and also support localization (if any)

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
*[1]*: Example:

```
visibility_map = {
    ...
}
```