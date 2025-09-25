pipeline {
    agent any

    environment {
        VENV_DIR      = "${WORKSPACE}/venv"
        PYTHONPATH    = "${WORKSPACE}/src"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT   = "test"
        SONARQUBE     = 'sonarqube'   // Nom configuré dans Jenkins → Manage Jenkins → System
        DATABASE_URL  = "postgresql://user:password@192.168.189.135:5432/mydb"
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
                    echo ">>> Running Trivy Scan (pipeline ne sera PAS bloqué)"
                    trivy image --format table --output ${REPORT_DIR}/trivy_report.txt ${DOCKER_IMAGE} || true
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

        stage('Send SonarQube Report by Email') {
            steps {
                withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                    sh """
                        mkdir -p ${REPORT_DIR}
                        # Fetch SonarQube analysis result using the task API for the specific task ID
                        curl -s -u $SONAR_TOKEN: \
                          "http://192.168.189.138:9000/api/ce/task?id=your-task-id" \
                          -o ${REPORT_DIR}/sonarqube_report.html
                    """
                }

                emailext(
                    subject: "📊 Rapport SonarQube - simple-banking2",
                    body: """Bonjour Manel,

Veuillez trouver ci-joint le rapport HTML généré par SonarQube pour le projet simple-banking2.

-- Votre pipeline Jenkins DevSecOps 🚀
""",
                    to: "manelsliti184@gmail.com",
                    attachmentsPattern: "${REPORT_DIR}/sonarqube_report.html"
                )
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: "${REPORT_DIR}/*", fingerprint: true
            echo "✅ Pipeline terminé. Rapports (Trivy + SonarQube HTML) disponibles."
        }
    }
}
