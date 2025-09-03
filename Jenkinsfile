pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "simple-banking-api"
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout scm
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
                        sonar-scanner \
                          -Dsonar.projectKey=simple-banking2 \
                          -Dsonar.sources=src \
                          -Dsonar.python.coverage.reportPaths=coverage.xml \
                          -Dsonar.host.url=http://192.168.189.138:9000 \
                          -Dsonar.token=$SONAR_TOKEN
                        '''
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
                sh 'docker build -t $DOCKER_IMAGE .'
            }
        }

        stage('Trivy Scan') {
            steps {
                sh '''
                echo "Installing Trivy..."
                curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh
                chmod +x ./bin/trivy
                sudo mv ./bin/trivy /usr/local/bin/trivy || mv ./bin/trivy ~/bin/trivy

                echo "Running Trivy scan..."
                trivy --version
                trivy image --exit-code 0 --severity MEDIUM,HIGH $DOCKER_IMAGE
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: '**/trivy-report*', allowEmptyArchive: true
                }
            }
        }

        stage('Push Docker Image') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                sh 'docker tag $DOCKER_IMAGE your-dockerhub-user/$DOCKER_IMAGE:latest'
                sh 'docker push your-dockerhub-user/$DOCKER_IMAGE:latest'
            }
        }

        stage('Run Docker Container') {
            steps {
                sh 'docker run -d -p 8000:8000 $DOCKER_IMAGE'
            }
        }
    }
}
