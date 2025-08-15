"""Simple wait script to ensure databases are ready before app starts."""
import os
import time
import socket
import psycopg2
import pymysql

POSTGRES_DSN = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "user": os.getenv("POSTGRES_USER", "test_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "test_password"),
    "dbname": os.getenv("POSTGRES_DB", "test_db"),
}
MYSQL_CFG = {
    "host": os.getenv("MYSQL_HOST", "mysql"),
    "port": int(os.getenv("MYSQL_PORT", "3306")),
    "user": os.getenv("MYSQL_USER", "test_user"),
    "password": os.getenv("MYSQL_PASSWORD", "test_password"),
    "database": os.getenv("MYSQL_DATABASE", "test_db"),
}


def wait_for_port(host: str, port: int, timeout: float = 1.0) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
            return True
        except Exception:
            return False


def wait_postgres(max_attempts: int = 30, delay: float = 2.0):
    for attempt in range(1, max_attempts + 1):
        try:
            if wait_for_port(POSTGRES_DSN["host"], POSTGRES_DSN["port"]):
                conn = psycopg2.connect(**POSTGRES_DSN)
                conn.close()
                print(f"Postgres ready (attempt {attempt})")
                return
        except Exception as e:  # noqa: BLE001
            print(f"Postgres not ready yet: {e}")
        time.sleep(delay)
    raise RuntimeError("Postgres not ready in time")


def wait_mysql(max_attempts: int = 30, delay: float = 2.0):
    for attempt in range(1, max_attempts + 1):
        try:
            if wait_for_port(MYSQL_CFG["host"], MYSQL_CFG["port"]):
                conn = pymysql.connect(**MYSQL_CFG)
                conn.close()
                print(f"MySQL ready (attempt {attempt})")
                return
        except Exception as e:  # noqa: BLE001
            print(f"MySQL not ready yet: {e}")
        time.sleep(delay)
    raise RuntimeError("MySQL not ready in time")


def main():
    print("Waiting for databases...")
    wait_postgres()
    wait_mysql()
    print("All databases ready.")


if __name__ == "__main__":  # pragma: no cover
    main()
