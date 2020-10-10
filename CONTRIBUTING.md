# Contributing to pyronear-api

Everything you need to know to contribute efficiently to the project.



## Codebase structure

- [src](https://github.com/pyronear/pyronear-api/blob/master/src) - The actual [FastAPI](https://fastapi.tiangolo.com/) project
- [src/app](https://github.com/pyronear/pyronear-api/blob/master/src/app) - The source code of the API
- [src/tests](https://github.com/pyronear/pyronear-api/blob/master/src/tests) - The unittests for the app



## Continuous Integration

This project uses the following integrations to ensure proper codebase maintenance:

- [Github Worklow](https://help.github.com/en/actions/configuring-and-managing-workflows/configuring-a-workflow) - run jobs for package build and coverage
- [Codacy](https://www.codacy.com/) - analyzes commits for code quality
- [Codecov](https://codecov.io/) - reports back coverage results
- [Heroku](https://www.heroku.com/) - where the app is deployed from the `master` branch

As a contributor, you will only have to ensure coverage of your code by adding appropriate unit testing of your code.



## Issues

Use Github [issues](https://github.com/pyronear/pyronear-api/issues) for feature requests, or bug reporting. When doing so, use issue templates whenever possible and provide enough information for other contributors to jump in.



## Developing pyronear-api


### Commits

- **Code**: ensure to provide docstrings to your Python code. In doing so, please follow [Google-style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) so it can ease the process of documentation later.
- **Commit message**: please follow [Udacity guide](http://udacity.github.io/git-styleguide/)