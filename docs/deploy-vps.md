# Deploy VPS — ms-poc

Production URL: **https://mspoc.faruk.dev.br**

Follows the shared Faruk VPS pattern documented in [`faruk_base/docs/deploy-vps.md`](https://github.com/farukzahra/faruk_base/blob/main/docs/deploy-vps.md) and `C:\repo\financeiro\planos\guia-deploy-vps.local.md`.

## Infrastructure

| Item | Value |
|------|-------|
| VPS | `66.23.231.218` |
| Path | `/opt/ms-poc` |
| Host port | `127.0.0.1:8086` → container `:80` |
| HTTPS | Caddy on host (`/etc/caddy/Caddyfile`) |
| DNS | `A mspoc → 66.23.231.218` (Registro.br) |
| Deploy SSH key | `C:\repo\financeiro\planos\vps-secrets\deploy_key` |

## Architecture

```text
Internet → Caddy :443 (mspoc.faruk.dev.br)
              → 127.0.0.1:8086 (web container)
                    /api/* → api:8000 (FastAPI + Azure)
                    /*     → Vue SPA (static)
              api → mcp-server → mock CRM/Sales/…
              api → Azure OpenAI + AI Search + Blob
```

## First-time VPS setup

```bash
ssh -i C:/repo/financeiro/planos/vps-secrets/deploy_key root@66.23.231.218

mkdir -p /opt/ms-poc
git clone https://github.com/farukzahra/ms-poc.git /opt/ms-poc
# Copy production .env with Azure keys (never commit)
nano /opt/ms-poc/.env

cd /opt/ms-poc
chmod +x scripts/deploy-vps.sh
WEB_PORT=8086 sh scripts/deploy-vps.sh
```

## Caddy (host)

Add to `/etc/caddy/Caddyfile`:

```caddy
mspoc.faruk.dev.br {
	encode gzip zstd
	reverse_proxy 127.0.0.1:8086
}
```

```bash
systemctl reload caddy
curl -sI https://mspoc.faruk.dev.br/
```

## GitHub Actions

Push to `main` → `.github/workflows/deploy.yml`:

1. Playwright E2E (mocked API)
2. SSH → `git reset --hard` → `scripts/deploy-vps.sh`

### Repository secrets

| Secret | Value |
|--------|-------|
| `VPS_HOST` | `66.23.231.218` |
| `VPS_USER` | `root` |
| `VPS_PORT` | `22` |
| `VPS_SSH_KEY` | contents of `deploy_key` |
| `DEPLOY_PATH` | `/opt/ms-poc` |

Variable: `WEB_PORT` = `8086`

## Production `.env`

Copy `.env.production.example` to `.env` on the VPS. Must include Azure keys (`scripts/azure_fill_env.py` on a machine with `az login`).

Set `CORS_ORIGIN=https://mspoc.faruk.dev.br`.

## Validate

```bash
curl -s https://mspoc.faruk.dev.br/api/health
curl -s https://mspoc.faruk.dev.br/api/ready   # expect llm:azure, rag:azure
```

## Related

- [azure-access.md](azure-access.md) — Azure resource names and bootstrap
- [stack.md](stack.md) — local ports vs production
