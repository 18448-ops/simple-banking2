pipeline {
    agent any

    tools {
        // Ton JDK17 configuré dans Jenkins
        jdk 'jdk17'
    }

    environment {
        SONAR_HOST_URL    = 'http://192.168.189.138:9000'
        SONAR_PROJECT_KEY = 'simple-banking2'
        DOCKER_IMAGE      = "simple-banking2:latest"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/18448-ops/simple-banking2.git',
                    credentialsId: 'fraud-pipeline'
            }
        }

        stage('Build') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    export DATABASE_URL=sqlite:///./test_banking.db
                    pytest --maxfail=1 --disable-warnings -q \
                           --junitxml=pytest-report.xml \
                           --cov=src --cov-report=xml
                '''
            }
            post {
                always {
                    junit 'pytest-report.xml'
                }
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                        sh '''
                            export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
                            export PATH=$JAVA_HOME/bin:$PATH
                            sonar-scanner \
                              -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                              -Dsonar.sources=src \
                              -Dsonar.python.coverage.reportPaths=coverage.xml \
                              -Dsonar.host.url=${SONAR_HOST_URL} \
                              -Dsonar.token=$SONAR_TOKEN
                        '''
                    }
                }
            }
        }

        stage("Quality Gate") {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build -t ${DOCKER_IMAGE} .
                '''
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                    trivy image --exit-code 0 --severity LOW,MEDIUM ${DOCKER_IMAGE}
                    trivy image --exit-code 1 --severity HIGH,CRITICAL ${DOCKER_IMAGE}
                '''
            }
        }

        stage('Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials',
                                                 usernameVariable: 'DOCKER_USERNAME',
                                                 passwordVariable: 'DOCKER_PASSWORD')]) {
                    sh '''
                        echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
                        docker tag ${DOCKER_IMAGE} maneldev131/simple-banking2:latest
                        docker push maneldev131/simple-banking2:latest
                    '''
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                sh '''
                    docker rm -f simple-banking2 || true
                    docker run -d -p 8000:8000 --name simple-banking2 ${DOCKER_IMAGE}
                '''
            }
        }
    }
}
