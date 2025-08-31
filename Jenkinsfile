pipeline {
    agent any

    tools {
        // Scanner configuré dans Manage Jenkins → Global Tool Configuration
        sonarQubeScanner 'sonar-scanner'
    }

    environment {
        VENV_DIR      = "${WORKSPACE}/venv"
        PYTHONPATH    = "${WORKSPACE}/src"
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
        ENVIRONMENT   = "test" // test = SQLite, dev/prod = PostgreSQL
        SONARQUBE     = 'sonarqube'  // doit correspondre au "Name" configuré dans Jenkins > System
        DATABASE_URL  = "postgresql://user:password@localhost:5432/mydb"
    }

    stages {

        stage('Checkout SCM') {
            steps {
                echo "📥 Cloning the source code..."
                checkout scm
            }
        }

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

        stage('Test') {
            steps {
                echo "🧪 Running tests..."
                sh """
                    . ${VENV_DIR}/bin/activate
                    if [ "$ENVIRONMENT" = "test" ]; then
                        export DATABASE_URL="sqlite:///./test_banking.db"
                    fi
                    pytest --maxfail=1 --disable-warnings -q
                """
            }
        }

        stage('SonarQube Analysis') {
            when { expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' } }
            steps {
                echo "🔎 Running SAST analysis with SonarQube..."
                withSonarQubeEnv("${SONARQUBE}") {
                    withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                        sh """
                            sonar-scanner \
                              -Dsonar.projectKey=simple-banking2 \
                              -Dsonar.sources=src \
                              -Dsonar.python.coverage.reportPaths=coverage.xml \
                              -Dsonar.host.url=$SONAR_HOST_URL \
                              -Dsonar.login=$SONAR_TOKEN
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "🐳 Building Docker image..."
                sh "docker build -t simple-banking-api ."
            }
        }

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

        stage('Verify Docker') {
            steps {
                echo "🔍 Verifying Docker permissions..."
                sh 'docker info'
            }
        }

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
