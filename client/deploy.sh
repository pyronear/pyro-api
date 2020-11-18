#!/bin/bash 
set -e


read -p "API url [http://localhost:8002]: " API_URL
API_URL=${API_URL:-http://localhost:8002}
echo $API_URL
read -p "Login (device Name): [superuser]" login
login=${login:-superuser}
read -p "password: [superuser]" password
password=${password:-superuser}



query=$(curl -X POST "${API_URL}/login/access-token" \
            -H  "accept: application/json" \
            -H  "Content-Type: application/x-www-form-urlencoded"  \
            -d "grant_type=&username=${login}&password=${password}&scope=&client_id=&client_secret=")

ACCESS_TOKEN=$(echo $query | jq -r '.access_token')

# Check docker installation:
if [ ${ACCESS_TOKEN} == "null" ]; then
    echo "Could not retrieve a token. Check the API url and your login credentials."
    exit 1
fi




# Check docker installation:
if [ -x "$(command -v docker)" ]; then
    echo "Docker is updated"
    # command
else
    echo "Install docker"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ${USER}
    sudo su - ${USER}

    sudo apt-get install libffi-dev libssl-dev
    sudo apt install python3-dev
    sudo apt-get install -y python3 python3-pip
    sudo pip3 install docker-compose
fi



ACCESS_TOKEN=$ACCESS_TOKEN API_URL=$API_URL docker-compose up -d --build
