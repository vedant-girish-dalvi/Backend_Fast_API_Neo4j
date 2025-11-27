from neo4j import GraphDatabase

URI  = "neo4j://127.0.0.1:7687"
USERNAME= "neo4j"
PASSWORD = "test1234"
# URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
AUTH = (USERNAME, PASSWORD)

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

def test_connection():
    with driver:
        driver.verify_connectivity()
        print("Connection established.")

test_connection()

records, summary, keys = driver.execute_query( # (1)
    "RETURN COUNT {()} AS count"
)

# Get the first record
first = records[0]      # (2)

# Print the count entry
print(first["count"])   # (3)


driver.close()