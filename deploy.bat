docker stop QuantitativeFinance-API
docker build . -t jcorderop/QuantitativeFinance
docker push docker.io/jcorderop/QuantitativeFinance
docker run --rm --name exchange-api -p 5000:5000 -d jcorderop/QuantitativeFinance