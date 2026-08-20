# EduSense AI — AWS Production Deployment Strategy

This guide provides step-by-step instructions for deploying the **EduSense AI** platform to Amazon Web Services (AWS) using production best practices, multi-container orchestration, and managed cloud infrastructure.

---

## 🏗️ Recommended AWS Architecture

```
                      +-----------------------------+
                      |   AWS Route 53 (DNS) &     |
                      |   CloudFront (CDN) / ACM    |
                      +--------------+--------------+
                                     |
                                     v
                      +--------------+--------------+
                      |   Application Load Balancer |
                      |           (ALB)             |
                      +-------+--------------+------+
                              |              |
              Port 8501 (HTTP)|              | Port 8000 (HTTP)
                              v              v
               +--------------+----+    +----+--------------+
               |  AWS ECS Fargate  |    |  AWS ECS Fargate  |
               |  Frontend Task    |    |  Backend Task     |
               | (Streamlit UI)    |    | (FastAPI Service) |
               +-------------------+    +----+--------------+
                                             |
                               +-------------+-------------+
                               |                           |
                               v                           v
                    +----------+---------+     +-----------+----------+
                    |  AWS RDS PostgreSQL|     | AWS ECR Container Reg. |
                    |  (Managed Database)|     | (Docker Images)          |
                    +--------------------+     +--------------------------+
```

---

## 🚀 Step 1: Push Docker Images to AWS ECR

1. **Authenticate Docker CLI to AWS ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com
   ```

2. **Create ECR Repositories**:
   ```bash
   aws ecr create-repository --repository-name edusense-backend
   aws ecr create-repository --repository-name edusense-frontend
   ```

3. **Build, Tag, and Push Docker Images**:
   ```bash
   # Backend Image
   docker build -t edusense-backend -f Dockerfile .
   docker tag edusense-backend:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edusense-backend:latest
   docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edusense-backend:latest

   # Frontend Image
   docker build -t edusense-frontend -f Dockerfile.frontend .
   docker tag edusense-frontend:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edusense-frontend:latest
   docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edusense-frontend:latest
   ```

---

## 🗄️ Step 2: Provision Managed Database (AWS RDS PostgreSQL)

1. Provision a multi-AZ **Amazon RDS PostgreSQL** instance (`db.t4g.micro` or `db.m6g.large`).
2. Retrieve Database Connection String:
   ```env
   DATABASE_URL=postgresql://edusense_user:<DB_PASSWORD>@edusense-db.c123456789.us-east-1.rds.amazonaws.com:5432/edusense_db
   ```
3. Run Alembic or DB table creation on initial boot:
   ```bash
   python -c "from app.db.session import init_db; init_db()"
   ```

---

## ☁️ Step 3: Deploy Service Tasks on AWS ECS Fargate

1. **Create ECS Cluster**:
   ```bash
   aws ecs create-cluster --cluster-name edusense-production-cluster
   ```

2. **Backend Task Definition (`backend-task.json`)**:
   ```json
   {
     "family": "edusense-backend-task",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "512",
     "memory": "1024",
     "containerDefinitions": [
       {
         "name": "edusense-backend",
         "image": "<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edusense-backend:latest",
         "portMappings": [{ "containerPort": 8000 }],
         "environment": [
           { "name": "APP_NAME", "value": "EduSense AI" },
           { "name": "APP_ENV", "value": "production" }
         ],
         "secrets": [
           { "name": "DATABASE_URL", "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:edusense/db_url" },
           { "name": "SECRET_KEY", "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:edusense/jwt_secret" }
         ],
         "healthCheck": {
           "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
           "interval": 30,
           "timeout": 5,
           "retries": 3
         }
       }
     ]
   }
   ```

3. **Frontend Task Definition (`frontend-task.json`)**:
   ```json
   {
     "family": "edusense-frontend-task",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "containerDefinitions": [
       {
         "name": "edusense-frontend",
         "image": "<AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/edusense-frontend:latest",
         "portMappings": [{ "containerPort": 8501 }],
         "environment": [
           { "name": "API_BASE_URL", "value": "http://edusense-backend.internal:8000" }
         ]
       }
     ]
   }
   ```

---

## ⚡ Option B: Rapid Deployment with AWS App Runner

For zero-infrastructure management, deploy using **AWS App Runner**:

1. Open AWS App Runner Console ➔ **Create Service**.
2. Source: **Container Registry (ECR)** ➔ Select `edusense-backend:latest`.
3. Port: `8000`, Environment Variables: set `DATABASE_URL` and `SECRET_KEY`.
4. Deploy! App Runner automatically provides HTTPS SSL certificates and auto-scaling.

---

## 🛡️ Production Checklist

- [x] Configure HTTPS SSL Certificates via AWS Certificate Manager (ACM).
- [x] Store JWT secrets and database passwords in **AWS Secrets Manager**.
- [x] Enable AWS CloudWatch logs for structured JSON error tracing.
- [x] Configure ALB Health Check Target Group path: `/health`.
- [x] Enable Auto-scaling (scale tasks between 2 and 10 based on CPU/RAM threshold >= 75%).
