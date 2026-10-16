# ClinicFlow — Clinic Appointment System (DevOps Capstone)

ClinicFlow is a small clinic front-desk application. Reception staff can **book patient appointments**, **check patients in**, **mark visits completed** or **cancel** them, and see a live dashboard of today's appointment counts and the "up next" queue.

It is built and shipped end-to-end with a production-style DevOps toolchain:

| Layer | Tools |
|---|---|
| Frontend | React + Vite, responsive CSS, served by Nginx (non-root) |
| Backend | FastAPI (Python 3.12), SQLAlchemy, Alembic, Pydantic |
| Database | PostgreSQL 16 |
| Tests | Pytest (isolated SQLite test DB) |
| Containers | Docker, Docker Compose |
| CI/CD | GitHub Actions → GHCR (images tagged with commit SHA) |
| Security | Trivy image scan (fails on HIGH/CRITICAL) |
| Infrastructure | Terraform → AWS VPC + EKS (`ap-southeast-2`) |
| Orchestration | Kubernetes, Helm, Ingress (ingress-nginx), HPA |
| Observability | Prometheus + Grafana (kube-prometheus-stack), `/metrics` |

```text
Developer → GitHub → GitHub Actions ─┬─ pytest + frontend build
                                     ├─ docker build (backend, frontend)
                                     ├─ Trivy scan
                                     ├─ push to GHCR (tag = commit SHA)
                                     └─ helm upgrade --install  ──►  AWS EKS (Terraform: VPC + EKS)
                                                                        │
                                              Ingress  /  → frontend (Nginx + React)
                                                       /api → backend (FastAPI) → PostgreSQL (PVC)
                                                                        │
                                                         Prometheus (ServiceMonitor) → Grafana
```

- **Repository:** https://github.com/shubhamk0205/clinicflow
- **CI/CD runs:** https://github.com/shubhamk0205/clinicflow/actions
- **Images:** `ghcr.io/shubhamk0205/clinicflow-backend` and `ghcr.io/shubhamk0205/clinicflow-frontend`

---

## Submission evidence (by grading module)

All screenshots are in [`docs/screenshots/`](docs/screenshots). They were taken from the running system: the local Docker Compose stack and the EKS cluster in `ap-southeast-2`. Terminal screenshots are rendered from the real command output.

### M1 — Application (frontend + backend + database)

Dashboard served from EKS through the Ingress load balancer:

![ClinicFlow dashboard](docs/screenshots/app-dashboard.png)

Booking modal and the responsive mobile layout:

<p>
  <img src="docs/screenshots/app-book-modal.png" alt="Book appointment modal" width="68%">
  <img src="docs/screenshots/app-mobile.png" alt="Mobile layout" width="24%">
</p>

REST API in Swagger (`/docs`): 5 CRUD endpoints, stats, health, readiness and metrics:

![Swagger UI](docs/screenshots/swagger.png)

### M2 — Testing (pytest)

11 tests against an isolated SQLite test database (`tests/conftest.py`, `pytest.ini`):

![pytest -v](docs/screenshots/term-pytest.png)

### M3 — Git and GitHub

![git log](docs/screenshots/term-gitlog.png)

![GitHub commit history](docs/screenshots/github-commits.png)

### M4 — Docker + Compose

`docker compose up --build` starts postgres, backend and frontend. Both app images run as non-root (uid 10001 / 101), and the data lands in PostgreSQL:

![docker compose](docs/screenshots/term-compose.png)

![localhost:3000](docs/screenshots/localhost-3000.png)

### M5 — CI/CD (GitHub Actions → GHCR)

Pipeline on push to `main`: pytest + frontend build → Docker build → Trivy → push to GHCR. Image tags are the commit SHA:

![GitHub Actions run](docs/screenshots/github-actions-run.png)

![GitHub Actions history](docs/screenshots/github-actions-list.png)

![GHCR packages](docs/screenshots/ghcr-packages.png)

![GHCR SHA tags](docs/screenshots/ghcr-backend.png)

### M6 — DevSecOps (Trivy)

