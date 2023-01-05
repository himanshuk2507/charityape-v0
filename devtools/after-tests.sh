container_name=skraggle-backend
container_id=$(docker ps -aqf "name=$container_name")
docker logs --follow $container_id