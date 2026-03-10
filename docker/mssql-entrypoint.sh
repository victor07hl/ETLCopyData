#!/bin/bash
# Start SQL Server in the background
/opt/mssql/bin/sqlservr &
MSSQL_PID=$!

echo "Waiting for SQL Server to be ready..."
for i in $(seq 1 30); do
    /opt/mssql-tools18/bin/sqlcmd \
        -S localhost -U sa -P "$SA_PASSWORD" \
        -Q "SELECT 1" -No > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "SQL Server is ready. Running init script..."
        /opt/mssql-tools18/bin/sqlcmd \
            -S localhost -U sa -P "$SA_PASSWORD" \
            -i /docker/createtable.sql -No
        echo "Database initialised."
        break
    fi
    echo "  Attempt $i/30 — retrying in 2s..."
    sleep 2
done

# Hand back control to SQL Server (keeps the container running)
wait $MSSQL_PID
