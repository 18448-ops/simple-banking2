pipeline {
    agent any

    environment {
        IMAGE = "simple-banking:latest"
        KUBECONFIG = "${HOME}/.kube/config"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                    pytest || true
                '''
            }
        }

        stage('Analyse SAST avec SonarQube') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh 'sonar-scanner'
                }
            }
        }

        stage('Build Docker') {
            steps {
                sh 'docker build -t $IMAGE .'
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            steps {
                sh 'trivy image $IMAGE || true'
            }
        }

        stage('Déploiement sur Minikube') {
            steps {
                sh '''
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml
                '''
            }
        }

        stage('Rapports finaux') {
            steps {
                echo '📊 Envoi ou stockage des rapports.'
            }
        }
    }

    post {
        always {
            echo '✅ Pipeline terminé, avec ou sans succès.'
        }
        failure {
            echo '❌ Une erreur est survenue durant le pipeline.'
        }
    }
}

