pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                echo 'Building application...'
            }
        }
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh 'pytest --maxfail=1 --disable-warnings -q'
            }
        }
    }
    post {
        always {
            echo 'Pipeline finished (main branch)'
        }
    }
}
