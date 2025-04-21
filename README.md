
# URL Shortener - Deployment Guide with Minikube and Ingress


1. **Log in to Docker Hub:**

   docker login

2. **Build the Docker image:**
  
   docker build -t pes2ug22cs545/url-shortener-app .


3. **Push the image to Docker Hub:**
   ```bash
   docker push pes2ug22cs545/url-shortener-app
   ```

---

## Minikube Setup

1. **Start Minikube:**
   ```bash
   minikube start
   ```

2. **Install Metrics Server:**
   ```bash
   kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
   ```

3. **Verify Metrics Server Installation:**
   ```bash
   kubectl get deployment metrics-server -n kube-system
   ```

---

## Ingress Setup

1. **Enable NGINX Ingress Controller:**
   ```bash
   minikube addons enable ingress
   ```

2. **Verify NGINX Ingress Controller:**
   ```bash
   kubectl get pods -n ingress-nginx
   ```

---

## Update Ingress Service

1. **Delete existing Kubernetes resources (if needed):**
   ```bash
   kubectl delete -f kubernetes/
   ```

2. **Edit the ingress service to use LoadBalancer:**
   ```bash
   kubectl edit svc ingress-nginx-controller -n ingress-nginx
   ```
   Change 
   type: NodePort
   To
   type: LoadBalancer

3. **Export and reapply the modified service:**
   ```bash
   kubectl get svc ingress-nginx-controller -n ingress-nginx -o yaml > svc.yaml
   kubectl apply -f svc.yaml
   ```

4. **Apply your Kubernetes manifests:**
   ```bash
   kubectl apply -f kubernetes/
   ```

5. **Check for External IP (it may show as `pending`):**
   ```bash
   kubectl get svc -n ingress-nginx
   ```

---

do minikube tunnel 

Make sure your hosts file has a mapping of 127.0.0.1 to url-shortener.local
## Send a POST Request

Once everything is up and running, send a POST request to:

```
http://url-shortener.local/shorten
```

With the following JSON body:

```json
{
  "url": "https://www.youtube.com/"
}
```

---
##Stress Testing
1. Install Chocolatey
   Open PowerShell as administrator and run:
   Set-ExecutionPolicy Bypass -Scope Process -Force; `
   [System.Net.ServicePointManager]::SecurityProtocol = `
   [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
2. Check whether chocolatey is installed- choco -v
3. Install Apache Bench:
   choco install apache-httpd
   Add Apche Bench to environment variables "C:\Users\shaun\AppData\Roaming\Apache24\bin" and check if its installed with ab -V
4. Now open 2 other terminals. On one terminal run "kubectl get hpa -w". Other terminal run "kubectl get pods -l app=url-shortener -w"
5. On another terminal run " ab -n 1000 -c 50 -T "application/json" -p payload.json http://shortener.local/shorten"
6. If there are no changes check whether metrscs server is up "kubectl get deployment metrics-server -n kube-system
"

