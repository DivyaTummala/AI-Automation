
from flask import Flask, render_template, request, jsonify, session
import pyodbc
import pymysql
import psycopg2
from pymongo import MongoClient

app = Flask(__name__)

# --- Place duplicate validation endpoint after app initialization ---
@app.route('/validate-duplicates')
def validate_duplicates():
    source_table = request.args.get('source_table', '')
    target_table = request.args.get('target_table', '')
    key_columns = request.args.get('key_columns', '')  # comma-separated list of columns to check duplicates on
    key_cols = [col.strip() for col in key_columns.split(',') if col.strip()]
    if not key_cols:
        return jsonify({"error": "No key columns specified for duplicate check."}), 400

    def get_duplicates(conn, table, db_type, key_cols):
        cursor = conn.cursor()
        col_str = ', '.join(key_cols)
        # Build query to find duplicates based on key columns
        if db_type in ['SQL Server', 'PostgreSQL', 'MySQL']:
            query = f"SELECT {col_str}, COUNT(*) as dup_count FROM {table} GROUP BY {col_str} HAVING COUNT(*) > 1"
        else:
            return [], 0
        cursor.execute(query)
        rows = cursor.fetchall()
        # Return up to 5 sample duplicate rows
        sample = [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows[:5]]
        total_dups = len(rows)
        cursor.close()
        return sample, total_dups

    # Source duplicates
    source_sample = []
    source_total = 0
    if source_table and source_config:
        try:
            db_type = source_config.get('sourceDbType', '')
            conn = get_database_connection(source_config, is_target=False)
            source_sample, source_total = get_duplicates(conn, source_table, db_type, key_cols)
            conn.close()
        except Exception as e:
            return jsonify({"error": f"Source error: {str(e)}"}), 500

    # Target duplicates
    target_sample = []
    target_total = 0
    if target_table and target_config:
        try:
            db_type = target_config.get('targetDbType', '')
            conn = get_database_connection(target_config, is_target=True)
            target_sample, target_total = get_duplicates(conn, target_table, db_type, key_cols)
            conn.close()
        except Exception as e:
            return jsonify({"error": f"Target error: {str(e)}"}), 500

    return jsonify({
        "source_duplicates": source_sample,
        "source_total": source_total,
        "target_duplicates": target_sample,
        "target_total": target_total,
        "key_columns": key_cols
    })
from flask import Flask, render_template, request, jsonify, session
import pyodbc
import pymysql
import psycopg2
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/validate-null-values')
def validate_null_values():
    source_table = request.args.get('source_table', '')
    target_table = request.args.get('target_table', '')
    source_nulls = {}
    target_nulls = {}
    columns = []

    # Helper to get NULL counts for each column
    def get_null_counts(conn, table, db_type):
        cursor = conn.cursor()
        null_counts = {}
        col_names = []
        # Get column names
        if db_type == 'SQL Server':
            cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (table.split('.')[-1],))
            col_names = [row[0] for row in cursor.fetchall()]
        elif db_type == 'MySQL':
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            col_names = [row[0] for row in cursor.fetchall()]
        elif db_type == 'PostgreSQL':
            cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s", (table.split('.')[-1],))
            col_names = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute(f"SELECT * FROM {table} LIMIT 0")
            col_names = [desc[0] for desc in cursor.description]
        # For each column, count NULLs
        for col in col_names:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NULL")
                null_counts[col] = cursor.fetchone()[0]
            except Exception:
                null_counts[col] = 'ERR'
        cursor.close()
        return col_names, null_counts

    # Source
    if source_table and source_config:
        try:
            db_type = source_config.get('sourceDbType', '')
            conn = get_database_connection(source_config, is_target=False)
            columns, source_nulls = get_null_counts(conn, source_table, db_type)
            conn.close()
        except Exception as e:
            return jsonify({"error": f"Source error: {str(e)}"}), 500

    # Target
    if target_table and target_config:
        try:
            db_type = target_config.get('targetDbType', '')
            conn = get_database_connection(target_config, is_target=True)
            tgt_columns, target_nulls = get_null_counts(conn, target_table, db_type)
            conn.close()
            # Ensure columns list is union of both
            columns = sorted(set(columns) | set(tgt_columns))
        except Exception as e:
            return jsonify({"error": f"Target error: {str(e)}"}), 500

    # Build result
    results = []
    for col in columns:
        src_val = source_nulls.get(col, '')
        tgt_val = target_nulls.get(col, '')
        match = src_val == tgt_val and src_val != 'ERR' and tgt_val != 'ERR'
        results.append({
            "Column": col,
            "Source NULLs": src_val,
            "Target NULLs": tgt_val,
            "Match": match
        })

    return jsonify({"nulls": results})

