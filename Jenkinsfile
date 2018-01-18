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
                            // Add a symbolic link to levpro dir, as the Ansible scripts
                            // assume that is part of the path
                            sh 'ln -sv $WORKSPACE ../levpro'

                            // use Ansible to do pip installs, using current WORKSPACE
                            // as the software_root
                            // install coverage manually, so it can be used after tests
                            sh '''
                                PARENT_DIR=`dirname $WORKSPACE`
                                cd ansible
                                ansible-playbook -i hosts install_sw.yml \
                                  --limit "local" \
                                  --tags install-sw-levpro \
                                  --tags install-sw-skabase \
                                  --verbose \
                                  --extra-vars software_root=$PARENT_DIR
                                pip install coverage
                                cd ..
                            '''

                            // run tests, and generate HTML coverage report
                            sh '''
                                python setup.py test \
                                  --addopts="--junitxml results.xml --color=yes --cov=skabase --cov=refelt --cov-report=term --cov-config .coveragerc"
                                coverage html
                            '''
                        }
                        finally {
                            step([$class: 'JUnitResultArchiver', testResults: 'results.xml'])
                            archive 'htmlcov/*'
                        }
                    }
                }
            }
    }
}
