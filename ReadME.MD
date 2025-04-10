## How to set up environment

Note env can bne name whatever

```python3 -m venv env```

To activate run:
```source env/bin/activate```

To stop run:
```decativate```

To load packages run:
``` pip3 install -r requirments.txt ```


## To run API Server
Old method:
```uvicorn main:api --port 9999```

New method:
```fastapi dev main.py --port 9999```

To view docs run:
```localhost:9999/docs```

## Database
To Query database run:
```sqlite3 testdb.db "select * from people;"```
or 
```sqlite3 <database>
.tables
.headers on
<sql_command>
```