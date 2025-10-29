## Deployment setup — Roboshop (backend on Railway, frontend on Netlify)

This document explains how to deploy the repository's backend to Railway, the frontend to Netlify, how to optionally publish backend images to GitHub Container Registry (GHCR), how to smoke-test locally with Docker Compose, and which secrets/env vars to rotate and set.

Please DO NOT add any secrets back into the repository. Use Railway/Netlify/GitHub secrets or environment variables.

---

## 1. Immediate security steps (do these first)

- Rotate any exposed tokens immediately. In particular:
  - Revoke the old Hugging Face token that was in `backend/.env` and create a new one.
  - Rotate any database credentials if they were in `backend/.env`.

- Do not commit rotated tokens into Git. Use the hosting provider's environment variables or GitHub Secrets.

---

## 2. Local smoke test (Docker Compose)

Purpose: Validate the app builds and DB initialization locally before cloud deploy.

Prerequisites:
- Docker Desktop running
- PowerShell (Windows)

Create a local `.env` file for Docker Compose (do NOT commit):

```powershell
cd C:\Users\rubay\Documents\gadgets-store
Set-Content -Path backend\.env -Value @'
MYSQL_ROOT_PASSWORD=local_root_pw
MYSQL_DATABASE=roboshop
MYSQL_USER=roboshop_user
MYSQL_PASSWORD=roboshop_pw
HUGGINGFACE_API_TOKEN=<YOUR_NEW_HF_TOKEN>
FLASK_ENV=production
'@
```

Start services:

```powershell
docker-compose up --build
```

If your `backend` container doesn't auto-initialize the DB, run:

```powershell
docker-compose exec backend python backend/setup_database.py --non-interactive
```

Smoke test the API (adjust port if different):

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/health
```

Stop and remove containers when done:

```powershell
docker-compose down
```

---

## 3. Railway — Backend deployment (Dockerfile)

Railway supports Dockerfile-based deployments. Use `Dockerfile.railway` at the repo root or `backend/Dockerfile`.

Steps:

1. Sign in to Railway (https://railway.app) and create a new project.
2. Connect the GitHub repository `MMI122/roboshop`.
3. Add a new service; choose "Deploy from Dockerfile" and point to `Dockerfile.railway` or specify the `backend` directory and `backend/Dockerfile`.
4. Add environment variables in the Railway project settings. Set values for:
   - MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD
   - HUGGINGFACE_API_TOKEN
   - FLASK_ENV=production
   - SECRET_KEY (Flask secret key)

If you prefer Railway-managed database:
- Add the MySQL plugin in Railway; Railway will provide connection values — add them to the service variables or accept Railway-injected values.

Database initialization:
- Use Railway one-off commands to run the DB initialization script after the service is deployed:

```text
Run one-off: python backend/setup_database.py --non-interactive
```

Start command / WSGI:
- Ensure the container runs your Flask app via a production server, e.g.:

```
gunicorn -b 0.0.0.0:$PORT app:app
```

Railway will set the `$PORT` env var. Confirm your Dockerfile or entrypoint reads it.

---

## 4. Netlify — Frontend deployment

Option A — Connect Netlify directly to GitHub (recommended):

1. On Netlify, "Add new site from Git" and connect to `MMI122/roboshop`.
2. Set the base directory to `frontend` in the site settings (so builds run from that folder).
3. Build command: `npm run build` (or `pnpm build` if used). Publish directory: `dist`.
4. Add build-time environment variables:
   - REACT_APP_API_URL or VITE_API_URL pointing to your Railway backend public URL.

Option B — Use GitHub Actions to deploy (already included):
- Add these repository secrets in GitHub: `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`.
- The existing workflow will build and deploy on push.

---

## 5. Optional — Publish backend image to GHCR (GitHub Container Registry)

If you want to build images in CI and publish them:

1. Create a GitHub PAT with `write:packages` and `repo` (if repo is private).
2. Add the PAT in GitHub secrets as `GHCR_PAT` (or the name used in your workflow).
3. Configure workflow permissions:

```yaml
permissions:
  contents: read
  packages: write
  id-token: write
```

4. The workflow may push built images to `ghcr.io/<owner>/<repo>:tag` — Railway (or other hosts) can pull using those credentials.

Note: GitHub Packages can often be written using the built-in `GITHUB_TOKEN` if repository settings allow packages write.

---

## 6. Required repository secrets and names (summary)

- HUGGINGFACE_API_TOKEN — used by backend to call HF inference API.
- MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD — DB connection.
- SECRET_KEY — Flask secret.
- NETLIFY_AUTH_TOKEN and NETLIFY_SITE_ID — for the Netlify GitHub Action.
- GHCR_PAT (if publishing images to GHCR from Actions).

Add these in:
- Railway variables (for backend runtime)
- Netlify site settings (for frontend build-time vars)
- GitHub -> Settings -> Secrets & variables -> Actions (for workflow secrets)

---

## 7. Checklist — recommended order

1. Rotate exposed tokens (Hugging Face, DB credentials).
2. Add rotated tokens to Railway/Netlify/GitHub secrets as needed.
3. Run local smoke test with Docker Compose.
4. Deploy backend to Railway and run DB initialization as a one-off task.
5. Deploy frontend to Netlify and set the API URL to the Railway backend.
6. Test end-to-end, and monitor logs.

---

## 8. If you want me to finish the deployment wiring for you

I can:
- Run a deep scan to confirm the sensitive blob is no longer reachable from any ref.
- Rewrite git history to remove `backend/.env` from all refs and force-push cleaned history (I will create a backup branch on the remote first).
- Help create the exact GitHub repo secrets and validate the workflow.

If you choose history rewrite, confirm you accept a force-push to the repository's `origin1` remote. I will create `backup-main-before-env-clean` on the remote before any destructive change.

---

## 9. Appendix — useful PowerShell commands

Create remote backup of main:

```powershell
cd C:\Users\rubay\Documents\gadgets-store
git push origin1 main:refs/heads/backup-main-before-env-clean
```

Create a local mirror and purge `backend/.env` (destructive, will rewrite history):

```powershell
rm -Recurse -Force C:\tmp\gadgets-store-mirror.git -ErrorAction SilentlyContinue
git clone --mirror . C:\tmp\gadgets-store-mirror.git
cd C:\tmp\gadgets-store-mirror.git
git filter-branch --force --index-filter "git rm -r --cached --ignore-unmatch backend/.env" --prune-empty -- --all
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force origin1 --all
git push --force origin1 --tags
```
