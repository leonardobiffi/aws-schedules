# Schedule Instances

This lambda is Stop and Start RDS, EC2, ASG and ECS services based in TAG defined

## Run Manual

Execute lambda with event in format as shown below

| var   | value                                           |
|-------|-------------------------------------------------|
| hh    | hour that is in the resource tag start or stop  |

### EC2

```json
{"ec2": {"hour": "10", "day": "fri"}}
```

### RDS

```json
{"rds": {"hour": "8", "day": "mon"}}
```

### ECS

```json
{"ecs": {"hour": "5", "day": "fri"}}
```

## Schedules Example

## EC2

EC2 accept json or list format

- Monday to Friday

> JSON Format
```json
{"workday": {"start": 8, "stop": 22}}
```

> List Format
```text
workday_start=8 workday_stop=22
```

## ASG

AutoScaling Groups accept json or list format

- Monday to Friday

> JSON Format
```json
{"workday": {"start": 8, "stop": 22}}
```

> List Format
```text
workday_start=8 workday_stop=22
```

### RDS

RDS only list format is accepted

- Thursday

> List Format
```text
thu_start=7 thu_stop=19
```

### ECS

ECS only list format is accepted

> List Format
```text
daily_start=8 daily_stop=20 daily_stop-desired=1
```

If desired is 0, then daily_stop-desired can be removed

```text
daily_start=8 daily_stop=20
```

## Deploy

In order to deploy the lambda to the Client, it is necessary to have awscli configured with the Secret Keys of the Client account.

### Configure file .env

Create copy of file .env.example like .env.prod

```bash
cp .env.example .env.prod
```

Change the env for the Client who will Deploy the function if necessary

### Dependencies

Install plugins serverless framework

```bash
serverless plugin install -n serverless-python-requirements 
serverless plugin install -n serverless-dotenv-plugin
serverless plugin install -n serverless-plugin-resource-tagging
```

### Deploy

```bash
serverless deploy --stage prod
```

### Remove

```bash
serverless remove --stage prod
```
