from flask import Flask, request, jsonify 
import sqlite3

from pubsub import AsyncConn

app = Flask(__name__)
pubnub = AsyncConn("Flask Application", "meu_canal")


def connect_db():
    return sqlite3.connect('data.db')


def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT NOT NULL,p0
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    conn.close()


create_table()

@app.route('/', methods=['POST', 'GET'])
def use_api():
    try:
      

        if request.method == "POST":
            data = request.json.get('data')  
        
            if data is None:
                return jsonify({"error": "No value provided"}), 400
        
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO data (value) VALUES (?)', (data,))
                conn.commit()

            pubnub.publish({"text": data})
            
            return jsonify({"message": "Value added successfully"}), 201

       

        elif request.method == "GET":
            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM data')
                rows = cursor.fetchall()

            values = [{"id": row[0], "data": row[1]} for row in rows]

            return jsonify(values), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
