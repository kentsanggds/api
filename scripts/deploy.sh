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
    sudo ./scripts/bootstrap.sh
    ./scripts/run_app.sh $environment gunicorn $output_params"""

    eval "API_ENV=\${API_$environment}"
    ./scripts/check_site.sh $API_ENV
else
    echo "$port"
    exit 1
fi
