# Commit Message Convention

This repository follows the [Conventional Commits](https://www.conventionalcommits.org/) specification. Each commit message should be structured as follows:

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Types

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code (formatting, etc)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `build`: Changes that affect the build system or external dependencies
- `ci`: Changes to our CI configuration files and scripts
- `chore`: Other changes that don't modify src or test files
- `revert`: Reverts a previous commit

## Scope

The scope should be the name of the affected component in kebab-case.

Examples:
- `feat(timeline): Add task resizing functionality`
- `fix(auth): Resolve login redirect issue`
- `docs(api): Update authentication documentation`

## Subject

The subject contains a succinct description of the change:
- Use the imperative, present tense: "change" not "changed" nor "changes"
- Don't capitalize the first letter
- No dot (.) at the end

## Body

The body should include the motivation for the change and contrast this with previous behavior.

## Footer

The footer should contain any information about Breaking Changes and is also the place to reference GitHub issues that this commit Closes.

Breaking Changes should start with the word `BREAKING CHANGE:` with a space or two newlines. The rest of the commit message is then used for this.

## Examples

```
feat(timeline): Add drag-and-drop task scheduling

Implement drag-and-drop functionality for task scheduling in the timeline view. 
This allows users to easily reschedule tasks by dragging them to a new date.

Closes #123
```

```
fix(workload): Correct resource allocation calculation

The workload percentage was being incorrectly calculated when tasks spanned multiple days.
Now properly distributes the hours across the task duration.

BREAKING CHANGE: The workload calculation API now returns an object with daily distributions 
instead of a single number.
```
