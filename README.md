# lindrea

Simple application written in Python to automate capturing data of [realestate.com.au](https://www.realestate.com.au) GraphQL endpoint and stores it in a PostgreSQL database to be able to catch changes to individual property listings to track trends.


## Usage

### Requirements

1. [Docker Compose](https://docs.docker.com/compose/install/)
2. [Docker](https://www.docker.com/)

### Building + Running

1. Rename `app.env.example` to `app.env` and fill out the values.

Example:

```
DB_HOST="localhost"
DB_PORT="5432"
PGADMIN_DEFAULT_PASSWORD="password"
POSTGRES_PASSWORD="password"
POSTGRES_USER="postgres"
POSTGRES_DB="lindrea"
```

2. Rename `pgadmin.env.example` to `pgadmin.env` and fill the values in if you wish to browse the data stored easily.

```
PGADMIN_DEFAULT_PASSWORD="password"
PGADMIN_DEFAULT_EMAIL="user@user.com"
```

3. Update `app.py` search parameters to what values you want.

```python
realestate_com_au_listings = api.search(
    locations=[
        "Chelsea Heights, 3196",
        "Aspendale Gardens, 3195",
        "Patterson Lakes, 3197"
    ],
    channel="buy",
    surrounding_suburbs=False,
    sortType="new-desc"
)
```



4. Run the below command to build the image + bring up the necessary services.

```shell
$ docker-compose -p lindrea -f docker-compose.yml up --build -d
```

### Query

To query, you need to enter the running container, then run the query application.

```shell
[root@JD-Dev-02 Lindrea]# docker exec -it lindrea-app-1 sh
~ # python query.py 1
"url": "https://www.realestate.com.au/property-unit-vic-patterson+lakes-xxxxx",
"history": [
    {
        "price_text": "$640,000 - $670,000",
        "date": "11PM Sat 21 Jan",
        "original_val": "$700,000 - $770,000"
    },
```
