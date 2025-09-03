pipeline {
    agent any

    environment {
        VENV_DIR      = "${WORKSPACE}/venv"
        PYTHONPATH    = "${WORKSPACE}/src"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT   = "test"
        SONARQUBE     = 'sonarqube'
        DATABASE_URL  = "postgresql://user:password@192.168.189.138:5432/mydb"
        DOCKER_IMAGE  = "maneldev131/simple-banking-api:latest"
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
                sh "docker build -t simple-banking-api ."
            }
        }

        stage('Trivy Scan') {
            steps {
                sh """
                    if ! command -v trivy >/dev/null 2>&1; then
                        echo "Installing Trivy..."
                        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
                        sudo mv trivy /usr/local/bin/
                    fi
                    echo "Running Trivy scan..."
                    trivy image --exit-code 0 --severity MEDIUM,HIGH simple-banking-api > trivy-report.txt
                    trivy image --exit-code 1 --severity CRITICAL simple-banking-api >> trivy-report.txt
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-report.txt', fingerprint: true
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker tag simple-banking-api ${DOCKER_IMAGE}
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
    }
}
