docker-compose -f docker-compose.build.yml config > docker-compose.build.effective.yml
docker-compose -f docker-compose.build.effective.yml build
docker-compose -f docker-compose.build.effective.yml push
