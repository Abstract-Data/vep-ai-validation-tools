# 🏷️ Auto-Labeling System

This project uses an automated labeling system to help organize and categorize issues and pull requests. The system automatically applies labels based on file paths, content patterns, and other criteria.

## 🚀 How It Works

The auto-labeling system consists of:

1. **`.github/labeler.yml`** - Configuration file that defines label rules
2. **`.github/workflows/auto-label.yml`** - GitHub Actions workflow that applies labels
3. **Issue and PR Templates** - Structured templates for consistent labeling

## 📋 Available Labels

### 🐍 Code Categories

- **`python`** - Python code changes
- **`server`** - Server and API files
- **`tools`** - Tools and utilities
- **`data`** - Data and models
- **`database`** - Database and storage

### 🔧 Project Management

- **`config`** - Configuration files
- **`ci`** - GitHub Actions workflows
- **`dependencies`** - Package dependencies
- **`documentation`** - Documentation updates

### 🧪 Testing & Quality

- **`testing`** - Test files and updates
- **`bug`** - Bug fixes
- **`feature`** - New features
- **`refactor`** - Code refactoring

### 🔒 Security & Performance

- **`security`** - Security-related changes
- **`performance`** - Performance and optimization
- **`error-handling`** - Error handling and diagnostics

### 🤖 MCP-Specific

- **`mcp`** - MCP-specific files
- **`web-scraping`** - Web scraping and browser automation
- **`file-management`** - File management and search
- **`knowledge-base`** - Knowledge base and AI
- **`media`** - Screenshots and media files
- **`logging`** - Logging and monitoring

### 📝 Change Types

- **`breaking`** - Breaking changes
- **`docs`** - Documentation updates
- **`test`** - Testing updates
- **`security-update`** - Security updates
- **`deps`** - Dependencies update

## 🎯 How Labels Are Applied

### File Path Based

Labels are automatically applied based on the files changed in a PR:

```yaml
# Example: Any Python file gets the 'python' label
python:
  - "**/*.py"
  - "**/*.pyi"

# Example: Documentation files get the 'documentation' label
documentation:
  - "**/*.md"
  - "docs/**/*"
```

### Content Based

Labels are also applied based on file content patterns:

```yaml
# Example: Files with 'fix' in the name get the 'bug' label
bug:
  - "**/*fix*.py"
  - "**/*bug*.py"

# Example: Files with 'feature' in the name get the 'feature' label
feature:
  - "**/*feature*.py"
  - "**/*new*.py"
```

## 📝 Using Issue Templates

### Bug Report Template

When creating a bug report, use the 🐛 Bug Report template:

- Automatically applies `bug` and `🐛` labels
- Includes structured fields for reproduction steps
- Captures system information and logs

### Feature Request Template

When requesting a feature, use the ✨ Feature Request template:

- Automatically applies `enhancement` and `✨` labels
- Includes priority levels
- Captures problem description and proposed solutions

### General Issue Template

For questions and discussions, use the 📝 General Issue template:

- Automatically applies `question` label
- Includes category selection
- Flexible format for various types of issues

## 🔄 Using PR Templates

The PR template includes:

- **Type of Change** checkboxes for automatic categorization
- **Related Issues** linking
- **Testing** checklist
- **Release Notes** section for changelog generation

## 🎨 Customizing Labels

### Adding New Labels

1. Edit `.github/labeler.yml`
2. Add new label rules based on file paths or content patterns
3. Update the workflow summary in `.github/workflows/auto-label.yml`

### Example: Adding a New Label

```yaml
# In .github/labeler.yml
new-feature:
  - "**/new-feature/**/*"
  - "**/*new-feature*.py"
```

### Label Colors and Descriptions

You can customize label colors and descriptions in GitHub:

1. Go to **Issues** → **Labels**
2. Click on a label to edit its color and description
3. Use consistent colors for related labels

## 🔍 Manual Label Management

### Adding Labels Manually

You can always add or remove labels manually:

1. Open an issue or PR
2. Click on the **Labels** button
3. Select or deselect labels as needed

### Label Synchronization

The auto-labeler includes `sync-labels: true`, which means:

- Labels are automatically removed if files no longer match the rules
- Labels are updated when PRs are modified
- The system stays in sync with your changes

## 📊 Label Analytics

### Viewing Label Usage

- Go to **Issues** → **Labels** to see all labels
- Click on a label to see all issues/PRs with that label
- Use GitHub's search to filter by labels: `label:python`

### Label Insights

- Track which areas of your codebase are most active
- Identify common types of changes
- Monitor security and performance improvements

## 🚀 Best Practices

### For Contributors

1. **Use templates** - Always use the provided issue and PR templates
2. **Check labels** - Review automatically applied labels and adjust if needed
3. **Link issues** - Reference related issues in PR descriptions
4. **Update templates** - Suggest improvements to templates if needed

### For Maintainers

1. **Review labels** - Ensure labels are being applied correctly
2. **Update rules** - Refine label rules based on project needs
3. **Monitor usage** - Track which labels are most/least used
4. **Clean up** - Remove unused labels and consolidate similar ones

## 🔧 Troubleshooting

### Labels Not Applied

- Check that the workflow ran successfully
- Verify file paths match the labeler rules
- Ensure the PR is on a supported branch

### Incorrect Labels

- Manually adjust labels as needed
- Update the labeler configuration if rules are wrong
- Report issues with the labeling system

### Workflow Failures

- Check the Actions tab for workflow errors
- Verify the labeler configuration syntax
- Ensure GitHub token permissions are correct

## 📚 Related Documentation

- [GitHub Labeler Action](https://github.com/actions/labeler)
- [GitHub Issue Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository)
- [GitHub PR Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository)
