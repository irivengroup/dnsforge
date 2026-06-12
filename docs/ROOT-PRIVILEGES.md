# Root privilege policy

DNSForge commands manage BIND configuration, BIND runtime state, filesystem ownership, permissions, SELinux contexts and system services.

For this reason, every executable DNSForge command requires elevated privileges.

Supported usage:

```bash
sudo dnsforge authoritative initialize
sudo dnsforge proxy initialize --type hybrid
sudo dnsforge status
sudo dnsforge zone list
```

Help output remains readable without privileges:

```bash
dnsforge --help
dnsforge proxy initialize --help
```

If a command is run without root privileges, DNSForge exits before dispatching the command and prints a clear sudo instruction.
