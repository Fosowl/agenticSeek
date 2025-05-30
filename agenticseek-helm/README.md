## Local Installation with Kind and Helm


### Prerequisites
- Docker installed
- `kubectl`, `kind`, and `helm` CLI tools installed

### 1. Create a Kind Cluster
```bash
# Create a minimal Kind cluster configuration
cat <<EOF | kind create cluster --name agenticseek --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraMounts:
  - hostPath: ./screenshots  # Mount screenshots directory
    containerPath: /mnt/screenshots
EOF



# Build the frontend image
docker build -t agenticseek-frontend:latest -f ./frontend/Dockerfile.frontend ./frontend

# Load image into Kind cluster
kind load docker-image agenticseek-frontend:latest --name agenticseek

# Deploy Helm chart
helm dependency update ./agenticseek-helm
helm install agenticseek ./agenticseek-helm
# Update Helm dependencies
helm dependency update ./agenticseek-helm

# Install the chart
helm install agenticseek ./agenticseek-helm

# Wait for pods to be ready
kubectl wait --for=condition=Ready pods --all --timeout=120s

# Forward frontend port locally
kubectl port-forward service/frontend 3000:3000 &

# Forward searxng port locally
kubectl port-forward service/searxng 8080:8080 &

# Check pod status
kubectl get pods

# Check persistent volumes
kubectl get pvc

# View logs for a component
kubectl logs deploy/frontend -f


# Delete Helm release
helm uninstall agenticseek

# Delete Kind cluster
kind delete cluster --name agenticseek