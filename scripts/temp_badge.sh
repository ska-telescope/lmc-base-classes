cp ci-metrics.json build/reports
mkdir -p build/badges
apt-get -y update
apt-get install -y python3-pip
pip3 install -U anybadge
curl https://gitlab.com/ska-telescope/ci-metrics-utilities/raw/master/scripts/create_badges.py | python3
find build/badges -type f -exec curl --user $RAW_USER:$RAW_PASS --upload-file {} $RAW_HOST/repository/raw/gitlab-ci-metrics/$CI_PROJECT_PATH/$CI_COMMIT_REF_NAME/badges/ \;
find build/reports -type f -exec curl --user $RAW_USER:$RAW_PASS --upload-file {} $RAW_HOST/repository/raw/gitlab-ci-metrics/$CI_PROJECT_PATH/$CI_COMMIT_REF_NAME/reports/ \;