# DNSForge Render / Deploy split

DNSForge separates BIND configuration lifecycle operations:

- `dnsforge render`: generates the native Enterprise BIND tree in the render staging area only.
- `dnsforge deploy`: applies a previously rendered tree to the native BIND layout, then applies permissions, SELinux contexts, BIND validation and service reload/restart.
- `dnsforge initialize`: one-shot bootstrap that runs `backup -> render -> deploy -> lock`.

`deploy` does not create `/etc/dnsforge/.initialized.conf.lock`. The lock remains owned exclusively by `initialize`.
