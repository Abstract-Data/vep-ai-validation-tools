# GitHub Pages Setup Guide

This repository is configured to automatically build and deploy documentation using GitHub Pages when you push to the main/master branch.

## Enabling GitHub Pages

To enable GitHub Pages for this repository, you need to configure it in your repository settings:

### Step 1: Access Repository Settings

1. Go to your repository on GitHub
2. Click on the **Settings** tab
3. Scroll down to the **Pages** section in the left sidebar

### Step 2: Configure Pages Source

1. Under **Source**, select **GitHub Actions**
2. Save the configuration

### Step 3: Verify Setup

1. Once enabled, any push to the main/master branch will trigger the documentation workflow
2. Your documentation will be available at: `https://<username>.github.io/<repository-name>/`

## Current Status

If you're seeing workflow failures for the Documentation workflow, it's likely that GitHub Pages hasn't been enabled yet. The documentation builds successfully, but the deployment step fails without Pages enabled.

## Troubleshooting

### Documentation Workflow Fails

- **Cause**: GitHub Pages not enabled
- **Solution**: Follow the steps above to enable GitHub Pages
- **Error Message**: `Failed to create deployment (status: 404)`

### Documentation Doesn't Update

- **Cause**: Workflow not triggering or failing
- **Solution**: Check the Actions tab for workflow status
- **Check**: Ensure you're pushing to main/master branch

### Local Documentation Build

You can build the documentation locally to test changes:

```bash
# Install dependencies
uv sync --extra docs

# Build documentation
cd .docs
uv run sphinx-build -b html source build/html

# View locally
open build/html/index.html  # macOS
# or
xdg-open build/html/index.html  # Linux
```

## Documentation Structure

- `.docs/source/` - Sphinx source files
- `.docs/source/conf.py` - Sphinx configuration
- `.docs/source/index.rst` - Main documentation index
- `.docs/build/html/` - Built HTML files (generated)

## Customizing Documentation

To customize the documentation:

1. Edit files in `.docs/source/`
2. Add new pages and reference them in `index.rst`
3. Modify `conf.py` for Sphinx settings
4. Use either reStructuredText (.rst) or Markdown (.md) files

The documentation uses the Sphinx RTD theme and supports both reStructuredText and Markdown via MyST parser.
