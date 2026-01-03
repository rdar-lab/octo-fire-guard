# Release Process

This document describes how to create a new release of the Octo Fire Guard plugin.

## Prerequisites

- You must have push access to the repository
- The code must be in a stable, tested state
- The CHANGELOG.md must be updated with the new version

## Release Steps

1. **Update the version number** in `setup.py`:
   ```python
   plugin_version = "X.Y.Z"
   ```

2. **Update CHANGELOG.md** with the new version and release date:
   ```markdown
   ## [X.Y.Z] - YYYY-MM-DD
   
   ### Added
   - List new features
   
   ### Changed
   - List changes to existing features
   
   ### Fixed
   - List bug fixes
   ```

3. **Commit the version changes**:
   ```bash
   git add setup.py CHANGELOG.md
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

4. **Create and push a git tag**:
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin vX.Y.Z
   ```

5. **GitHub Actions will automatically**:
   - Create a GitHub release with the tag
   - Extract release notes from CHANGELOG.md
   - Make the release available for plugin updates

## Update Mechanism

The plugin uses OctoPrint's Software Update plugin with GitHub releases:

- **Type**: `github_release`
- **Repository**: `rdar-lab/octo-fire-guard`
- **Install Method**: pip install from GitHub archive

Users will be notified of updates through OctoPrint's built-in update checker when new releases are published.

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Added functionality in a backwards compatible manner
- **PATCH** version: Backwards compatible bug fixes

## First Release

To publish the initial v1.0.0 release (which is already documented but not published):

```bash
# Ensure you're on the main branch with the latest changes
git checkout main
git pull

# Verify that setup.py contains version 1.0.0
if ! grep -q 'plugin_version = "1.0.0"' setup.py; then
  echo "WARNING: Version mismatch in setup.py" >&2
  exit 1
fi

# Create and push the v1.0.0 tag
git tag -a v1.0.0 -m "Release version 1.0.0 - Initial release"
git push origin v1.0.0
```

The GitHub Actions workflow will automatically create the release with notes extracted from CHANGELOG.md.
