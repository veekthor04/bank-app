# bank-app

This an app that will be used for banks. Banks have accounts. Accounts hold 
money. Transfers can be made between accounts. Banks store the history of transfers.

## Endpoints

### Bank

#### Bank List

This returns a list of all available banks.

#### Bank Account List

`GET /bank​/`

This returns a list of all accounts in a bank.

#### Bank Account List

`GET ​/bank​/{bank_id}​/account​/`

This returns a list of all accounts in a bank.

#### Intra-Bank Transfer

`PUT ​/transfer​/`

This transfers money from one account to another within the same bank.

#### List Transfer

`GET ​/{account_id}​/list​/`

This returns a list of transfers link to an account.

#### Add Fund

`PUT /{account_id}/add/`

This adds fund to an account.

#### Remove Fund

`PUT /{account_id}/retire/`

This removes fund from an account.

### Authentication

#### Signup

`POST ​/signup​/`

This creates new user

#### Login

`POST ​/login/`

This logs in a user

#### Profile (Get)

`GET ​/profile​/`

This gets the logged in user's profile details.

#### Profile (Put)

`PUT ​/profile​/`

This completely updates the logged in user's details.

#### Profile (Patch)

`PATCH ​/profile​/`

This partially updates the logged in user's details.

## Running

Create a .env file using the .env.sample file as a template

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

The app will be accessed at `localhost:8000`.

## API Documentation

Postman at `https://www.getpostman.com/collections/c3af285bf05a1eb86fb7`

ReDoc at `localhost:8000/redoc/`

Swagger-ui at  `localhost:8000/swagger/`