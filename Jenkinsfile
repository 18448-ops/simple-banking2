pipeline {
    agent any

    environment {
        VENV_DIR = "${WORKSPACE}/venv"
        PYTHONPATH = "${WORKSPACE}/src"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT = "test" // test = SQLite, dev/prod = PostgreSQL
        SONARQUBE_URL = 'http://192.168.189.138:9000'
    }

    stages {

        // Stage 1: Checkout source code from GitHub
        stage('Checkout SCM') {
            steps {
                echo "📥 Cloning the source code..."
                checkout scm
            }
        }

        // Stage 2: Build environment and install dependencies
        stage('Build') {
            steps {
                echo "⚙️ Creating virtual environment and installing dependencies..."
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
                echo "🧪 Running tests..."
                sh """
                    . ${VENV_DIR}/bin/activate
                    if [ "$ENVIRONMENT" = "test" ]; then
                        export DATABASE_URL="sqlite:///./test_banking.db"
                    else
                        export DATABASE_URL="${DATABASE_URL}"
                    fi
                    export PYTHONPATH="$PYTHONPATH"
                    pytest --maxfail=1 --disable-warnings -q
                """
            }
        }

        // Stage 4: SonarQube Static Analysis
        stage('SonarQube Analysis') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "🔎 Running SAST analysis with SonarQube..."
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
                echo "🐳 Building Docker image..."
                sh """
                    docker build -t simple-banking-api .
                """
            }
        }

        // Stage 6: Push Docker Image to DockerHub
        stage('Push Docker Image') {
            steps {
                echo "📦 Pushing Docker image to DockerHub..."
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh """
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker tag simple-banking-api maneldev131/simple-banking-api:latest
                        docker push maneldev131/simple-banking-api:latest
                    """
                }
            }
        }

        // Stage 7: Verify Docker Permissions
        stage('Verify Docker') {
            steps {
                echo "🔍 Verifying Docker permissions..."
                sh 'docker info'
            }
        }

        // Stage 8: Run Docker Container
        stage('Run Docker Container') {
            steps {
                echo "🚀 Running Docker container..."
                sh """
                    docker stop simple-banking-api || true
                    docker rm simple-banking-api || true
                    docker run -d --name simple-banking-api -p 8000:8000 maneldev131/simple-banking-api:latest
                """
            }
        }
    }

    post {
        always {
            echo "🧹 Cleaning up..."
        }
        success {
            echo "✅ Pipeline succeeded"
        }
        failure {
            echo "❌ Pipeline failed"
        }
    }
}
