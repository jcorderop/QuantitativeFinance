docker stop quantitative-finance-api
docker build . -t jcorderop/quantitative-finance
docker push docker.io/jcorderop/quantitative-finance
docker run --rm --name quantitative-finance-api -p 5000:5000 -d jcorderop/quantitative-finance