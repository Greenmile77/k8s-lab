#!/usr/bin/env python3
import os
import psycopg2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def load_data():
    try:
        host = os.getenv('POSTGRES_HOST', 'postgres-service')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'portfolio_db')
        user = os.getenv('POSTGRES_USER', 'portfolio_user')
        password = os.getenv('POSTGRES_PASSWORD', 'secure_password_123')
        
        logger.info(f"Connecting to {host}:{port}/{db}")
        
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=db,
            user=user,
            password=password
        )
        cur = conn.cursor()
        
        # Создаем таблицу
        cur.execute("""
            CREATE TABLE IF NOT EXISTS financial_assets (
                id SERIAL PRIMARY KEY,
                asset_name VARCHAR(100),
                date DATE,
                return_value FLOAT,
                volume INTEGER
            )
        """)
        
        # Проверяем и вставляем данные
        cur.execute("SELECT COUNT(*) FROM financial_assets")
        count = cur.fetchone()[0]
        
        if count == 0:
            cur.execute("""
                INSERT INTO financial_assets (asset_name, date, return_value, volume)
                VALUES 
                ('AAPL', '2026-01-01', 0.025, 1000000),
                ('GOOGL', '2026-01-01', 0.018, 800000),
                ('MSFT', '2026-01-01', 0.032, 1500000)
            """)
            conn.commit()
            logger.info("Inserted test data")
        
        cur.execute("SELECT COUNT(*) FROM financial_assets")
        count = cur.fetchone()[0]
        logger.info(f"Total records: {count}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return False

if __name__ == "__main__":
    load_data()