Both images scanned in CI with `severity: HIGH,CRITICAL` and `exit-code: 1`. Result: 0 vulnerabilities (see [Security — Trivy](#security--trivy) for the explanation):

![Trivy scan](docs/screenshots/term-trivy.png)

### M7 — Terraform (AWS VPC + EKS)

`terraform plan`: 61 resources, including the VPC, 2 public + 2 private subnets, NAT gateway, EKS cluster and managed node group:

![terraform plan](docs/screenshots/term-tfplan.png)

`terraform apply` outputs and the EKS worker nodes:

![terraform output](docs/screenshots/term-tfoutput.png)

![kubectl get nodes](docs/screenshots/term-nodes.png)

### M8 — Kubernetes + Helm

![kubectl get pods](docs/screenshots/term-pods.png)

![kubectl get svc,ingress](docs/screenshots/term-svc.png)

![helm list](docs/screenshots/term-helm.png)

HPA scaling the backend from 2 → 4 replicas under load:

![HPA](docs/screenshots/term-hpa.png)

Troubleshooting labs:

![broken image](docs/screenshots/term-broken-image.png)

![broken service](docs/screenshots/term-broken-service.png)

### M9 — Observability (Prometheus + Grafana)

Backend `/metrics`:

![metrics](docs/screenshots/metrics.png)

Prometheus scraping every backend pod through the ServiceMonitor (all **UP**):

![Prometheus targets](docs/screenshots/prometheus-targets.png)

![Prometheus query](docs/screenshots/prometheus-query.png)

Grafana "ClinicFlow API" dashboard with live data (requests/s, p95 latency, 5xx rate, backend pods during the HPA test):

![Grafana dashboard](docs/screenshots/grafana-dashboard.png)

### M10 — Commit → pipeline → deployment

A UI fix was committed and pushed. GitHub Actions tested, built, scanned and pushed the images for that commit, and Helm rolled the new SHA out to EKS (revision 3):

![Helm rollout of new SHA](docs/screenshots/term-rollout.png)

---

## Repository structure

```text
.
├── backend/                  # FastAPI app
│   ├── app/                  # main.py (routes), models.py, schemas.py, db.py, config.py
│   ├── alembic/versions/     # DB migrations
│   ├── tests/                # pytest tests + conftest.py
│   ├── pytest.ini
│   └── Dockerfile
├── frontend/                 # React + Vite app, nginx.conf, multi-stage Dockerfile
├── docker-compose.yml        # postgres + backend + frontend
├── .github/workflows/        # CI/CD pipeline
├── terraform/                # AWS VPC + EKS
├── k8s/namespace.yaml
├── helm/clinicflow/          # Helm chart (deployments, services, ingress, HPA, postgres, monitoring)
├── monitoring/               # kube-prometheus-stack values
├── troubleshooting/          # deliberately broken manifests
└── scripts/load-test.sh      # traffic generator for HPA / Grafana demo
```

---

## Backend API

| Method | Path | Description |
|---|---|---|
| GET | `/` | Service info |
| GET | `/health` | Liveness — app process is up |
| GET | `/ready` | Readiness — database reachable |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api/appointments` | List appointments (ordered by time) |
| GET | `/api/appointments/{id}` | Get one appointment |
| POST | `/api/appointments` | Book an appointment |
| PUT | `/api/appointments/{id}` | Update (e.g. status → `CHECKED_IN`) |
| DELETE | `/api/appointments/{id}` | Delete an appointment |
| GET | `/api/appointments/stats` | Counts per status |

Swagger UI: `http://localhost:8000/docs`

Appointment fields: `patient_name`, `patient_phone`, `doctor`, `department` (`GENERAL`, `CARDIOLOGY`, `DERMATOLOGY`, `PEDIATRICS`, `ORTHOPEDICS`), `scheduled_at`, `reason`, `status` (`SCHEDULED`, `CHECKED_IN`, `COMPLETED`, `CANCELLED`).

Example:

```bash
curl -X POST http://localhost:8000/api/appointments \
  -H 'Content-Type: application/json' \
  -d '{"patient_name":"Priya Verma","doctor":"Dr. Mehta","department":"CARDIOLOGY","scheduled_at":"2026-10-20T10:00:00+05:30","reason":"Follow-up"}'
```

---

## Run locally with Docker Compose

```bash
docker compose up --build
```

- App: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health / metrics: http://localhost:8000/health, http://localhost:8000/metrics

The backend runs `alembic upgrade head` before starting, so the `appointments` table is created automatically. Show the table:

```bash
docker compose exec postgres psql -U clinicflow -c "select * from appointments;"
```

Stop (`-v` also deletes the DB volume):

```bash
docker compose down -v
```

> If port 3000 is already in use on your machine, stop the other process first (`lsof -i :3000`).

Both images run as non-root: backend as uid `10001`, frontend as uid `101` (`nginx-unprivileged`).

### Run the backend without Docker

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL='postgresql+psycopg://clinicflow:clinicflow@localhost:5432/clinicflow'
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Frontend dev server (proxies `/api` to `localhost:8000`):

```bash
cd frontend && npm install && npm run dev
```

---

## Tests

```bash
cd backend
pytest -v
```

11 tests cover health, readiness, metrics, and create/list/get/update/delete/stats plus validation and 404 cases. `tests/conftest.py` points `DATABASE_URL` at a throwaway SQLite file **before** the app is imported, so tests never touch PostgreSQL. Each test gets a fresh schema.

---

## CI/CD — GitHub Actions

`.github/workflows/ci-cd.yml` runs on every push and pull request to `main`:

1. **test** — `pytest` (a failure stops the pipeline) and `npm ci && npm run build`
2. **build-scan-push** — builds both images tagged `ghcr.io/shubhamk0205/clinicflow-{backend,frontend}:<commit-sha>`, scans both with Trivy, then pushes to GHCR (on push only)
3. **deploy** — `helm upgrade --install` to EKS with the new SHA tag (on push to `main` only)

### One-time GitHub setup

1. Create the repo `github.com/shubhamk0205/<repo>` and push:
   ```bash
   git init && git add . && git commit -m "Add ClinicFlow appointment app with full DevOps pipeline"
   git branch -M main
   git remote add origin https://github.com/shubhamk0205/<repo>.git
   git push -u origin main
   ```
2. After the first push, open each package (GitHub profile → Packages → `clinicflow-backend` / `clinicflow-frontend`) → *Package settings* → set visibility to **Public**, so the cluster can pull without credentials.
3. To enable the deploy job (only while the EKS cluster exists):
   - *Settings → Secrets and variables → Actions → Secrets*: add `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
   - *Variables*: add `DEPLOY_ENABLED` = `true`
   - Remove the variable (or set it to `false`) after `terraform destroy`, so the pipeline stays green.

---

## Security — Trivy

The pipeline scans both container images with Trivy for **HIGH** and **CRITICAL** CVEs that have a fix available (`ignore-unfixed: true`). If any are found, the job exits with code 1 and nothing is pushed.

**What Trivy scanned and what the result means:** Trivy inspected the OS packages of each base image (Debian for the backend, Alpine for the Nginx frontend) and the Python packages installed from `requirements.txt`. An early scan of this project flagged **CVE-2025-62727** (HIGH) in Starlette 0.41.3, a denial-of-service via crafted HTTP `Range` headers. It also flagged OpenSSL/zlib/libxml2 CVEs in an older Nginx Alpine base. These were fixed by upgrading FastAPI/Starlette and moving to `nginx-unprivileged:1.30-alpine` with `apk upgrade`, after which both scans are clean. A clean result means there are no *known, fixable* high-severity CVEs today. It does not prove the application is secure. Code scanning, dependency updates, secret scanning and runtime security are separate layers.

No secrets are committed. `.env`, `*.tfvars` and Terraform state are git-ignored, and AWS credentials live only in GitHub Secrets / your local AWS CLI.

---

## Terraform — AWS VPC + EKS

Creates, in `ap-southeast-2`:

- VPC `10.30.0.0/16` with **2 public + 2 private subnets** across 2 AZs, internet gateway and one NAT gateway
- EKS cluster `clinicflow-eks` (Kubernetes 1.31) with a managed node group (2× `m7i-flex.large`, free-tier eligible, scales 2–4)
- EKS add-ons: CoreDNS, kube-proxy, VPC CNI, **EBS CSI driver** (needed for the PostgreSQL PVC; it uses the node IAM role because the AWS Free plan blocks creating the OIDC provider that IRSA needs)

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # optional; defaults work
terraform init
terraform plan
terraform apply
aws eks update-kubeconfig --region ap-southeast-2 --name clinicflow-eks
```

> ⚠️ EKS and the NAT gateway cost money by the hour. Run `terraform destroy` as soon as you have your screenshots / demo. First uninstall the Helm releases (below) so the ingress load balancer is deleted before the VPC.

---

## Deploy to Kubernetes (EKS)

```bash
# 1. Namespace
kubectl apply -f k8s/namespace.yaml

# 2. Cluster add-ons: ingress controller, metrics-server (for HPA), Prometheus + Grafana
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace
helm install metrics-server metrics-server/metrics-server -n kube-system
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace -f monitoring/prometheus-values.yaml

# 3. ClinicFlow (CI does this automatically on every push to main)
helm upgrade --install clinicflow ./helm/clinicflow -n clinicflow \
  -f helm/clinicflow/values-prod.yaml \
  --set backend.tag=<commit-sha> --set frontend.tag=<commit-sha>
```

The chart deploys:

- `clinicflow-frontend` Deployment (2 replicas) + ClusterIP Service (80 → 8080)
- `clinicflow-backend` Deployment (HPA 2–6 replicas, CPU 60%) + ClusterIP Service (8000), with readiness `/ready` and liveness `/health` probes
- `clinicflow-postgres` Deployment + Service + Secret + 5Gi PVC
- Ingress: `/` → frontend, `/api` → backend
- ServiceMonitor (Prometheus scrapes `/metrics` every 15s) + Grafana dashboard ConfigMap

Check it:

```bash
kubectl get pods -n clinicflow
kubectl get svc -n clinicflow
kubectl get ingress -n clinicflow
kubectl get hpa -n clinicflow
helm list -n clinicflow
```

Open the app with the ingress load balancer hostname:

```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

**Local cluster (minikube / kind / Docker Desktop):** install ingress-nginx and metrics-server, then use `-f helm/clinicflow/values-dev.yaml` and add `127.0.0.1 clinicflow.local` (or the minikube IP) to `/etc/hosts`.

Rollback: `helm history clinicflow -n clinicflow` then `helm rollback clinicflow <revision> -n clinicflow`.

---

## Autoscaling demo (HPA)

```bash
kubectl get hpa -n clinicflow -w     # in one terminal
URL=http://<ingress-host>/api/appointments REQUESTS=20000 CONCURRENCY=50 ./scripts/load-test.sh
```

Watch CPU climb above 60% and the backend scale from 2 replicas up toward 6.

---

## Monitoring — Prometheus + Grafana

```bash
# Prometheus targets: look for serviceMonitor/clinicflow/clinicflow-backend = UP
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090
# → http://localhost:9090/targets

# Grafana (user: admin, password: from monitoring/prometheus-values.yaml)
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3001:80
# → http://localhost:3001 → Dashboards → "ClinicFlow API"
```

The **ClinicFlow API** dashboard is provisioned automatically with these panels: requests/sec per endpoint, p95 latency, 5xx error rate, and backend pods up. Run the load test to populate it.

Raw metrics: `kubectl port-forward -n clinicflow svc/clinicflow-backend 8000` then `curl localhost:8000/metrics`.

---

## Troubleshooting labs

**1. Broken image**

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n clinicflow                       # ImagePullBackOff
kubectl describe pod <pod> -n clinicflow              # "manifest unknown" for tag does-not-exist
kubectl get events -n clinicflow --sort-by=.lastTimestamp
kubectl delete -f troubleshooting/broken-image.yaml   # fix: use a real tag
```

**2. Service with no endpoints**

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get endpoints clinicflow-broken-service -n clinicflow   # <none>
kubectl get pods -n clinicflow --show-labels                     # no pod has app=label-that-does-not-exist
kubectl delete -f troubleshooting/broken-service.yaml
```

A Service finds Pods only through label selectors. If no labels match, there are no endpoints and no traffic.

---

## Final demo flow

1. Open ClinicFlow, book an appointment, then check it in.
2. Show `/docs` and run CRUD from Swagger.
3. Show the `appointments` table in PostgreSQL.
4. Make a small UI change and `git commit` + `git push`.
5. Watch GitHub Actions: tests → build → Trivy → GHCR → Helm deploy.
6. Show the SHA-tagged images in GHCR.
7. Walk through `terraform/` and show the VPC and EKS in the AWS Console.
8. Run `kubectl get pods,svc,ingress,hpa -n clinicflow` and `helm list -n clinicflow`.
9. Open the app through the Ingress hostname and show the change is live.
10. Run the load test and watch the HPA scale and Grafana panels move.
11. Break an image/Service and troubleshoot it live.

## Cleanup

```bash
helm uninstall clinicflow -n clinicflow
helm uninstall kube-prometheus-stack -n monitoring
helm uninstall ingress-nginx -n ingress-nginx
cd terraform && terraform destroy
```

---

Author: **Shubham Kapoor** ([@shubhamk0205](https://github.com/shubhamk0205))
