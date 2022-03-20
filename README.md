# bank-app

This an app that will be used for banks. Banks have accounts. Accounts hold 
money. Transfers can be made between accounts. Banks store the history of transfers.

#### Running

To run the app you can use docker-compose:

```
docker-compose up --build -d
```

To stop the app:

```
docker-compose down
```

To run tests:

```
docker-compose run --rm app sh -c "python manage.py test"
```

The app will be accessed at `0.0.0.0:8000`.

## API Documentation

Postman at `https://www.getpostman.com/collections/c3af285bf05a1eb86fb7`

ReDoc at `0.0.0.0:8000/redoc/`

Swagger-ui at  `0.0.0.0:8000/swagger/`