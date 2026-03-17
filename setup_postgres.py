#!/usr/bin/env python
import psycopg2
from psycopg2 import sql

try:
    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="admin",
        port="5432"
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier("memorial_care")
        ))
        print("✓ Database 'memorial_care' created successfully!")
    except psycopg2.errors.DuplicateDatabase:
        print("✓ Database 'memorial_care' already exists")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ Error: {e}")
