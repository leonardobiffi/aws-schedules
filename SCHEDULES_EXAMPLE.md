# Schedules Example

## EC2

EC2 accept json or list format

- Monday - Friday

> JSON Format
```json
{"workday": {"start": 8, "stop": 22}}
```

> List Format
```text
workday_start=8 workday_stop=22
```

## RDS

RDS only list format is accepted

- Thursday

> List Format
```text
thu_start=7 thu_stop=19
```

## ECS

ECS format in list

> List Format
```text
daily_start=8 daily_stop=20 daily_stop-desired=0
```