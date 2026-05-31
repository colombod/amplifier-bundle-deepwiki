# DeepWiki Bundle — Digital Twin Universe (DTU) Validation

This folder holds a reusable [Digital Twin Universe](https://github.com/microsoft/amplifier-bundle-digital-twin-universe)
profile for **end-to-end validation of the `deepwiki` bundle in a realistic,
isolated deployment** — not just "unit tests pass on my machine."

| File | Purpose |
|------|---------|
| `deepwiki-validation.yaml` | DTU profile that installs Amplifier and layers this bundle via `--app` from a local mirror of the working tree. |
| `README.md` | This file — how to relaunch and what the profile validates. |

## What it validates

1. **Clean install/load from local source.** Amplifier installs and the
   `deepwiki` bundle registers without error.
2. **`--app` layering (the README install path).**
   `amplifier bundle add … --app` makes deepwiki available on **every** session
   with **no `bundle use`** required.
3. **Local hook module mount + agent registration.** The hook module
   `modules/hooks-deepwiki-trigger` (referenced by the relative source
   `../modules/hooks-deepwiki-trigger`) resolves and composes, and the
   `deepwiki:deepwiki-expert` agent is registered.
4. **`tool-mcp` deepwiki server config.** The MCP server
   (`https://mcp.deepwiki.com/mcp`) is registered and exposes its 3 tools
   (`mcp_deepwiki_read_wiki_structure`, `mcp_deepwiki_read_wiki_contents`,
   `mcp_deepwiki_ask_question`).

## Why Gitea (testing LOCAL changes)

The profile uses `url_rewrites` to redirect
`github.com/colombod/amplifier-bundle-deepwiki` to a local
[Gitea](https://github.com/microsoft/amplifier-bundle-gitea) mirror. This makes
the DTU install the **local working tree** (committed + uncommitted) instead of
the published GitHub version, so unpushed changes are exercised exactly as a
real user would install them.

## Prerequisites

- `amplifier-digital-twin`, `amplifier-gitea`, Incus, and Docker installed and running.
- An Anthropic API key in `ANTHROPIC_API_KEY` (and `ANTHROPIC_BASE_URL` if you
  use a gateway) — forwarded into the DTU for the live smoke test.

## Relaunch (full cycle)

From the bundle repo root:

```bash
# 1. Start (or reuse) a Gitea instance and capture its id/port/token
amplifier-gitea list            # reuse a running instance, OR:
amplifier-gitea create --port 10110
TOKEN=$(amplifier-gitea token <gitea-id> | jq -r .token)

# 2. Mirror this repo into Gitea (first time only)
amplifier-gitea mirror-from-github <gitea-id> \
  --github-repo https://github.com/colombod/amplifier-bundle-deepwiki

# 3. Push the current working tree (committed + uncommitted) to the mirror
#    via a throwaway snapshot clone — NEVER mutate your working tree for this.
SNAP=$(mktemp -d)/amplifier-bundle-deepwiki
git clone --local --no-hardlinks . "$SNAP"
( git ls-files -z --cached --modified --others --exclude-standard ) \
  | rsync -a --files-from=- --from0 ./ "$SNAP/"
( git ls-files -z --deleted ) | (cd "$SNAP" && xargs -0 --no-run-if-empty rm -f)
( cd "$SNAP" \
  && git -c user.email=dtu@local -c user.name="DTU Snapshot" add -A \
  && git -c user.email=dtu@local -c user.name="DTU Snapshot" commit --allow-empty -m "DTU snapshot" \
  && git remote add gitea "http://admin:$TOKEN@localhost:<port>/admin/amplifier-bundle-deepwiki.git" \
  && git push gitea HEAD:main --force )

# 4. Find a host IP the DTU container can reach Gitea on (Incus gateway works on
#    most Linux/WSL2 hosts; probe if unsure):
#    incus exec <tmp> -- curl -sf http://<host-ip>:<port>/
# 5. Launch
amplifier-digital-twin launch .amplifier/dtu/deepwiki-validation.yaml \
  --var GITEA_URL=http://<host-ip>:<port> \
  --var GITEA_TOKEN="$TOKEN" \
  --name deepwiki-validation
```

> The `launch` call provisions the container and may take several minutes.
> Run it with a generous timeout; it prints `DTU <name> ready.` when done.

## Verify

```bash
ID=deepwiki-validation

# 1. Installed + registered
amplifier-digital-twin exec $ID -- amplifier --version
amplifier-digital-twin exec $ID -- amplifier bundle list

# 2. --app layering (deepwiki present in bundle.app, no `bundle use`)
amplifier-digital-twin exec $ID -- cat /root/.amplifier/settings.yaml

# 3 + 4. Live composition: a default session sees the deepwiki-expert subagent
#         and the 3 deepwiki MCP tools.
amplifier-digital-twin exec $ID -- amplifier run \
  "Do not use any tools. List every subagent you can delegate to and every \
   deepwiki MCP tool available to you."
```

## Re-test after new changes

After pushing a fresh working-tree snapshot (step 3 above), refresh the running
container in place instead of relaunching:

```bash
amplifier-digital-twin update deepwiki-validation \
  --var GITEA_URL=http://<host-ip>:<port> \
  --var GITEA_TOKEN="$TOKEN"
```

The profile's `update` section clears the bundle cache and re-adds deepwiki via
`--app`.

## Tear down

```bash
amplifier-digital-twin destroy deepwiki-validation
```

## Notes

- The hook module's detection logic is covered by the in-repo unit suite
  (`modules/hooks-deepwiki-trigger/tests`, 155 tests). This DTU validates the
  **deployed composition** (relative-source mount, agent + MCP registration,
  `--app` layering) that unit tests cannot reach.
- DeepWiki MCP egress (`https://mcp.deepwiki.com/mcp`) requires outbound
  network from the container. If the sandbox blocks egress, the server still
  **registers** from config; only live round-trips are affected.
