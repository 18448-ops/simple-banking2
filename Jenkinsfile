# ⬇️ Colle le code suivant dedans :
```
pipeline {
    agent any

    environment {
        IMAGE = "simple-banking:latest"
        REGISTRY = "simple-banking"
        KUBECONFIG = "~/.kube/config"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Tests') {
            steps {
                sh 'python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt && pytest'
            }
        }

        stage('Analyse SAST avec SonarQube') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh 'sonar-scanner'
                }
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            steps {
                sh 'docker build -t $IMAGE .'
                sh 'trivy image $IMAGE || true'
            }
        }

        stage('Build Docker') {
            steps {
                sh 'docker build -t $IMAGE .'
            }
        }

        stage('Déploiement sur Minikube') {
            steps {
                sh 'kubectl apply -f k8s/deployment.yaml'
                sh 'kubectl apply -f k8s/service.yaml'
            }
        }

        stage('Rapports finaux') {
            steps {
                echo 'Envoi ou stockage des rapports.'
            }
        }
    }
}
```

