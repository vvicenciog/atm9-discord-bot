# 🤖 EC2 Manager — Discord Bot

Bot de Discord que permite **encender y apagar** una instancia EC2 de AWS usando comandos de texto (`!prender`, `!apagar`), mantenido vivo automáticamente con GitHub Actions.

---

## ⚡ Comandos disponibles

| Comando | Alias | Descripción |
|---------|-------|-------------|
| `!prender` | `!encender` `!start` `!on` | 🟢 Enciende la instancia EC2 y avisa cuando está lista |
| `!apagar` | `!stop` `!off` | 🔴 Apaga la instancia EC2 y avisa cuando se apaga |
| `!estado` | `!status` `!info` | 📊 Muestra estado, IP, tipo y región |
| `!ayuda` | `!help` `!comandos` | 📖 Lista todos los comandos en el chat |

> 🔔 El bot te **menciona automáticamente** cuando la instancia termina de encenderse o apagarse.

---

## 🚀 Setup — Paso a paso

### 1. Crear el Bot de Discord

1. Ve a [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** → ponle nombre → **Create**
3. Ve a **Bot** → click **"Reset Token"** → **copia el token** (lo necesitas después)
4. En la misma página, activa:
   - ✅ `MESSAGE CONTENT INTENT`
5. Ve a **OAuth2 → URL Generator**:
   - Scopes: `bot`
   - Permissions: `Send Messages`, `Read Message History`, `Embed Links`
6. Copia la URL generada y pégala en tu navegador para **invitar el bot a tu servidor**

### 2. Crear credenciales AWS (IAM)

Crea un usuario IAM con esta política mínima:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:DescribeInstances"
      ],
      "Resource": "arn:aws:ec2:*:*:instance/TU_INSTANCE_ID"
    }
  ]
}
```

> Reemplaza `TU_INSTANCE_ID` con tu ID real (e.g., `i-0abc123def456`).

### 3. Subir a GitHub

```bash
git init
git add .
git commit -m "feat: EC2 Discord bot"
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

> ⚠️ **Usa un repositorio PRIVADO** para que tus secrets estén seguros.

### 4. Configurar GitHub Secrets

Ve a tu repo → **Settings → Secrets and variables → Actions → New repository secret**

Agrega estos secrets:

| Secret | Valor |
|--------|-------|
| `DISCORD_TOKEN` | Token del bot de Discord |
| `AWS_ACCESS_KEY_ID` | Access Key de IAM |
| `AWS_SECRET_ACCESS_KEY` | Secret Key de IAM |
| `AWS_REGION` | Región de tu instancia (e.g., `us-east-1`) |
| `EC2_INSTANCE_ID` | ID de la instancia (e.g., `i-0abc123def456`) |
| `ALLOWED_ROLE_ID` | *(opcional)* ID del rol de Discord con permiso |

### 5. ¡Listo! 🎉

El bot arrancará automáticamente. También puedes ir a **Actions → Discord Bot Runner → Run workflow** para lanzarlo manualmente.

---

## 🛡️ Estrategia anti-ban de GitHub

Este proyecto usa una estrategia cuidadosa para **no violar los ToS de GitHub Actions**:

| Aspecto | Estrategia |
|---------|-----------|
| **Duración por ejecución** | ~5 horas (límite de GitHub: 6h) |
| **Frecuencia** | Cada 5 horas vía cron |
| **Minutos/mes estimados** | ~600 de 2000 gratis (30%) |
| **Concurrencia** | Solo 1 instancia a la vez (`cancel-in-progress`) |
| **Keep-alive** | Commit automático cada 50 días para que el cron no se desactive |
| **Sin crypto mining** | ✅ Solo ejecuta un bot liviano de Python |

### ⚠️ Consideraciones importantes

1. **GitHub Actions tiene un límite de 2,000 minutos/mes** en repos privados (plan Free). Con la config actual usarás ~600 min/mes.
2. Si necesitas el bot **24/7 sin interrupciones**, considera:
   - Una EC2 `t2.micro` (free tier) para hostear el bot
   - [Railway](https://railway.app) o [Render](https://render.com) (tier gratuito)
   - Un VPS barato (\$3-5/mes)
3. El bot tendrá **gaps de ~1 minuto** entre cada reinicio (mientras se instalan las dependencias).
4. Los repos **públicos** tienen minutos ilimitados, pero ¡**no expongas tus secrets**! Usa siempre GitHub Secrets.

---

## 📂 Estructura del proyecto

```
BOT DISCORD/
├── bot.py                          # Bot principal
├── requirements.txt                # Dependencias Python
├── .env.example                    # Plantilla de variables de entorno
├── .gitignore                      # Archivos ignorados por git
├── README.md                       # Este archivo
└── .github/
    └── workflows/
        ├── bot.yml                 # Workflow que ejecuta el bot
        └── keep-alive.yml          # Workflow que mantiene el repo activo
```

---

## 🏠 Ejecución local (desarrollo)

```bash
# 1. Clonar el repo
git clone https://github.com/TU_USUARIO/TU_REPO.git
cd TU_REPO

# 2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar y configurar variables de entorno
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac
# Editar .env con tus valores reales

# 5. Ejecutar
python bot.py
```

---

## 📜 Licencia

MIT — Usa como quieras.
