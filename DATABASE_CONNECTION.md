# 데이터베이스 연결 정보

## 포트 정보

| 포트      | 의미         | 호스트               | 데이터베이스/스키마 | 사용자   | 비밀번호      |
| ------- | ---------- | ----------------- | ------------ | ----- | --------- |
| `30570` | MySQL      | 192.168.109.254   | datafabric   | fabric | fabric12*$ |
| `5432`  | PostgreSQL | 192.168.106.12    | fabric (public) | postgres | fabric12*$ |
| `9000`  | MinIO      | 192.168.106.12    | 2024-fabric (Bucket) | fabric | fabric12## |
| `30475` | MariaDB    | 192.168.109.254   | datafabric   | fabric | fabric12#$ |

## 연결 방법

### 1. MySQL (포트 30570)

```bash
mysql -h 192.168.109.254 -P 30570 -u fabric -p datafabric
# 비밀번호: fabric12*$
```

Python:
```python
import mysql.connector

conn = mysql.connector.connect(
    host='192.168.109.254',
    port=30570,
    user='fabric',
    password='fabric12*$',
    database='datafabric'
)
```

### 2. PostgreSQL (포트 5432)

```bash
psql -h 192.168.106.12 -p 5432 -U postgres -d fabric
# 비밀번호: fabric12*$
```

Python:
```python
import psycopg2

conn = psycopg2.connect(
    host='192.168.106.12',
    port=5432,
    user='postgres',
    password='fabric12*$',
    database='fabric'
)
```

### 3. MinIO (포트 9000)

웹 브라우저:
```
http://192.168.106.12:9000
ID: fabric
비밀번호: fabric12##
```

MinIO Client:
```bash
mc alias set myminio http://192.168.106.12:9000 fabric 'fabric12##'
mc ls myminio/2024-fabric
```

Python:
```python
from minio import Minio

client = Minio(
    '192.168.106.12:9000',
    access_key='fabric',
    secret_key='fabric12##',
    secure=False
)
```

### 4. MariaDB (포트 30475)

```bash
mysql -h 192.168.109.254 -P 30475 -u fabric -p datafabric
# 비밀번호: fabric12#$
```

Python:
```python
import pymysql

conn = pymysql.connect(
    host='192.168.109.254',
    port=30475,
    user='fabric',
    password='fabric12#$',
    database='datafabric'
)
```

## 연결 테스트

포트 연결 확인:
```bash
# MySQL
nc -zv 192.168.109.254 30570

# PostgreSQL
nc -zv 192.168.106.12 5432

# MinIO
nc -zv 192.168.106.12 9000

# MariaDB
nc -zv 192.168.109.254 30475
```

Python 스크립트로 전체 테스트:
```bash
python test_db_connections.py
```

## 주의사항

- VPN 연결이 필요합니다
- SSH 서버에서 접속해야 합니다
- 방화벽 규칙 확인이 필요할 수 있습니다

