# DNSForge Manager Performance and Scale Model

DNSForge Manager uses bounded concurrency for fleet fan-out operations such as DNSSync and DNSBeat monitoring. Worker counts are calculated from server CPU and memory characteristics and are capped to avoid exhausting the Manager host or the managed DNSForge agents.

PostgreSQL persistence must be designed for very large datasets. Tables that can grow without bound, such as audit, compliance history and DNSSync executions, require selective indexes, batched reads, bounded result windows and asynchronous access paths when used by API endpoints or fleet operations.

Current scale guarantees:

- JSON remains the default backend for simple deployments.
- PostgreSQL remains optional but is optimized for enterprise deployments.
- DNSSync fan-out uses deterministic bounded threading.
- Async connection protocols are available for PostgreSQL adapters that need non-blocking I/O.
- Large history datasets are queried through indexed payload fields and should be read with bounded pagination at API boundaries.
