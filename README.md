# BraBos — Google Reviews no relógio Ulanzi/AWTRIX

A cada 30 minutos, o GitHub Actions:

1. Lê a contagem de reviews na home de [braboscleaning.com](https://braboscleaning.com)
2. Publica via MQTT (flespi) o app `googlereviews` no relógio AWTRIX

O relógio se conecta ao broker `mqtt.flespi.io` de qualquer rede Wi-Fi —
não depende de IP local. Se o relógio reiniciar, a próxima execução
recria o app e mantém hora/data/temperatura fora da rotação.

## Configuração

- Secret necessário: `FLESPI_TOKEN` (Settings → Secrets and variables → Actions)
- Prefixo MQTT do relógio: `awtrix_9da880`
- Para rodar manualmente: aba **Actions** → *Atualizar reviews no relogio* → **Run workflow**

## Visual

G colorido do Google + número em verde BraBos (#8DC63F) + 5 estrelas amarelas.
