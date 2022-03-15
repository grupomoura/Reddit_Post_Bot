import sqlite3
con = sqlite3.connect('db/data.db')
cur = con.cursor()

def insert_db(value):
    cur.execute("INSERT into posts_reddit (postagens) values (?)", (value,))
    con.commit()

def insert_db_recusadas(value):
    cur.execute("INSERT into posts_reddit_recusadas (postagem_recusada) values (?)", (value,))
    con.commit()

def consult_db():
    data = list(cur.execute("SELECT * from posts_reddit"))
    return data

def consult_db_recusadas():
    data = list(cur.execute("SELECT * from posts_reddit_recusadas"))
    return data

def removeColumn(table, column):
    columns = []
    for row in cur.execute('PRAGMA table_info(' + table + ')'):
        columns.append(row[1])
    columns.remove(column)
    columns = str(columns)
    columns = columns.replace("[", "(")
    columns = columns.replace("]", ")")
    for i in ["\'", "(", ")"]:
        columns = columns.replace(i, "")
    cur.execute('CREATE TABLE temptable AS SELECT ' + columns + ' FROM ' + table)
    cur.execute('DROP TABLE ' + table)
    cur.execute('ALTER TABLE temptable RENAME TO ' + table)
    con.commit()


"""
(.*\n)\1
$1

CREATE TABLE post_registry (
	id BIGINT PRIMARY KEY AUTOINCREMENT,
	criado_em TIMESTAMP,
	postagem VARCHAR,
	CONSTRAINT post_registry_PK PRIMARY KEY (id)
);"""

"""
SELECT *
  FROM post_registry;

SELECT *
  FROM post_registry
 WHERE id = 1;

DELETE 
  FROM nft_db
 WHERE id = 1;

 UPDATE nft_db
   SET postagem = 'novo valor'
 WHERE ID = 1; 

"""