import psycopg2

DB_NAME = "touchcon"
DB_USER = "touchcon"
DB_PASS = "touchcon"
DB_HOST = "localhost"
DB_PORT = "5432" 
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()


cur.execute("DELETE FROM testtest a USING testtest b WHERE a.id < b.id AND a.docnumber = b.docnumber")
conn.commit()
