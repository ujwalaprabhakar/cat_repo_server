@Library('utils')
import static main.utils.Utilities.*

def APP_NAMES = ['ujcatapi', 'ujcatapi-consumer']
pipeline {
    agent any
    environment {
        REPO = 'ujcatapi'
        GIT_COMMIT = sh (
            script: 'git rev-parse HEAD',
            returnStdout: true
        ).trim()
        SLACK_CHANNEL = "#jenkins_pipelines"
    }
    stages {
        stage('Start') {
            steps {
                slackSend([
                    channel: "${env.SLACK_CHANNEL}",
                    color: "good",
                    message: "<${env.BUILD_URL}|${currentBuild.fullDisplayName}> started with <https://github.com/lionbridgeai/${env.REPO}/commit/${env.GIT_COMMIT}|${env.GIT_COMMIT}>"
                ])
            }
        }
        stage('Build') {
            when { not { buildingTag() } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'deployer-github-token', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_TOKEN')]) {
                    sh "docker build -t ${APP_NAMES[0]} -t ${APP_NAMES[1]} -f Dockerfile --build-arg DEV=no --build-arg GITHUB_TOKEN=${GITHUB_TOKEN} ."
                }
            }
            post {
                failure {
                    slackSend([
                        channel: "${env.SLACK_CHANNEL}",
                        color: "danger",
                        message: "<${env.BUILD_URL}|${currentBuild.fullDisplayName}> failed on Build"
                    ])
                }
            }
        }
        stage('Push') {
            when { not { buildingTag() } }
            steps {
                script {
                    getPushStage(this, APP_NAMES[0]).call()
                    getPushStage(this, APP_NAMES[1]).call()
                }
            }
        }
        stage('Deploy') {
            steps {
                script {
                    environments = getEnvironmentsFromJobName(currentBuild.projectName, ["staging-saas"])
                    parallel getDeployStages(this, environments, APP_NAMES)
                }
            }
        }
        stage('Finish') {
            steps {
                slackSend([
                    channel: "${env.SLACK_CHANNEL}",
                    color: "good",
                    message: "<${env.BUILD_URL}|${currentBuild.fullDisplayName}> finished successfully"
                ])
            }
        }
    }
}