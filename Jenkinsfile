pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        SONARQUBE = 'sonarqube' // Nom de la configuration SonarQube dans Jenkins
        DOCKER_REGISTRY = 'registry.example.com' // Remplacer par ton registre
        APP_NAME = 'simple-banking'
        KUBECONFIG = '/home/jenkins/.kube/config'
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building application...'
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pytest --maxfail=1 --disable-warnings -q
                '''
            }
        }

        stage('Analyse SAST avec SonarQube') {
            steps {
                withSonarQubeEnv(SONARQUBE) {
                    echo 'Running SonarQube scan...'
                    sh 'sonar-scanner'
                }
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            steps {
                echo 'Scanning Docker image for vulnerabilities...'
                sh '''
                    docker build -t ${APP_NAME}:latest .
                    trivy image --exit-code 1 --severity CRITICAL ${APP_NAME}:latest || true
                '''
            }
        }

        stage('Build Docker') {
            steps {
                echo 'Building Docker image...'
                sh '''
                    docker build -t ${DOCKER_REGISTRY}/${APP_NAME}:latest .
                    docker push ${DOCKER_REGISTRY}/${APP_NAME}:latest
                '''
            }
        }

        stage('Déploiement sur Minikube (VM1)') {
            steps {
                echo 'Deploying application on Kubernetes...'
                sh '''
                    export KUBECONFIG=${KUBECONFIG}
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml
                '''
            }
        }

        stage('Monitoring & Alertes') {
            steps {
                echo 'Collecting metrics and sending alerts...'
                sh '''
                    # Exemple: appeler script Python d'alerte si seuils dépassés
                    python3 scripts/send_alerts.py
                '''
            }
        }

        stage('Reporting automatisé') {
            steps {
                echo 'Generating PDF/HTML reports...'
                sh '''
                    python3 scripts/generate_reports.py
                '''
            }
        }

        stage('Red Team / Simulation attaques (VM4)') {
            steps {
                echo 'Launching Red Team tests...'
                sh '''
                    # Exemple: appeler script de simulation d'attaques
                    python3 scripts/red_team_simulation.py
                '''
            }
        }

    }

    post {
        always {
            echo 'Pipeline finished (main branch)'
        }
        success {
            echo '✅ Pipeline executed successfully!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}

