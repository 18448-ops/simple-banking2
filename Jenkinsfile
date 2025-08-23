pipeline {
    agent any

    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        PYTHONPATH = "${WORKSPACE}/src"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT = "test" // test pour SQLite, dev/prod pour PostgreSQL
        DATABASE_URL = "${env.ENVIRONMENT == 'test' ? 'sqlite:///./test_banking.db' : (env.DATABASE_URL ?: 'postgresql://user:password@192.168.189.135/mydb')}"
        SONARQUBE_URL = 'http://192.168.189.138:9000'  // URL de SonarQube
        SONARQUBE_TOKEN = credentials('sonarqube-token')  // Utilisation du token SonarQube stocké dans Jenkins
    }

    stages {

        stage('Install Python3-venv') {
          steps {
            echo "Installation du paquet python3-venv..."
            sh 'sudo apt-get update && sudo apt-get install -y python3.11-venv'
    }
}

        stage('Checkout SCM') {
            steps {
                echo "Clonage du code source..."
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
                withSonarQubeEnv('sonarqube') {
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                        sh """
                            ${tool 'sonar-scanner'}/bin/sonar-scanner \
                              -Dsonar.projectKey=simple-banking2 \
                              -Dsonar.sources=src \
                              -Dsonar.host.url=$SONARQUBE_URL \
                              -Dsonar.login=$SONAR_TOKEN
                        """
                    }
                }
            }
        }

        stage('Scan de vulnérabilités avec Trivy') {
            steps {
                echo 'Scan des vulnérabilités avec Trivy (code source)...'
                sh '''
                    # Scan du code source, ne bloque pas le pipeline si des vulnérabilités sont trouvées
                    trivy fs --severity CRITICAL,HIGH --format json --output trivy-report.json . || true
                '''
                archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
            }
        }

        stage('Build Docker') {
            steps {
                echo 'Construction de l\'image Docker...'
                sh 'docker build -t simple-banking2:latest .'
            }
        }

        stage('Scan Docker Image avec Trivy') {
            steps {
                echo 'Scan des vulnérabilités de l\'image Docker...'
                sh '''
                    # Scan de l'image Docker, ne bloque pas le pipeline si des vulnérabilités sont trouvées
                    trivy image --severity CRITICAL,HIGH --format json --output trivy-image-report.json simple-banking2:latest || true
                '''
                archiveArtifacts artifacts: 'trivy-image-report.json', allowEmptyArchive: true
            }
        }

        // Les autres étapes sont commentées pour l'instant
        /*

        stage('Monitoring & Alertes') {
            steps {
                echo "Vérification du monitoring et alertes..."
                sh "echo 'Monitoring et alertes à configurer ici'"
            }
        }

        stage('Reporting automatisé') {
            steps {
                echo "Génération du reporting automatisé..."
                sh "echo 'Reporting automatisé à configurer ici'"
            }
        }

        stage('Red Team / Simulation attaques (VM4)') {
            steps {
                echo "Simulation attaques Red Team..."
                sh "echo 'Simulation d'attaques à configurer ici'"
            }
        }
        */
    }

    post {
        always { echo "Pipeline terminé" }
        success { echo "✅ Pipeline réussi" }
        failure { echo "❌ Pipeline échoué" }
    }
}

