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
        sh '''
            python3 -m venv venv
            . venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
            pytest --maxfail=1 --disable-warnings -q
        '''
    }
}

