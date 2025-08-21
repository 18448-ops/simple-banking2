pipeline {
    agent any

    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        PYTHONPATH = "${WORKSPACE}/src" // Ajouté pour que Python trouve les packages
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT = "test" // test pour SQLite, dev/prod pour PostgreSQL
        DATABASE_URL = "${env.ENVIRONMENT == 'test' ? 'sqlite:///./test_banking.db' : (env.DATABASE_URL ?: 'postgresql://postgres:admin@localhost/banking')}"
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo "Création de la virtualenv et installation des dépendances..."
                sh """
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Test') {
            steps {
                echo "Exécution des tests..."
                sh """
                    . ${VENV_DIR}/bin/activate
                    export DATABASE_URL="$DATABASE_URL"
                    export PYTHONPATH="$PYTHONPATH"
                    pytest --maxfail=1 --disable-warnings -q
                """
            }
        }

        stage('Analyse SAST avec SonarQube') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "Analyse SAST avec SonarQube..."
                withSonarQubeEnv('sonarqube') { // nom du serveur configuré dans Jenkins
                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                        sh """
                            sonar-scanner \
                              -Dsonar.projectKey=simple-banking \
                              -Dsonar.sources=src \
                              -Dsonar.host.url=$SONAR_HOST_URL \
                              -Dsonar.login=$SONAR_TOKEN
                        """
                    }
                }
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "Scan des vulnérabilités avec Trivy..."
                sh "trivy fs --exit-code 1 --severity CRITICAL,HIGH ."
            }
        }

        stage('Build Docker') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "Construction de l'image Docker..."
                sh "docker build -t simple-banking:latest ."
            }
        }

        stage('Monitoring & Alertes') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "Vérification du monitoring et alertes..."
                sh "echo 'Monitoring et alertes à configurer ici'"
            }
        }

        stage('Reporting automatisé') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "Génération du reporting automatisé..."
                sh "echo 'Reporting automatisé à configurer ici'"
            }
        }

        stage('Red Team / Simulation attaques (VM4)') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "Simulation attaques Red Team..."
                sh "echo 'Simulation d'attaques à configurer ici'"
            }
        }
    }

    post {
        always { echo "Pipeline terminé" }
        success { echo "✅ Pipeline réussi" }
        failure { echo "❌ Pipeline échoué" }
    }
}

