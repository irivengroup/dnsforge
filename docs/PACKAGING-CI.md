# DNSForge packaging CI

DNSForge CI must validate that the Python package is not only testable from source, but also installable as a wheel.

The packaging gate performs:

```bash
python -m build
```

Then it verifies:

```bash
dist/*.whl
dist/*.tar.gz
python -m twine check dist/*
pip install dist/*.whl
dnsforge --help
dnsforge version
```

The generated wheel and source distribution are uploaded as GitHub Actions artifacts using `actions/upload-artifact`.

This prevents a release from passing tests while producing no installable artifact.
