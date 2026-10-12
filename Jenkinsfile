pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Run Tests') {
            steps {
                dir('backend') {
                    sh '''
                        python3 -m venv ci-venv
                        ci-venv/bin/pip install -r requirements.txt
                        ci-venv/bin/python -m pytest -v
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('backend') {
                    sh '''
                        docker build -t nexus-backend:${BUILD_NUMBER} .
                    '''
                }
            }
        }
    }
}