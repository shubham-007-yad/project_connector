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

        stage('Deploy') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'nexus-db-user',
                        variable: 'POSTGRES_USER'
                    ),
                    string(
                        credentialsId: 'nexus-db-password',
                        variable: 'POSTGRES_PASSWORD'
                    ),
                    string(
                        credentialsId: 'nexus-db-name',
                        variable: 'POSTGRES_DB'
                    ),
                    string(
                        credentialsId: 'nexus-db-port',
                        variable: 'POSTGRES_PORT'
                    )
                ]) {
                    sh '''
                        set -eu

                        export BACKEND_IMAGE="nexus-backend:${BUILD_NUMBER}"

                        docker compose \
                            --project-name backend \
                            -f backend/docker-compose.yml \
                            up -d --no-deps --no-build backend

                        echo "Waiting for backend health check..."

                        for i in $(seq 1 30); do
                            if curl -fsS http://localhost:8000/health; then
                                echo "Backend is healthy!"
                                exit 0
                            fi

                            sleep 2
                        done

                        echo "Backend health check failed."
                        exit 1
                    '''
                }
            }
        }
    }
}