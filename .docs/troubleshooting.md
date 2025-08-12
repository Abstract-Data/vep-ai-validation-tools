# 🔧 Troubleshooting Guide

This guide helps you resolve common issues with the GitHub Actions workflows and project setup.

## 🚨 Common GitHub Actions Errors

### **GraphqlResponseError: Resource not accessible by integration**

**Error Message:**

```
GraphqlResponseError: Request failed due to following response errors:
- Resource not accessible by integration
```

**Cause:** The GitHub Actions workflow doesn't have sufficient permissions to access repository resources.

**Solution:**

1. **Check workflow permissions** - Ensure the workflow has the required permissions:

   ```yaml
   permissions:
     contents: write
     issues: write
     pull-requests: write
     checks: write
   ```

2. **Verify repository settings** - Go to your repository settings:
   - **Settings** → **Actions** → **General**
   - Ensure "Workflow permissions" is set to "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"

3. **Check branch protection** - If using branch protection:
   - **Settings** → **Branches** → **Branch protection rules**
   - Ensure "Allow GitHub Actions to create and approve pull requests" is enabled

4. **Use Personal Access Token (PAT)** - If the issue persists:
   - Create a PAT with `repo` scope
   - Add it as a repository secret (e.g., `PAT_TOKEN`)
   - Replace `${{ secrets.GITHUB_TOKEN }}` with `${{ secrets.PAT_TOKEN }}`

### **Release Drafter Permission Issues**

**Symptoms:** Release Drafter fails with GraphqlResponseError even with correct permissions.

**Solutions:**

1. **Add error handling** - Use `continue-on-error: true` in Release Drafter steps
2. **Check token scope** - Ensure the token has sufficient permissions
3. **Verify repository access** - Check if the repository is private and token has access
4. **Use alternative approach** - Consider using semantic-release instead

### **Workflow Not Triggering**

**Symptoms:** Workflows don't run when expected.

**Solutions:**

1. **Check workflow triggers** - Verify the `on` section in workflow files
2. **Check branch names** - Ensure you're pushing to `main` or `master`
3. **Check file paths** - Workflows must be in `.github/workflows/`
4. **Check syntax** - Validate YAML syntax

### **Permission Denied Errors**

**Error Message:**

```
Error: Resource not accessible by integration
```

**Solutions:**

1. **Add permissions to workflow:**

   ```yaml
   permissions:
     contents: write
     issues: write
     pull-requests: write
   ```

2. **Use Personal Access Token (PAT):**
   - Create a PAT with required permissions
   - Add it as a repository secret
   - Use it in the workflow instead of `GITHUB_TOKEN`

## 🔧 Pre-commit Hook Issues

### **Hooks Not Running**

**Symptoms:** Pre-commit hooks don't execute on commit.

**Solutions:**

1. **Install hooks:**

   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

2. **Check configuration:**

   ```bash
   pre-commit run --all-files
   ```

3. **Update hooks:**
   ```bash
   pre-commit autoupdate
   ```

### **Hook Failures**

**Common Issues:**

- **Black formatting** - Run `black .` to format code
- **isort imports** - Run `isort .` to sort imports
- **flake8 linting** - Fix linting errors manually
- **mypy type checking** - Add type hints or ignore errors

## 🏷️ Auto-Labeling Issues

### **Labels Not Applied**

**Symptoms:** PRs don't get automatic labels.

**Solutions:**

1. **Check labeler configuration** - Verify `.github/labeler.yml`
2. **Check workflow logs** - Look for errors in auto-label workflow
3. **Verify file patterns** - Ensure file paths match labeler rules
4. **Check permissions** - Ensure workflow has `pull-requests: write`

### **Incorrect Labels**

**Solutions:**

1. **Update labeler rules** - Modify `.github/labeler.yml`
2. **Add new labels** - Create labels in GitHub repository
3. **Test patterns** - Use GitHub's labeler testing

## 📦 Release Management Issues

### **Release Not Created**

**Symptoms:** Pushing tags doesn't create releases.

**Solutions:**

1. **Check workflow triggers** - Ensure workflow runs on tag push
2. **Verify permissions** - Check `contents: write` permission
3. **Check release-drafter config** - Verify `.github/release-drafter.yml`
4. **Test manually** - Use workflow dispatch to test

### **Version Not Updated**

**Symptoms:** `pyproject.toml` version not bumped.

**Solutions:**

1. **Check workflow logs** - Look for sed command errors
2. **Verify file format** - Ensure `pyproject.toml` has correct format
3. **Check permissions** - Ensure workflow can write to repository

## 🔒 Security Cleanup Issues

### **Files Not Removed**

**Symptoms:** Ignored files not removed from repository.

**Solutions:**

1. **Check .gitignore** - Verify files match ignore patterns
2. **Check workflow logs** - Look for git command errors
3. **Verify permissions** - Ensure workflow can modify repository
4. **Test manually** - Run git commands locally

## 🐛 General Debugging

### **Workflow Debugging Steps**

1. **Check Actions tab** - View detailed workflow logs
2. **Enable debug logging** - Add `ACTIONS_STEP_DEBUG: true` secret
3. **Test locally** - Run commands locally to verify
4. **Check syntax** - Validate YAML files

### **Common Commands**

```bash
# Test pre-commit hooks
pre-commit run --all-files

# Check git status
git status

# Test release script
./.scripts/create-release.sh version

# Validate YAML
yamllint .github/workflows/*.yml

# Check Python syntax
python -m py_compile src/**/*.py
```

### **Useful GitHub URLs**

- **Actions:** `https://github.com/{owner}/{repo}/actions`
- **Issues:** `https://github.com/{owner}/{repo}/issues`
- **Settings:** `https://github.com/{owner}/{repo}/settings`
- **Branches:** `https://github.com/{owner}/{repo}/branches`

## 📞 Getting Help

### **Before Asking for Help**

1. **Check this guide** - Look for similar issues
2. **Search logs** - Look for specific error messages
3. **Test locally** - Try reproducing the issue locally
4. **Check documentation** - Review relevant documentation

### **When Reporting Issues**

Include:

- **Error message** - Full error text
- **Workflow logs** - Relevant log sections
- **Repository settings** - Relevant configuration
- **Steps to reproduce** - How to trigger the issue
- **Expected behavior** - What should happen

### **Useful Resources**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Release Drafter Documentation](https://github.com/release-drafter/release-drafter)
- [Pre-commit Documentation](https://pre-commit.com/)
- [GitHub Labeler Action](https://github.com/actions/labeler)

---

**Still having issues?** Open an issue using the 🐛 Bug Report template with the details above!
