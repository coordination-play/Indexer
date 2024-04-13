# Deno Indexer
## Build

### Requirements
- Apibara
- Deno runtime env
- Docker

##### Terminal 1
- `export AUTH_TOKEN=dna_xxxxxxxxxxxx`
- `export MONGO_CONNECTION_STRING='mongodb://mongo:mongo@localhost:27017'`
- `docker compose up`

##### Terminal 2
- `apibara run starknet_to_mongo.js`

##### Browser
- http://localhost:8081/db/example/transfers