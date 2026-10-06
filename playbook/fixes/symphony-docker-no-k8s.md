---
type: playbook
component: symphony
tags: [fix, symphony, docker]
status: verified
sources:
  - "[[symphony-overview]]"
last-verified: 2026-10-03
related:
  - "[[symphony-overview]]"
---
# Symphony API in Docker without Kubernetes
```bash
docker run -d --name symph -e CONFIG=/symphony-api-no-k8s.json -e LOG_LEVEL=Info -p 28082:8082 ghcr.io/eclipse-symphony/symphony-api:latest
curl localhost:28082/v1alpha2/greetings
docker rm -f symph
```
Without `CONFIG` the entrypoint runs `/symphony-api -c $CONFIG -l ...` with an empty value and exits. Observed 2026-10-03 ([[symphony-overview]]).
