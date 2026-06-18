# DNSForge release packaging policy

DNSForge source trees and release archives follow different hygiene rules.

## Source hygiene

The source tree must not contain generated cache/build artifacts:

- `__pycache__/`
- `*.pyc`, `*.pyo`, `*.pyd`
- `.pytest_cache/`
- `.mypy_cache/`
- `.ruff_cache/`
- `.coverage`, `coverage.xml`, `htmlcov/`
- `build/`
- `dist/`
- `*.egg-info/`

Check source hygiene:

```bash
python tools/clean.py --check-source
```

Remove transient artifacts before a clean build:

```bash
sudo python tools/clean.py --fix
```

`sudo` is useful in CI after root-required integration tests have produced root-owned caches.

## Release hygiene

Release archives intentionally include `dist/` after `python -m build` so an administrator can install DNSForge without rebuilding the package locally.

Allowed in a release archive:

```text
dist/
├── dnsforge-<version>-py3-none-any.whl
└── dnsforge-<version>.tar.gz
```

Still forbidden in release archives:

- caches
- `build/`
- `*.egg-info/`
- duplicate wheels or sdists

Check release hygiene:

```bash
python tools/clean.py --check-release
```

Recommended release flow:

```bash
sudo python tools/clean.py --fix
python tools/clean.py --check-source
python -m build
sudo python tools/clean.py --fix-release
python tools/clean.py --check-release
```

After a build, remove build metadata while preserving `dist/`:

```bash
sudo python tools/clean.py --fix-release
```
