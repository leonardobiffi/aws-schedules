# Schedule Instances

## Deploy

In order to deploy the lambda to the Client, it is necessary to have awscli configured with the Secret Keys of the Client account.

### Dependencies

Install plugins serverless framework

```bash
export $(grep -v '^#' .env.example | xargs)
serverless plugin install -n serverless-dotenv-plugin
serverless plugin install -n serverless-python-requirements
```

### Configure file .env

Create copy of file .env.example like .env.prod

```bash
cp .env.example .env.prod
```

Change the env for the Client who will Deploy the function if necessary


### Deploy

```bash
serverless deploy --stage prod
```

### Remove

```bash
serverless remove --stage prod
```
