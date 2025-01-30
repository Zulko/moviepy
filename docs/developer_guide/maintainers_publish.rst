.. _maintainers_publish:

Publishing a New Version of MoviePy
===================================

This section is for maintainers responsible for publishing new versions of MoviePy. Follow these steps to ensure the process is smooth and consistent:

**Pre-requisites**
------------------
- Ensure you have proper permissions to push changes and create releases in the MoviePy repository.

Steps to Publish a New Version
------------------------------

1. **Update the `CHANGELOG.md`**

   - Add a new section for the upcoming version, respecting the format used in previous entries.
   - Summarize all changes, fixes, and new features.

2. **Update the version in `pyproject.toml`**

   - Open the `pyproject.toml` file.
   - Update the `version` field to the new version, following `Semantic Versioning <https://semver.org/>`_.

3. **Commit and Push**

   - Stage your changes::

        git add CHANGELOG.md pyproject.toml

   - Commit your changes::

        git commit -m "Release vX.Y.Z"

   - Push your changes::

        git push

4. **Create a New Tag**

   - Create a tag for the new version (replace ``vX.Y.Z`` with the actual version number)::

        git tag -a vX.Y.Z -m "Release vX.Y.Z"

   - Push the tag to the remote repository::

        git push origin vX.Y.Z

5. **Create a New Release**

   - Go to the repository's page on GitHub (or the relevant hosting platform).
   - Navigate to the "Releases" section and create a new release.
   - Use the new tag (``vX.Y.Z``) and provide a description for the release.
     - Copy the changelog for this version into the release description.
   - Publish the release.

GitHub actions will automatically build and publish the new release on PyPi.

By following these steps, you ensure that each MoviePy release is well-documented, correctly versioned, and accessible to users.
