pipeline {
    agent any

    environment {
        VENV_DIR      = "${WORKSPACE}/venv"
        PYTHONPATH    = "${WORKSPACE}/src"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT   = "test"
        SONARQUBE     = 'sonarqube'
        DATABASE_URL  = "sqlite:///./test_banking.db"
        DOCKER_IMAGE  = "maneldev131/simple-banking2:latest"
    }

    tools {
        jdk 'jdk17'
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
                    trivy image --exit-code 0 --severity LOW,MEDIUM ${DOCKER_IMAGE}
                    trivy image --exit-code 1 --severity HIGH,CRITICAL ${DOCKER_IMAGE}
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
                    docker rm -f simple-banking2 || true
                    docker run -d -p 8000:8000 --name simple-banking2 ${DOCKER_IMAGE}
                """
            }
        }
    }
}
