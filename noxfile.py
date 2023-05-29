import os

import nox

PYTHON_VERSIONS = [
    '3.8',
    '3.9',
    '3.10',
    '3.11',
]
PYTHON_DEFAULT_VERSION = PYTHON_VERSIONS[-1]
REQUIREMENTS = {
    'requirements': ['pip-tools'],
    'lint_pyproject': ['validate-pyproject[all]'],
    'lint': ['ruff'],
    'types': ['mypy', 'lxml-stubs'],
    'test': ['pytest', 'pytest-cov', 'pytest-sugar'],
    'coverage': ['coverage[toml]'],
    'build': ['build'],
}
SKIP_COVERAGE = os.environ.get('SKIP_COVERAGE') == 'true'

nox.options.sessions = ['lint', 'test', 'build']
nox.options.reuse_existing_virtualenvs = True
nox.options.stop_on_first_error = True


@nox.session(python=PYTHON_DEFAULT_VERSION)
def requirements(session: nox.Session) -> None:
    """Create `requirements*.txt`"""
    session.install(*REQUIREMENTS[session.name])
    pip_compile = ['pip-compile', '--quiet', '--resolver=backtracking', '--allow-unsafe']
    session.run(*pip_compile, '--extra=dev', '--output-file=requirements-dev.txt', 'pyproject.toml')
    session.run(*pip_compile, '--output-file=requirements.txt', 'pyproject.toml')


@nox.session(python=PYTHON_DEFAULT_VERSION)
def lint_pyproject(session: nox.Session) -> None:
    """Validate `pyproject.toml`"""
    session.install(*REQUIREMENTS[session.name])
    session.run('validate-pyproject', 'pyproject.toml')


@nox.session(python=PYTHON_DEFAULT_VERSION)
def lint(session: nox.Session) -> None:
    """Lint Python code with Ruff"""
    session.install(*REQUIREMENTS[session.name])
    session.run('ruff', *(session.posargs or ['.']))


@nox.session(python=PYTHON_DEFAULT_VERSION)
def types(session: nox.Session) -> None:
    """Check types with MyPy"""
    session.install(*REQUIREMENTS[session.name])
    session.run('mypy', *(session.posargs or ['.']))


@nox.session(python=PYTHON_VERSIONS)
def test(session: nox.Session) -> None:
    """Run tests with pytest"""
    session.install(*REQUIREMENTS[session.name.split('-')[0]])
    session.install('-e', '.')
    args = []
    if not SKIP_COVERAGE:
        args += ['--cov=random_xml_csv', '--cov-branch', '--cov-report=xml']
    session.run('pytest', *args, *(session.posargs or ['tests']))
    if not SKIP_COVERAGE:
        session.notify('coverage')


@nox.session(python=PYTHON_DEFAULT_VERSION)
def coverage(session: nox.Session) -> None:
    """Generate test coverage report"""
    session.install(*REQUIREMENTS[session.name])
    session.run('coverage', 'report', '--show-missing', '--skip-covered')
    session.run('coverage', 'erase')


@nox.session(python=PYTHON_VERSIONS)
def profile(session: nox.Session) -> None:
    """Profile Python code"""
    session.run('python', '-m', 'cProfile', '-s', 'tottime', '-o', 'random_xml_csv.stats', '-m', 'random_xml_csv')


@nox.session(python=PYTHON_DEFAULT_VERSION)
def build(session: nox.Session) -> None:
    """Build Python wheel"""
    session.install(*REQUIREMENTS[session.name])
    session.run('rm', '-rf', 'dist', '*.egg-info', external=True)
    session.run('python', '-m', 'build', '--wheel')
