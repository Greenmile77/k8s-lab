# Отчет по лабораторной работе №3
## Развертывание приложения в Kubernetes (Minikube)

**Вариант 4:** Финансы - Portfolio Report Gen (CronJob)

**Студент:** [Ваше имя]  
**Группа:** [Ваша группа]  
**Дата:** 26.03.2026

---

### 1. Цель работы

Получить практические навыки оркестрации контейнеризированных приложений в среде Kubernetes. Научиться транслировать архитектуру Docker Compose в манифесты K8s, управлять конфигурациями (ConfigMaps/Secrets), обеспечивать персистентность данных (PVC) и жизнеспособность сервисов (Probes).

---

### 2. Архитектура решения

| Компонент | В Docker Compose | В Kubernetes |
|-----------|------------------|--------------|
| **База данных** | Service db + volume | Deployment + PVC + Service (ClusterIP) |
| **Приложение** | Service app | Deployment + Service (NodePort) + Probes |
| **Загрузчик** | Service loader (разовый) | CronJob (каждые 5 минут) |
| **Конфигурация** | .env файл | ConfigMap + Secret |

---

### 3. Манифесты Kubernetes

#### 3.1 Secret (пароли)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: portfolio-secret
type: Opaque
data:
  POSTGRES_USER: cG9ydGZvbGlvX3VzZXI=
  POSTGRES_PASSWORD: c2VjdXJlX3Bhc3N3b3JkXzEyMw==
3.2 ConfigMap (несекретные настройки)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
3.3 PersistentVolumeClaim (для БД)
yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
3.4 PostgreSQL Deployment
yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: portfolio-config
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: portfolio-secret
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: portfolio-secret
              key: POSTGRES_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - portfolio_user
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - portfolio_user
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
3.5 Service для PostgreSQL (ClusterIP)
yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
3.6 Application Deployment (с InitContainer)
yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      initContainers:
      - name: wait-for-postgres
        image: busybox:1.35
        command: ['sh', '-c', 'until nc -z postgres-service 5432; do echo waiting; sleep 2; done;']
      containers:
      - name: app
        image: portfolio-app:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
        env:
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: portfolio-config
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: portfolio-secret
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: portfolio-secret
              key: POSTGRES_PASSWORD
        - name: POSTGRES_HOST
          valueFrom:
            configMapKeyRef:
              name: portfolio-config
              key: POSTGRES_HOST
        - name: POSTGRES_PORT
          valueFrom:
            configMapKeyRef:
              name: portfolio-config
              key: POSTGRES_PORT
3.7 Service для приложения (NodePort)
yaml
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: app
  ports:
  - port: 8080
    targetPort: 8080
    nodePort: 30001
  type: NodePort
3.8 CronJob для загрузчика (Вариант 4 - каждые 5 минут)
yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: data-loader
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: loader
            image: portfolio-loader:latest
            imagePullPolicy: IfNotPresent
            env:
            - name: POSTGRES_DB
              valueFrom:
                configMapKeyRef:
                  name: portfolio-config
                  key: POSTGRES_DB
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: portfolio-secret
                  key: POSTGRES_USER
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: portfolio-secret
                  key: POSTGRES_PASSWORD
            - name: POSTGRES_HOST
              valueFrom:
                configMapKeyRef:
                  name: portfolio-config
                  key: POSTGRES_HOST
            - name: POSTGRES_PORT
              valueFrom:
                configMapKeyRef:
                  name: portfolio-config
                  key: POSTGRES_PORT

