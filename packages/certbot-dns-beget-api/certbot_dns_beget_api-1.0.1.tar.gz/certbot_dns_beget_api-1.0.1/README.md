# Beget DNS Authenticator plugin for Certbot

---

## Credentials

```ini
# Beget API token used by Certbot
dns_beget_api_username = username
dns_beget_api_password = password 
```

## Examples

```bash
certbot certonly --authenticator dns-beget-api \
    --dns-beget-api-credentials ~/.secrets/certbot/beget.ini \
    --dns-beget-api-propagation-seconds 120 \
    -d domain.com -d *.domain.com
```

```bash
certbot certonly --authenticator dns-beget-api \
    --dns-beget-api-credentials ~/.secrets/certbot/beget.ini \
    --dns-beget-api-propagation-seconds 120 \
    -d xxx.yyy.domain.com -d *.yyy.domain.com
```