from flask import Flask, render_template, request, jsonify, session
import pyodbc
import pymysql
import psycopg2
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Required for session

# Store connection configs in memory (in production, use proper session management)
source_config = {}
target_config = {}

@app.route('/validate-schema')
def validate_schema():
    source_table = request.args.get('source_table', '')
    target_table = request.args.get('target_table', '')
    source_schema = []
    target_schema = []
    mismatches = []

    def get_schema(conn, table, db_type):
        cursor = conn.cursor()
        schema = []
        if db_type == 'SQL Server':
            cursor.execute(f"SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?", (table.split('.')[-1],))
            schema = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
        elif db_type == 'MySQL':
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            schema = [(row[0], row[1], row[2] if len(row) > 2 else None) for row in cursor.fetchall()]
        elif db_type == 'PostgreSQL':
            cursor.execute(f"SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = %s", (table.split('.')[-1],))
            schema = [(row[0], row[1], row[2]) for row in cursor.fetchall()]
        else:
            # fallback: use cursor.description (no length info)
            cursor.execute(f"SELECT * FROM {table} LIMIT 0")
            schema = [(desc[0], str(desc[1]), None) for desc in cursor.description]
        cursor.close()
        return schema

    # Fetch schema from source
    if source_table and source_config:
        try:
            db_type = source_config.get('sourceDbType', '')
            conn = get_database_connection(source_config, is_target=False)
            source_schema = get_schema(conn, source_table, db_type)
            conn.close()
        except Exception as e:
            return jsonify({"error": f"Source error: {str(e)}"}), 500

    # Fetch schema from target
    if target_table and target_config:
        try:
            db_type = target_config.get('targetDbType', '')
            conn = get_database_connection(target_config, is_target=True)
            target_schema = get_schema(conn, target_table, db_type)
            conn.close()
        except Exception as e:
            return jsonify({"error": f"Target error: {str(e)}"}), 500

    # Compare schemas by column name
    source_dict = {col: (dtype, clen) for col, dtype, clen in source_schema}
    target_dict = {col: (dtype, clen) for col, dtype, clen in target_schema}
    all_columns = set(source_dict.keys()) | set(target_dict.keys())
    for col in sorted(all_columns):
        src_type, src_len = source_dict.get(col, (None, None))
        tgt_type, tgt_len = target_dict.get(col, (None, None))
        mismatches.append({
            "Column": col,
            "Source Type": src_type,
            "Source Length": src_len,
            "Target Type": tgt_type,
            "Target Length": tgt_len,
            "Type Match": src_type == tgt_type and src_type is not None,
            "Length Match": src_len == tgt_len and src_len is not None
        })

    return jsonify({
        "schema": mismatches
    })

