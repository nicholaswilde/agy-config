---
name: network-speed-diagnostics
description: >-
  Workflow for diagnosing network speed issues in a UniFi homelab environment.
  Guides the agent through running local speedtests and checking the UniFi Gateway.
---

# Network Speed Diagnostics

Use this skill when the user asks to investigate slow internet speed or run a speed test in a UniFi environment.

## Workflow

1. **Local Benchmark:** 
   - Run the official Ookla speedtest CLI locally to check the effective speed from the host.
   - *Tip:* If the binary isn't installed and standard download tools are blocked by `context-mode`, use a Python script to download and extract `https://install.speedtest.net/app/cli/ookla-speedtest-1.2.0-linux-x86_64.tgz`.

2. **UniFi Gateway Status:**
   - Use the `unifi` MCP server to check if the gateway is artificially limiting speed.
   - Use `unifi_tool_index` to find network details tools (like `unifi_get_network_details`) to check if `wan_smartq_enabled` (Smart Queues / QoS) is enabled on the WAN.

3. **UniFi Gateway Speedtest:**
   - Use the `unifi` MCP server to trigger a speed test directly on the gateway (`unifi_trigger_speedtest` requires `gateway_mac`).
   - Use `unifi_get_device_details` on the gateway MAC address to retrieve the cached `speedtest-status` results from the raw device configuration.

4. **Compare and Conclude:**
   - Compare the local VM speed to the Gateway speed.
   - If the Gateway gets 1Gbps but the local VM is much slower (e.g., ~600 Mbps), attribute the loss to virtualization software bridge overhead and standard physical ethernet overhead.
