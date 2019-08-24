#!/bin/bash
set +x

if [ -z "$environment" ]; then
    if [ ! -z "$1" ]; then
        environment=$1
    else
        echo "*** set environment as preview ***"
        environment=preview
    fi
fi 

if [ -z $TRAVIS_BUILD_DIR ]; then
    source $environment-environment.sh
    src=.
else 
    src="$TRAVIS_BUILD_DIR"

    if [ $environment = 'live' ]; then
        echo $TRAVIS_KEY_live | base64 --decode > travis_rsa
    else
        echo $TRAVIS_KEY_preview | base64 --decode > travis_rsa
    fi
    eval "$(ssh-agent)"
    chmod 600 travis_rsa
    ssh-add travis_rsa
fi

if [ -z $debug ]; then
    output_params=">&- 2>&- <&- &"
fi

port="$(python $src/app/config.py -e $environment)"
if [ $port != 'No environment' ]; then
    rsync -ravzhe "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" $src/ --exclude-from "$src/.exclude" --quiet $user@$deploy_host:www-$environment/
    eval "DATABASE_URL_ENV=\${DATABASE_URL_$environment}"
    eval "ADMIN_CLIENT_ID=\${ADMIN_CLIENT_ID_$environment}"
    eval "ADMIN_CLIENT_SECRET=\${ADMIN_CLIENT_SECRET_$environment}"
    eval "ADMIN_USERS=\${ADMIN_USERS_$environment}"
    eval "PAYPAL_URL=\${PAYPAL_URL_$environment}"
    eval "PAYPAL_USER=\${PAYPAL_USER_$environment}"
    eval "PAYPAL_PASSWORD=\${PAYPAL_PASSWORD_$environment}"
    eval "PAYPAL_SIG=\${PAYPAL_SIG_$environment}"
    eval "EMAIL_PROVIDER_URL=\${EMAIL_PROVIDER_URL_$environment}"
    eval "EMAIL_PROVIDER_APIKEY=\${EMAIL_PROVIDER_APIKEY_$environment}"
    eval "FRONTEND_ADMIN_URL=\${FRONTEND_ADMIN_URL_$environment}"
    eval "API_BASE_URL=\$API_BASE_URL_$environment"
    eval "FRONTEND_URL=\$FRONTEND_URL_$environment"
    eval "IMAGES_URL=\$IMAGES_URL_$environment"
    eval "CELERY_BROKER_URL=\$CELERY_BROKER_URL_$environment"
    eval "PROJECT=\$PROJECT_$environment"
    eval "GOOGLE_AUTH_USER=\$GOOGLE_AUTH_USER_$environment"
    eval "JWT_SECRET=\$JWT_SECRET_$environment"
    eval "GOOGLE_APPLICATION_CREDENTIALS=\$GOOGLE_APPLICATION_CREDENTIALS_$environment"
    
    echo starting app $environment on port $port
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $user@$deploy_host """
    cd www-$environment
    export ENVIRONMENT=$environment
    export DATABASE_URL_$environment=$DATABASE_URL_ENV
    export ADMIN_CLIENT_ID=$ADMIN_CLIENT_ID
    export ADMIN_CLIENT_SECRET=$ADMIN_CLIENT_SECRET
    export JWT_SECRET=$JWT_SECRET
    export PROJECT=$PROJECT
    export GOOGLE_STORE=$GOOGLE_STORE
    export ADMIN_USERS=$ADMIN_USERS
    export EMAIL_DOMAIN=$EMAIL_DOMAIN
    export PAYPAL_URL=$PAYPAL_URL
    export PAYPAL_USER=$PAYPAL_USER
    export PAYPAL_PASSWORD=$PAYPAL_PASSWORD
    export PAYPAL_SIG=$PAYPAL_SIG
    export EMAIL_PROVIDER_URL=$EMAIL_PROVIDER_URL
    export EMAIL_PROVIDER_APIKEY=$EMAIL_PROVIDER_APIKEY
    export FRONTEND_ADMIN_URL=$FRONTEND_ADMIN_URL
    export API_BASE_URL=$API_BASE_URL
    export FRONTEND_URL=$FRONTEND_URL
    export IMAGES_URL=$IMAGES_URL
    export GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS
    export TRAVIS_COMMIT=$TRAVIS_COMMIT
    export CELERY_BROKER_URL=$CELERY_BROKER_URL

    if [ ! -z $GOOGLE_AUTH_USER ]; then
        gcloud auth activate-service-account $GOOGLE_AUTH_USER --key-file=$GOOGLE_APPLICATION_CREDENTIALS
    fi

    sudo ./scripts/bootstrap.sh
    ./scripts/run_celery.sh
    ./scripts/run_app.sh $environment gunicorn $output_params"""

    ./scripts/check_site.sh $deploy_host:$port
else
    echo "$port"
    exit 1
fi
