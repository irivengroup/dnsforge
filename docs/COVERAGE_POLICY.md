# DNSForge Coverage Policy

DNSForge v12.4.0 introduces a blocking coverage gate with a minimum threshold of **90%**.

The gate measures the stable product core:

- `src/dnsforge`
- `src/dnsforge_manager`

The policy intentionally excludes host-mutating adapters, process entrypoints, generated/build tooling, and progressive legacy compatibility surfaces that are already protected by architecture, CLI/API parity, Product Gate, release gate, Bandit, MyPy and integration tests.

## CI command

```bash
pytest \
  --cov=src/dnsforge \
  --cov=src/dnsforge_manager \
  --cov-report=term-missing \
  --cov-fail-under=90
```

## Rule

The build fails when measured coverage drops below 90%.
