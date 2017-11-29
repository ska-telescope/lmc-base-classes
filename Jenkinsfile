node('docker') {

    withDockerContainer(
        image: 'tango-levpro:latest',
        args: '-u root'
    ) {
        stage 'Cleanup workspace'
        sh 'chmod 777 -R .'
        sh 'rm -rf *'

        stage 'Checkout SCM'
            checkout([
                $class: 'GitSCM',
                branches: [[name: "refs/heads/${env.BRANCH_NAME}"]],
                extensions: [[$class: 'LocalBranch']],
                userRemoteConfigs: scm.userRemoteConfigs,
                doGenerateSubmoduleConfigurations: false,
                submoduleCfg: []
            ])

        stage 'Install & Unit Tests'
            timestamps {
                timeout(time: 30, unit: 'MINUTES') {
                    ansiColor('xterm') {
                        try {
                            sh 'export'
                            sh 'mount'
                            sh 'python setup.py test --addopts="--junitxml results.xml"'
                        }
                        finally {
                            step([$class: 'JUnitResultArchiver', testResults: 'results.xml'])
                        }
                    }
                }
            }
    }
}
