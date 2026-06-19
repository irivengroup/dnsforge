# DNSForge CI Coverage Policy

DNSForge 13.0.x keeps the product-code coverage gate at **90%**.

The coverage gate measures the Python product surfaces under:

- `src/dnsforge`
- `src/dnsforge_manager`

Live BIND smoke tests are executed by a dedicated enterprise validation step. They are intentionally excluded from the coverage gate because they validate host integration, BIND runtime isolation, and distribution-specific paths rather than Python branch coverage.

The CI therefore keeps two independent controls:

1. **Enterprise BIND validation**
   - generated BIND configuration validation
   - live `named` smoke startup

2. **Coverage gate**
   - product unit/integration tests
   - `--cov-fail-under=90`

This avoids duplicate live BIND startup inside the coverage phase while preserving the operational validation required for GA maintenance.
