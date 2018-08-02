# Developing BoxBoat Python Library

## Developing

#### Prerequisites
* python3.6
* virtualenv
* [pipenv](https://docs.pipenv.org/)

#### Checkout and Install Dependencies
1. Clone repository from GitLab and navigate to repository root
2. Run `pipenv sync --dev` to install dependencies.  This will create a new virtual environment on first run

#### Run
* **Shell**: `pipenv shell` will spawn a new shell with the virtual environment imported
* **Setup IDE**: get virtual environment path from `pipenv --venv` and setup IDE using this path

## Testing

#### Unit Tests
* Add to `./test/unit/` and mirror directory structure from `./bb-py`
* Unit tests should not make external calls to 3rd parties such as AWS; those belong in functional tests
* Test classes use built-in [unittest](https://docs.python.org/3.6/library/unittest.html) module.  Test methods should start with `test_`
* Tests are run with [nose](nose.readthedocs.io/en/latest/).  Test files should start with `test_`
* To run unit tests: `pipenv run nosetests` from `./test/unit`

#### Functional Tests
* Add to `./test/functional/` and mirror directory structure from `./bb-py`
* Tokens for 3rd party APIs should not be committed; they should be added as [GitLab CI/CD Secrets](https://gitlab.com/boxboat/bb-py/settings/ci_cd)
* CI uses the AWS [bb-py-ci](https://console.aws.amazon.com/iam/home?region=us-east-1#/users/bb-py-ci) IAM user.  Only the policies required by functional tests should be granted to that user.
* Test classes use built-in [unittest](https://docs.python.org/3.6/library/unittest.html) module.  Test methods should start with `test_`
* Tests are run with [nose](nose.readthedocs.io/en/latest/).  Test files should start with `test_`
* To run unit tests: `pipenv run nosetests` from `./test/functional`

#### Resources

Non-python files used for testing belong in `./test/resources`

#### Test Utilities

Test-related python code belongs in `./test/testutils`

## Build Process

Build-related files and scripts belong in `./scripts`

#### GitLab CI

* GitLab CI runs unit tests on each commit and pull request
* The GitLab CI tests are defined in `./.gitlab-ci.yml`
* CI related scripts are located in `./scripts/ci`