def get_database_connection(config, is_target=False):
    """Create database connection based on type"""
    db_type_key = 'targetDbType' if is_target else 'sourceDbType'
    host_key = 'targetServerHost' if is_target else 'serverHost'
    db_name_key = 'targetDbName' if is_target else 'dbName'
    port_key = 'targetPort' if is_target else 'port'
    auth_key = 'targetAuthType' if is_target else 'authType'
    user_key = 'targetUsername' if is_target else 'username'
    pass_key = 'targetPassword' if is_target else 'password'
    
    db_type = config.get(db_type_key, '')
    server = config.get(host_key, '').strip()
    database = config.get(db_name_key, '').strip()
    port = config.get(port_key, '').strip()
    auth_type = config.get(auth_key, '')
    username = config.get(user_key, '').strip()
    password = config.get(pass_key, '')
    
    # Detect if this is Azure SQL Database
    is_azure = 'database.windows.net' in server.lower()
    
    try:
        if db_type == 'SQL Server':
            # Build connection string - wrap password in braces to handle special characters
            if is_azure:
                # Azure SQL Database
                conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30'
            else:
                # Regular SQL Server
                if port and ',' not in server:
                    server = f"{server},{port}"
                
                if auth_type == 'Windows Authentication':
                    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
                else:
                    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
            
            print(f"Connecting to SQL Server: {server}, DB: {database}, User: {username}")
            print(f"Connection string (masked): DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD=***")
            
            # Use autocommit for better compatibility
            conn = pyodbc.connect(conn_str, timeout=30, autocommit=True)
            return conn
            
        elif db_type == 'MySQL':
            print(f"Connecting to MySQL: {server}, DB: {database}")
            return pymysql.connect(
                host=server,
                user=username,
                password=password,
                database=database,
                port=int(port) if port else 3306,
                connect_timeout=30
            )
            
        elif db_type == 'PostgreSQL':
            print(f"Connecting to PostgreSQL: {server}, DB: {database}")
            return psycopg2.connect(
                host=server,
                user=username,
                password=password,
                database=database,
                port=int(port) if port else 5432,
                connect_timeout=30
            )
            
        elif db_type == 'MongoDB':
            print(f"Connecting to MongoDB: {server}, DB: {database}")
            return MongoClient(
                host=server,
                port=int(port) if port else 27017,
                username=username,
                password=password,
                serverSelectionTimeoutMS=30000
            )
        else:
            raise Exception(f"Unsupported database type: {db_type}")
            
    except pyodbc.Error as e:
        error_msg = str(e)
        print(f"ODBC Error: {error_msg}")
        if "Cannot open server" in error_msg or "Login failed" in error_msg:
            raise Exception(f"Connection failed. Please verify: 1) Server name is correct, 2) Database name is correct, 3) Username and password are valid, 4) Firewall/network allows connection. Error: {error_msg}")
        else:
            raise Exception(f"Database connection error: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        print(f"Connection Error: {error_msg}")
        raise Exception(f"Connection failed: {error_msg}")

def fetch_tables_from_db(config, is_target=False):
    """Fetch table list from database"""
    db_type_key = 'targetDbType' if is_target else 'sourceDbType'
    db_name_key = 'targetDbName' if is_target else 'dbName'
    
    db_type = config.get(db_type_key, '')
    database = config.get(db_name_key, '')
    tables = []
    conn = None
    cursor = None
    
    try:
        print(f"Fetching tables from {db_type} database: {database}")
        print(f"Connection config: {config}")
        
        if db_type == 'SQL Server':
            conn = get_database_connection(config, is_target)
            cursor = conn.cursor()
            print("Executing query to fetch tables...")
            cursor.execute("""
                SELECT TABLE_SCHEMA + '.' + TABLE_NAME as TableName
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_SCHEMA, TABLE_NAME
            """)
            tables = [row[0] for row in cursor.fetchall()]
            print(f"Successfully fetched {len(tables)} tables")
            
        elif db_type == 'MySQL':
            conn = get_database_connection(config, is_target)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT CONCAT(TABLE_SCHEMA, '.', TABLE_NAME) as TableName
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = %s AND TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """, (database,))
            tables = [row[0] for row in cursor.fetchall()]
            print(f"MySQL: fetched tables: {tables}")
            
        elif db_type == 'PostgreSQL':
            conn = get_database_connection(config, is_target)
            cursor = conn.cursor()
            print(f"PostgreSQL: running table list query on DB: {database} as user: {config.get('username') or config.get('targetUsername')}, all user schemas")
            cursor.execute("""
                SELECT schemaname, tablename FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                ORDER BY schemaname, tablename
            """)
            rows = cursor.fetchall()
            print(f"PostgreSQL: raw rows: {rows}")
            tables = [f"{row[0]}.{row[1]}" for row in rows]
            print(f"PostgreSQL: formatted tables: {tables}")
            
        elif db_type == 'MongoDB':
            client = get_database_connection(config, is_target)
            db = client[database]
            tables = db.list_collection_names()
            print(f"MongoDB: fetched collections: {tables}")
            client.close()
            
        else:
            raise Exception(f"Unsupported database type: {db_type}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error fetching tables: {error_msg}")
        raise Exception(f"Failed to fetch tables: {error_msg}")
    
    finally:
        # Clean up resources
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn and db_type != 'MongoDB':
            try:
                conn.close()
                print("Database connection closed")
            except:
                pass
    
    return tables

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save-source-config', methods=['POST'])
def save_source_config():
    data = request.json
    print("Source Configuration:", data)
    # You can add database save logic here later
    return jsonify({"status": "success", "message": "Source configuration saved"})

@app.route('/save-target-config', methods=['POST'])
def save_target_config():
    data = request.json
    print("Target Configuration:", data)
    # You can add database save logic here later
    return jsonify({"status": "success", "message": "Target configuration saved"})

@app.route('/test-source-connection', methods=['POST'])
def test_source_connection():
    global source_config
    data = request.json
    print("Testing Source Connection:", data)
    try:
        db_type = data.get('sourceDbType', '')
        server = data.get('serverHost', '')
        database = data.get('dbName', '')
        
        if not db_type or not server or not database:
            return jsonify({
                "status": "error",
                "message": "Please fill in Database Type, Server, and Database Name"
            }), 400
        
        # Test actual connection by fetching tables
        tables = fetch_tables_from_db(data, is_target=False)
        
        # Store config for later use
        source_config = data.copy()
        
        return jsonify({
            "status": "success",
            "message": f"Source connection successful! Found {len(tables)} tables.",
            "tables": tables
        })
    except Exception as e:
        print(f"Source connection error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Source connection failed: {str(e)}"
        }), 400

@app.route('/test-target-connection', methods=['POST'])
def test_target_connection():
    global target_config
    data = request.json
    print("Testing Target Connection:", data)
    try:
        db_type = data.get('targetDbType', '')
        server = data.get('targetServerHost', '')
        database = data.get('targetDbName', '')
        
        if not db_type or not server or not database:
            return jsonify({
                "status": "error",
                "message": "Please fill in Database Type, Server, and Database Name"
            }), 400
        
        # Test actual connection by fetching tables
        tables = fetch_tables_from_db(data, is_target=True)
        
        # Store config for later use
        target_config = data.copy()
        
        return jsonify({
            "status": "success",
            "message": f"Target connection successful! Found {len(tables)} tables."
        })
    except Exception as e:
        print(f"Target connection error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Target connection failed: {str(e)}"
        }), 400

@app.route('/get-source-tables', methods=['POST'])
def get_source_tables():
    data = request.json
    print("Fetching Source Tables:", data)
    try:
        # Fetch real tables from database
        tables = fetch_tables_from_db(data, is_target=False)
        print(f"Found {len(tables)} source tables")
        return jsonify({
            "status": "success",
            "tables": tables
        })
    except Exception as e:
        print(f"Error fetching source tables: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch tables: {str(e)}"
        }), 400

@app.route('/get-target-tables', methods=['POST'])
def get_target_tables():
    data = request.json
    print("Fetching Target Tables:", data)
    try:
        # Fetch real tables from database
        tables = fetch_tables_from_db(data, is_target=True)
        print(f"Found {len(tables)} target tables")
        return jsonify({
            "status": "success",
            "tables": tables
        })
    except Exception as e:
        print(f"Error fetching target tables: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch tables: {str(e)}"
        }), 400


@app.route('/execute-source-query', methods=['POST'])
def execute_source_query():
    """Execute source database query"""
    global source_config
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({
            "error": "No query provided"
        }), 400
    
    if not source_config:
        return jsonify({
            "error": "Source connection not configured. Please connect first."
        }), 400
    
    conn = None
    cursor = None
    
    try:
        db_type = source_config.get('sourceDbType', '')
        print(f"Executing source query on {db_type}: {query[:100]}...")
        
        if db_type == 'SQL Server':
            conn = get_database_connection(source_config, is_target=False)
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            # Fetch results
            rows = cursor.fetchall()
            results = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert to JSON serializable types
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[col] = value
                results.append(row_dict)
            
            return jsonify({
                "status": "success",
                "results": results,
                "columns": columns,
                "row_count": len(results)
            })
            
        elif db_type == 'MySQL':
            conn = get_database_connection(source_config, is_target=False)
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [column[0] for column in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            results = [{columns[i]: row[i] for i in range(len(columns))} for row in rows]
            
            return jsonify({
                "status": "success",
                "results": results,
                "columns": columns,
                "row_count": len(results)
            })
            
        elif db_type == 'PostgreSQL':
            conn = get_database_connection(source_config, is_target=False)
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            results = [{columns[i]: row[i] for i in range(len(columns))} for row in rows]
            
            return jsonify({
                "status": "success",
                "results": results,
                "columns": columns,
                "row_count": len(results)
            })
            
        elif db_type == 'MongoDB':
            # MongoDB uses aggregation or find, not SQL
            return jsonify({
                "error": "MongoDB queries not supported in this interface. Use aggregation pipeline."
            }), 400
            
        else:
            return jsonify({
                "error": f"Unsupported database type: {db_type}"
            }), 400
            
    except Exception as e:
        error_msg = str(e)
        print(f"Query execution error: {error_msg}")
        return jsonify({
            "error": f"Query failed: {error_msg}"
        }), 500
    
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn and db_type != 'MongoDB':
            try:
                conn.close()
            except:
                pass

@app.route('/execute-target-query', methods=['POST'])
def execute_target_query():
    """Execute target database query"""
    global target_config
    data = request.json
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({
            "error": "No query provided"
        }), 400
    
    if not target_config:
        return jsonify({
            "error": "Target connection not configured. Please connect first."
        }), 400
    
    conn = None
    cursor = None
    
    try:
        db_type = target_config.get('targetDbType', '')
        print(f"Executing target query on {db_type}: {query[:100]}...")
        
        if db_type == 'SQL Server':
            conn = get_database_connection(target_config, is_target=True)
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            # Fetch results
            rows = cursor.fetchall()
            results = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert to JSON serializable types
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    row_dict[col] = value
                results.append(row_dict)
            
            return jsonify({
                "status": "success",
                "results": results,
                "columns": columns,
                "row_count": len(results)
            })
            
        elif db_type == 'MySQL':
            conn = get_database_connection(target_config, is_target=True)
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [column[0] for column in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            results = [{columns[i]: row[i] for i in range(len(columns))} for row in rows]
            
            return jsonify({
                "status": "success",
                "results": results,
                "columns": columns,
                "row_count": len(results)
            })
            
        elif db_type == 'PostgreSQL':
            conn = get_database_connection(target_config, is_target=True)
            cursor = conn.cursor()
            cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            results = [{columns[i]: row[i] for i in range(len(columns))} for row in rows]
            
            return jsonify({
                "status": "success",
                "results": results,
                "columns": columns,
                "row_count": len(results)
            })
            
        elif db_type == 'MongoDB':
            # MongoDB uses aggregation or find, not SQL
            return jsonify({
                "error": "MongoDB queries not supported in this interface. Use aggregation pipeline."
            }), 400
            
        else:
            return jsonify({
                "error": f"Unsupported database type: {db_type}"
            }), 400
            
    except Exception as e:
        error_msg = str(e)
        print(f"Query execution error: {error_msg}")
        return jsonify({
            "error": f"Query failed: {error_msg}"
        }), 500
    
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn and db_type != 'MongoDB':
            try:
                conn.close()
            except:
                pass
@app.route('/validation-dashboard')
def validation_dashboard():
    source_table = request.args.get('source_table', '')
    target_table = request.args.get('target_table', '')
    return render_template('validation_dashboard.html', source_table=source_table, target_table=target_table)

@app.route('/validate-table-counts')
def validate_table_counts():
    """Render a page showing row counts for source and target tables and validation result."""
    source_table = request.args.get('source_table', '')
    target_table = request.args.get('target_table', '')
    source_count = None
    target_count = None
    counts_match = False


    # Fetch counts for source table
    if source_table and source_config:
        try:
            conn = get_database_connection(source_config, is_target=False)
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {source_table}")
            source_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
        except Exception as e:
            source_count = f"Error: {str(e)}"

    # Fetch counts for target table
    if target_table and target_config:
        try:
            conn = get_database_connection(target_config, is_target=True)
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {target_table}")
            target_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
        except Exception as e:
            target_count = f"Error: {str(e)}"

    # Compare counts if both are valid integers
    try:
        counts_match = int(source_count) == int(target_count)
    except Exception:
        counts_match = False

    return render_template(
        'validation_results.html',
        source_table=source_table,
        target_table=target_table,
        source_count=source_count,
        target_count=target_count,
        counts_match=counts_match
    )

# New route for top 5 records validation
@app.route('/validate-top5-records')
def validate_top5_records():
    source_table = request.args.get('source_table', '')
    target_table = request.args.get('target_table', '')
    source_rows = []
    target_rows = []
    source_columns = []
    target_columns = []
    validation = []

    # Fetch top 5 from source
    if source_table and source_config:
        try:
            conn = get_database_connection(source_config, is_target=False)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {source_table} LIMIT 5")
            source_columns = [desc[0] for desc in cursor.description]
            source_rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            return jsonify({"error": f"Source error: {str(e)}"}), 500

    # Fetch top 5 from target
    if target_table and target_config:
        try:
            conn = get_database_connection(target_config, is_target=True)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {target_table} LIMIT 5")
            target_columns = [desc[0] for desc in cursor.description]
            target_rows = cursor.fetchall()
            cursor.close()
            conn.close()
        except Exception as e:
            return jsonify({"error": f"Target error: {str(e)}"}), 500

    # Compare columns and values
    columns = list(set(source_columns) | set(target_columns))
    columns.sort()
    for i in range(5):
        src = dict(zip(source_columns, source_rows[i])) if i < len(source_rows) else {}
        tgt = dict(zip(target_columns, target_rows[i])) if i < len(target_rows) else {}
        row_result = {}
        for col in columns:
            src_val = src.get(col)
            tgt_val = tgt.get(col)
            row_result[col] = {
                "source": src_val,
                "target": tgt_val,
                "match": src_val == tgt_val
            }
        validation.append(row_result)

    return jsonify({
        "columns": columns,
        "validation": validation
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 ETL - Validation testing is running!")
    print("="*60)
    print("📍 Access the application at: http://localhost:3000")
    print("📍 Or use: http://127.0.0.1:3000")
    print("📍 Network URL: http://10.10.32.214:3000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=3000)

