from neo4j import GraphDatabase

uri = "bolt://10.22.111.10:7687"  # Replace with Neo4j host IP
user = "neo4j"
password = "damages33"

driver = GraphDatabase.driver(uri, auth=(user, password))
driver.verify_connectivity()
print("Connected successfully!")
