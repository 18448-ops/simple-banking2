pipeline {
    agent any

    environment {
        VENV_DIR      = "${WORKSPACE}/venv"
        PYTHONPATH    = "${WORKSPACE}/src"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT   = "test"
        SONARQUBE     = 'sonarqube'   // Nom configuré dans Jenkins → Manage Jenkins → System
        DATABASE_URL  = "postgresql://user:password@192.168.189.138:5432/mydb"
        DOCKER_IMAGE  = "maneldev131/simple-banking-api:latest"
        REPORT_DIR    = "reports"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                sh """
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov
                """
            }
        }

        stage('Test') {
            steps {
                sh """
                    . ${VENV_DIR}/bin/activate
                    if [ "$ENVIRONMENT" = "test" ]; then
                        export DATABASE_URL="sqlite:///./test_banking.db"
                    fi
                    pytest --maxfail=1 --disable-warnings -q \
                           --junitxml=pytest-report.xml \
                           --cov=src --cov-report=xml
                """
            }
            post {
                always {
                    junit 'pytest-report.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv("${SONARQUBE}") {
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                        script {
                            def scannerHome = tool 'sonar-scanner'
                            sh """
                                ${scannerHome}/bin/sonar-scanner \
                                  -Dsonar.projectKey=simple-banking2 \
                                  -Dsonar.sources=src \
                                  -Dsonar.python.coverage.reportPaths=coverage.xml \
                                  -Dsonar.host.url=http://192.168.189.138:9000 \
                                  -Dsonar.login=$SONAR_TOKEN
                            """
                        }
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE} ."
            }
        }

        stage('Trivy Scan') {
            steps {
                sh """
                    mkdir -p ${REPORT_DIR}
                    echo ">>> Running Trivy Scan"
                    trivy image --format json --output ${REPORT_DIR}/trivy_report.json ${DOCKER_IMAGE} || true
                """
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_IMAGE}
                    """
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                sh """
                    docker stop simple-banking-api || true
                    docker rm simple-banking-api || true
                    docker run -d --name simple-banking-api -p 8000:8000 ${DOCKER_IMAGE}
                """
            }
        }

        stage('Send Reports by Email') {
            steps {
                withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                    // Récupérer le rapport en HTML depuis SonarQube
                    sh """
                        mkdir -p ${REPORT_DIR}
                        curl -s -u $SONAR_TOKEN: \
                          "http://192.168.189.138:9000/dashboard?id=simple-banking2" \
                          -o ${REPORT_DIR}/sonarqube_report.html
                    """
                }

                // Convertir le rapport HTML SonarQube en PDF (si nécessaire, vous pouvez remplacer wkhtmltopdf par un autre outil de conversion)
                sh """
                    wkhtmltopdf ${REPORT_DIR}/sonarqube_report.html ${REPORT_DIR}/sonarqube_report.pdf
                """

                // Envoi des rapports par email avec les fichiers en pièce jointe
                emailext(
                    subject: "📊 Rapports SonarQube & Trivy - simple-banking2",
                    body: """Bonjour Manel,

Voici les rapports générés par SonarQube et Trivy Scan pour le projet *simple-banking2*.

Veuillez trouver ci-joint les rapports PDF.

-- Votre pipeline Jenkins 🚀
""",
                    to: "manelsliti184@gmail.com",
                    attachmentsPattern: "${REPORT_DIR}/sonarqube_report.pdf,${REPORT_DIR}/trivy_report.json"
                )
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "${REPORT_DIR}/*", fingerprint: true
            echo "✅ Pipeline terminé. Rapports (Trivy + SonarQube PDF) disponibles."
        }
    }
}
