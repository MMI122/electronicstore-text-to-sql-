# Deploying on a free VM with Docker Compose (recommended robust free option)

This guide shows how to deploy the project on a free VM (for example Oracle Cloud Always Free) using Docker Compose.

Prerequisites
- A VM with Docker and Docker Compose installed
- Git installed on the VM
- A domain or use a public IP (Cloudflare recommended)

Steps

1. Clone the repo on the VM

   git clone https://github.com/<your-username>/roboshop.git
   cd roboshop

2. Create backend environment variables

   On the VM, create `backend/.env` (do NOT commit this file). Example:

   MYSQL_HOST=db
   MYSQL_USER=root
   MYSQL_PASSWORD=strongpassword
   MYSQL_DATABASE=gadgets_store
   SECRET_KEY=replace-with-random
   HUGGINGFACE_API_TOKEN=your_hf_token_if_any

3. Start services

   docker compose up -d --build

4. Initialize database (one-time)

   # run setup script inside backend container
   docker compose exec backend python setup_database.py

5. Verify

   - Backend: http://<vm-ip>:5000/
   - Frontend: http://<vm-ip>:3000/

TLS / production
- Use Cloudflare in front of the VM or install Let's Encrypt on the VM and configure Nginx reverse proxy.
