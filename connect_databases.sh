#!/bin/bash
# 데이터베이스 연결 스크립트
# VPN 연결 후 사용하세요

echo "=== 데이터베이스 연결 테스트 ==="
echo ""

# 1. MySQL 연결 테스트
echo "1. MySQL 연결 테스트 (192.168.109.254:30570)"
echo "   명령어: mysql -h 192.168.109.254 -P 30570 -u fabric -p datafabric"
echo "   비밀번호: fabric12*$"
echo ""
echo "   또는 Python으로:"
echo "   mysql -h 192.168.109.254 -P 30570 -u fabric -p'fabric12*$' datafabric -e 'SELECT 1;'"
echo ""

# 2. PostgreSQL 연결 테스트
echo "2. PostgreSQL 연결 테스트 (192.168.106.12:5432)"
echo "   명령어: psql -h 192.168.106.12 -p 5432 -U postgres -d fabric"
echo "   비밀번호: fabric12*$"
echo ""
echo "   또는:"
echo "   PGPASSWORD='fabric12*$' psql -h 192.168.106.12 -p 5432 -U postgres -d fabric -c 'SELECT 1;'"
echo ""

# 3. MinIO 연결 테스트
echo "3. MinIO 연결 정보 (192.168.106.12:9000)"
echo "   웹 브라우저: http://192.168.106.12:9000"
echo "   ID: fabric"
echo "   비밀번호: fabric12##"
echo "   Bucket: 2024-fabric"
echo ""
echo "   또는 mc (MinIO Client) 사용:"
echo "   mc alias set myminio http://192.168.106.12:9000 fabric 'fabric12##'"
echo "   mc ls myminio/2024-fabric"
echo ""

# 4. MariaDB 연결 테스트
echo "4. MariaDB 연결 테스트 (192.168.109.254:30475)"
echo "   명령어: mysql -h 192.168.109.254 -P 30475 -u fabric -p datafabric"
echo "   비밀번호: fabric12#$"
echo ""
echo "   또는:"
echo "   mysql -h 192.168.109.254 -P 30475 -u fabric -p'fabric12#$' datafabric -e 'SELECT 1;'"
echo ""

# 네트워크 연결 확인
echo "=== 네트워크 연결 확인 ==="
echo "MySQL/MariaDB 서버 (192.168.109.254):"
nc -zv 192.168.109.254 30570 2>&1 || echo "  MySQL 포트 연결 실패"
nc -zv 192.168.109.254 30475 2>&1 || echo "  MariaDB 포트 연결 실패"
echo ""
echo "PostgreSQL/MinIO 서버 (192.168.106.12):"
nc -zv 192.168.106.12 5432 2>&1 || echo "  PostgreSQL 포트 연결 실패"
nc -zv 192.168.106.12 9000 2>&1 || echo "  MinIO 포트 연결 실패"
echo ""

echo "=== Python 연결 예제 ==="
echo "Python으로 연결하려면 필요한 패키지:"
echo "  pip install mysql-connector-python psycopg2-binary minio pymysql"
echo ""

