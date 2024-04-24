# MoviePy's Contribution Guidelines

## Communication on GitHub

- Keep messages on GitHub issues and pull requests on-topic and to the point. Be aware that each comment triggers a notification which gets sent out to a number of people.
  - Opinions are OK.
  - For longer or more in-depth discussions, use the [MoviePy Gitter](https://gitter.im/movie-py/Lobby). If these discussions lead to a decision, like a merge/reject, please leave a message on the relevant MoviePy issue to document the outcome of the discussion/the reason for the decision.
- Do not push any commit that changes the API without prior discussion.

## Preparing for development

- Fork the official MoviePy repository to your own GitHub account:  
Use the "Fork" button in the top right corner of the GitHub interface while viewing [the official MoviePy](https://github.com/Zulko/moviepy) repository.
- Use your fork as the basis for cloning the repository to your local machine: `$ git clone URL_TO_YOUR_FORK`  
You can get the appropriate URL (SSH- or HTTPS-based) by using the green "Code" button located at the top right of the repository view while looking at your fork. By default, Git refers to any remote you clone from – i.e. in this case your fork on GitHub – as `origin`.
- Enter your local clone and add the official MoviePy repository as a second remote, with alias `upstream`:  
`$ git remote add upstream git@github.com:Zulko/moviepy.git` (using SSL) _or_   
`$ git remote add upstream https://github.com/Zulko/moviepy.git` (using HTTPS).
- Install the library inside a [virtual environment](https://docs.python.org/3/tutorial/venv.html) with all dependencies included using `$ pip install -e ".[optional,doc,test,lint]"`
- Configure pre-commit hooks running `$ pre-commit install`

## Coding conventions, code quality
 
- Respect [PEP8](https://www.python.org/dev/peps/pep-0008/) conventions.
- Add just the "right" amount of comments. Try to write auto-documented code with very explicit variable names.
- If you introduce new functionality or fix a bug, document it in the docstring or with code comments.
- MoviePy's team adopted [pre-commit](https://pre-commit.com/) to run code checks using black, flake8 and isort, so make sure that you've configured the pre-commit hooks with `pre-commit install`. 


## Standard contribution workflow

### Local development
- Keep your local `master` branch up-to-date with the official repo's master by periodically fetching/pulling it:  
`$ git pull upstream master`
- Never make changes on `master` directly, but branch off into separate develop branches:  
`$ git checkout --branch YOUR_DEVELOP_BRANCH`  
Ideally, these are given names which function as keywords for what you are working on, and are prefixed with `fix_` (for bug fixes), `feature_` or something similarly appropriate and descriptive.
- Base any changes you submit on the most recent `master`.

More detailed explanation of the last point:

It is likely that the official repo's `master` branch will move on (get updated, have other PRs merged into it) while you are working on your changes. Before creating a pull request, you will have to make sure your changes are not based on outdated code. For this reason, it makes sense to avoid falling "too much behind" while developing by rebasing your local `master` branch at intervals. Make sure your `master` branch is in sync with the official `master` branch (as per the first point), then, while checked into your develop branch, run: `$ git rebase master`

If you **haven't rebased before**, make sure to **familiarise yourself** with the concept.

### Submitting Pull Requests

You do not have to have finished your feature or bug fix before submitting a PR; just mention that it still is a work in progress.

Before submitting PRs:

- run the test suite over your code to expose any problems: `$ pytest`
- push your local develop branch to your GitHub fork `$ git push origin YOUR_DEVELOP_BRANCH`

When you now look at your forked repo on your GitHub account, you will see GitHub suggest branches for sending pull requests to the official `Zulko/moviepy` repository.

Once you open a PR, you will be presented with a template which you are asked to fill out. You are encouraged to add any additional information which helps provide further context to your changes, and to link to any issues or PRs which your pull request references or is informed by.

On submitting your PR, an automated test suite runs over your submission, which might take a few minutes to complete. In a next step, a MoviePy maintainer will review your code and, if necessary, help you to get it merge-ready.
