node {

    load "$JENKINS_HOME/.envvars"
    def application_name= "download-minio"
    
        stage('Checkout') {
            git branch: 'main',
            url: 'https://github.com/lapig-ufg/download-minio.git'
        }
        stage('Validate') {
            sh 'git pull origin main'

        }
        stage('SonarQube analysis') {

        def scannerHome = tool 'sonarqube-scanner';
                    withSonarQubeEnv("sonarqube") {
                    sh "${tool("sonarqube-scanner")}/bin/sonar-scanner \
                    -Dsonar.projectKey=download-minio \
                    -Dsonar.sources=. \
                    -Dsonar.css.node=. \
                    -Dsonar.host.url=$SonarUrl \
                    -Dsonar.login=$SonarKeyProject"
                    }
        }
        stage('Building Image') {
            dockerImage = docker.build registryPROD + "/$application_name:$BUILD_NUMBER", "--build-arg  --no-cache -f Dockerfile ."
        }
        stage('Push Image to Registry') {

            docker.withRegistry( "$Url_Private_Registry", "$registryCredential" ) {
            dockerImage.push("${env.BUILD_NUMBER}")
            dockerImage.push("latest")

                }   

            }
        stage('Removing image Locally') {
            sh "docker rmi $registryPROD/$application_name:$BUILD_NUMBER"
            sh "docker rmi $registryPROD/$application_name:latest"
        }

        stage ('Pull imagem on PROD') {
        sshagent(credentials : ['KEY_FULL']) {
            sh "$SERVER_PROD_SSH 'docker pull $registryPROD/$application_name:latest'"
                }
            
        }

        stage('Deploy container on PROD') {

                        configFileProvider([configFile(fileId: "$File_Json_Id_APP_LAPIG_DOWNLOAD_MINIO_SERVER_PROD", targetLocation: 'container-lapig-download-minio-deploy-prod.json')]) {

                            def url = "http://$SERVER_PROD/containers/$application_name?force=true"
                            def response = sh(script: "curl -v -X DELETE $url", returnStdout: true).trim()
                            echo response

                            url = "http://$SERVER_PROD/containers/create?name=$application_name"
                            response = sh(script: "curl -v -X POST -H 'Content-Type: application/json' -d @container-lapig-download-minio-deploy-prod.json -s $url", returnStdout: true).trim()
                            echo response
                        }

            }            
        stage('Start container on PROD') {

                        final String url = "http://$SERVER_PROD/containers/$application_name/start"
                        final String response = sh(script: "curl -v -X POST -s $url", returnStdout: true).trim()
                        echo response                    


            }                      
        stage('Send message to Telegram') {

                            def Author_Name=sh(script: "git show -s --pretty=%an", returnStdout: true).trim()
                            def Author_Email=sh(script: "git show -s --pretty=%ae", returnStdout: true).trim()
                            def Author_Data=sh(script: "git log -1 --format=%cd --date=local",returnStdout: true).trim()
                            def Project_Name=sh(script: "git config --local remote.origin.url",returnStdout: true).trim()
                            def Last_Commit=sh(script: "git show --summary | grep 'commit' | awk '{print \$2}'",returnStdout: true).trim()
                            def Comment_Commit=sh(script: "git log -1 --pretty=%B",returnStdout: true).trim()
                            def Date_Commit=sh(script: "git show -s --format=%ci",returnStdout: true).trim()  
                            def Branch_Name=sh(script: "git rev-parse --abbrev-ref HEAD",returnStdout: true).trim()

                            withCredentials([string(credentialsId: 'telegramToken', variable: 'TOKEN'), string(credentialsId: 'telegramChatId', variable: 'CHAT_ID')]) {
                                sh  ("""
                                    curl -s -X POST https://api.telegram.org/bot${TOKEN}/sendMessage -d chat_id=${CHAT_ID} -d parse_mode=markdown -d text='*Project*: *${Project_Name}* \n *Branch*: ${Branch_Name} \n *Author*: *${Author_Name}* \n *Author_Email*: *${Author_Email}* \n *Commit_ID*: *${Last_Commit}* \n *Message_Commit*: *${Comment_Commit}* \n *Date_Commit*: *${Date_Commit}* \n *Duration*: *${currentBuild.durationString}*'
                                """)
                            }
        }
        stage('Send message to Discord') {

                        //SEND DISCORD NOTIFICATION
                        def discordImageSuccess = 'https://www.jenkins.io/images/logos/formal/256.png'
                        def discordImageError = 'https://www.jenkins.io/images/logos/fire/256.png'
                        
                        def Author_Name=sh(script: "git show -s --pretty=%an", returnStdout: true).trim()
                        def Author_Email=sh(script: "git show -s --pretty=%ae", returnStdout: true).trim()
                        def Author_Data=sh(script: "git log -1 --format=%cd --date=local",returnStdout: true).trim()
                        def Project_Name=sh(script: "git config --local remote.origin.url",returnStdout: true).trim()
                        def Last_Commit=sh(script: "git show --summary | grep 'commit' | awk '{print \$2}'",returnStdout: true).trim()
                        def Comment_Commit=sh(script: "git log -1 --pretty=%B",returnStdout: true).trim()
                        def Date_Commit=sh(script: "git show -s --format=%ci",returnStdout: true).trim()

                        def discordDesc =
                                "Result: ${currentBuild.currentResult}\n" +
                                        "Project: $Project_Name\n" +
                                        "Commit: $Last_Commit\n" +
                                        "Author: $Author_Name\n" +
                                        "Author_Email: $Author_Email\n" +
                                        "Message: $Comment_Commit\n" +
                                        "Date: $Date_Commit\n" +
                                        "Duration: ${currentBuild.durationString}"

                                        //Variaveis de ambiente do Jenkins - NOME DO JOB E NÚMERO DO JOB
                                        def discordFooter = "${env.JOB_BASE_NAME} (#${BUILD_NUMBER})"
                                        def discordTitle = "${env.JOB_BASE_NAME} (build #${BUILD_NUMBER})"
                                        def urlWebhook = "https://discord.com/api/webhooks/$DiscordKey"

                        discordSend description: discordDesc,
                                footer: discordFooter,
                                link: env.JOB_URL,
                                result: currentBuild.currentResult,
                                title: discordTitle,
                                webhookURL: urlWebhook,
                                successful: currentBuild.resultIsBetterOrEqualTo('SUCCESS'),
                                thumbnail: 'SUCCESS'.equals(currentBuild.currentResult) ? discordImageSuccess : discordImageError              

        } 
}
