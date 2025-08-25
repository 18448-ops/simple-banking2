pipeline {
    agent any

    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        PYTHONPATH = "${WORKSPACE}/src"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT = "test" // test for SQLite, dev/prod for PostgreSQL
        DATABASE_URL = "${env.ENVIRONMENT == 'test' ? 'sqlite:///./test_banking.db' : (env.DATABASE_URL ?: 'postgresql://user:password@192.168.189.135/mydb')}"
        SONARQUBE_URL = 'http://192.168.189.138:9000'  // URL of your SonarQube
        SONARQUBE_TOKEN = credentials('sonarqube-token')  // Use the SonarQube token stored in Jenkins
    }

    stages {

        // Stage 1: Checkout source code from GitHub
        stage('Checkout SCM') {
            steps {
                echo "Cloning the source code..."
                checkout scm
            }
        }

        // Stage 2: Build environment and install dependencies
        stage('Build') {
            steps {
                echo "Creating virtual environment and installing dependencies..."
                sh """
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        // Stage 3: Run tests
        stage('Test') {
            steps {
                echo "Running tests..."
                sh """
                    . ${VENV_DIR}/bin/activate
                    export DATABASE_URL="$DATABASE_URL"
                    export PYTHONPATH="$PYTHONPATH"
                    pytest --maxfail=1 --disable-warnings -q
                """
            }
        }

        // Stage 4: SonarQube Static Analysis
        stage('SonarQube Analysis') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "Running SAST analysis with SonarQube..."
                withSonarQubeEnv('SonarQube') {
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

        // Stage 5: Build Docker Image
        stage('Build Docker Image') {
            steps {
                echo "Building Docker image..."
                sh """
                    docker build -t simple-banking-api .
                """
            }
        }

        // Stage 6: Verify Docker Permissions
        stage('Verify Docker') {
            steps {
                echo "Verifying Docker permissions..."
                sh 'docker info'
            }
        }

        // Stage 7: Run Docker Container
        stage('Run Docker Container') {
            steps {
                echo "Running Docker container..."
                sh """
                    docker stop simple-banking-api || true
                    docker rm simple-banking-api || true
                    docker run -d --name simple-banking-api -p 8000:8000 simple-banking-api
                """
            }
        }
    }

    post {
        always {
            echo "Cleaning up and stopping containers..."
            sh '''
                docker stop simple-banking-api || true
                docker rm simple-banking-api || true
            '''
        }
        success {
            echo "✅ Pipeline succeeded"
        }
        failure {
            echo "❌ Pipeline failed"
        }
    }
}
