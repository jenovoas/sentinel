# Grafana Iframe Embedding - Quick Fix

## Problem

Firefox (and other browsers) block Grafana iframes with error:
```
Firefox no puede abrir esta página
Para proteger tu seguridad, localhost no permitirá que Firefox 
muestre la página si otro sitio la ha incrustado.
```

This is due to Grafana's `X-Frame-Options` header which prevents clickjacking attacks.

## Solution

### Step 1: Create Grafana Configuration

File: `grafana/grafana.ini`

```ini
[security]
allow_embedding = true
cookie_samesite = none

[auth.anonymous]
enabled = true
org_name = Main Org.
org_role = Viewer
```

### Step 2: Mount Configuration in Docker

Update `docker-compose.yml`:

```yaml
grafana:
  volumes:
    - ./grafana/grafana.ini:/etc/grafana/grafana.ini:ro
```

### Step 3: Restart Grafana

```bash
docker-compose restart grafana
```

### Step 4: Verify

1. Open http://localhost:3001 (Grafana directly) - should work
2. Open http://localhost:3000/metrics (Sentinel frontend) - iframes should now load

## Security Note

**⚠️ IMPORTANT**: `allow_embedding = true` allows Grafana to be embedded in ANY website.

**For Production**:

1. **Use authentication** instead of anonymous access:
   ```ini
   [auth.anonymous]
   enabled = false
   ```

2. **Restrict embedding** to specific domains:
   ```ini
   [security]
   allow_embedding = true
   cookie_samesite = lax
   
   [server]
   root_url = https://sentinel.yourdomain.com
   ```

3. **Use API keys** for embedded dashboards:
   ```typescript
   // In frontend
   const grafanaUrl = `http://localhost:3001/d/dashboard-id?auth_token=${API_KEY}&kiosk`
   ```

## Alternative: Reverse Proxy

Instead of embedding, you can proxy Grafana through Nginx:

```nginx
location /grafana/ {
    proxy_pass http://grafana:3000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

Then access via: `http://localhost/grafana/`

## Testing

```bash
# Check if Grafana allows embedding
curl -I http://localhost:3001 | grep X-Frame-Options

# Should NOT see X-Frame-Options header
# or should see: X-Frame-Options: ALLOWALL
```

## Troubleshooting

### Still seeing error after restart?

1. **Clear browser cache**: Ctrl+Shift+Delete
2. **Hard refresh**: Ctrl+F5
3. **Check Grafana logs**:
   ```bash
   docker logs sentinel-grafana | grep -i "allow_embedding"
   ```

### Grafana not starting?

```bash
# Check config syntax
docker exec sentinel-grafana grafana-cli admin reset-admin-password admin

# View logs
docker logs sentinel-grafana --tail 50
```

---

**Status**: ✅ Fixed - Grafana now allows iframe embedding
