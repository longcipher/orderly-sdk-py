# Setting up GitHub Pages for Orderly SDK Documentation

This guide explains how to set up GitHub Pages to automatically publish your pdoc-generated documentation.

## 📋 Setup Steps

### 1. Enable GitHub Pages

1. Go to your repository settings: `https://github.com/longcipher/orderly-sdk-py/settings`
2. Scroll down to the **Pages** section
3. Under **Source**, select **GitHub Actions**
4. Save the settings

### 2. Configure Repository Permissions

1. Go to **Settings** → **Actions** → **General**
2. Under **Workflow permissions**, select **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**
4. Save the changes

### 3. Set Up PyPI Publishing (Optional)

To enable automatic PyPI publishing when you create releases:

1. Go to your PyPI account and create an API token:
   - Visit: https://pypi.org/manage/account/token/
   - Create a new token with scope for this project
   
2. Add the token to your GitHub repository secrets:
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token (starting with `pypi-`)

## 🚀 How It Works

### Documentation Workflow (`docs.yml`)

- **Triggers**: Push to `master`/`main`, PRs, or manual dispatch
- **What it does**:
  1. Checks out the code
  2. Sets up Python 3.13 and uv
  3. Installs dependencies
  4. Generates documentation with pdoc
  5. Deploys to GitHub Pages

### Publishing Workflow (`publish.yml`)

- **Triggers**: Version tags (`v*`), releases, or manual dispatch  
- **What it does**:
  1. Builds the Python package
  2. Runs quality checks
  3. Publishes to PyPI (if secrets are configured)

## 📖 Generated Documentation

After the first successful run, your documentation will be available at:
`https://longcipher.github.io/orderly-sdk-py/`

The documentation includes:
- Complete API reference for all modules
- Source code links
- Search functionality
- Responsive design with dark/light mode support
- Custom styling optimized for API documentation

## 🔧 Customization

### Pdoc Configuration

Edit `.pdoc.yml` to customize documentation generation:
- Change docstring format
- Enable/disable source code display
- Modify search settings
- Add custom footer text

### Custom Styling

Add custom CSS in `.github/pdoc_templates/custom.css` for:
- Brand colors and fonts
- Layout modifications  
- Additional responsive breakpoints
- Enhanced code highlighting

### Workflow Customization

Modify `.github/workflows/docs.yml` to:
- Change trigger conditions
- Add quality checks before deployment
- Integrate with other documentation tools
- Add notification steps

## 📝 Tips

1. **Documentation Quality**: Add comprehensive docstrings to all public methods and classes
2. **Version Control**: Tag releases properly (`git tag v0.3.1`) to trigger publishing
3. **Testing**: Use workflow dispatch to test documentation generation manually
4. **Monitoring**: Check the Actions tab to monitor workflow runs

## 🐛 Troubleshooting

### Common Issues

**Documentation not updating?**
- Check if GitHub Pages is enabled and set to "GitHub Actions"
- Verify workflow permissions are set correctly
- Look at the Actions tab for error logs

**PyPI publishing failing?**
- Ensure `PYPI_API_TOKEN` secret is set correctly
- Check if the token has the right scope
- Verify the package version is not already published

**Styling not applied?**
- Check if custom CSS files exist in the expected locations
- Verify HTML generation completes successfully
- Look for CSS-related errors in workflow logs

### Getting Help

- Check workflow logs in the Actions tab
- Review pdoc documentation: https://pdoc.dev
- Open an issue if you encounter persistent problems
