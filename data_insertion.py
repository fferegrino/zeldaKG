from neo4j import GraphDatabase
import pandas as pd
import os
import json

def escape(string):
    # Not sure why I decided to do this 
    # six years ago, but I'll leave it in place
    # just in case
    return json.dumps(string)[1:-1]

def main():
    host = os.environ['NEO4J_HOST']
    user = os.environ['NEO4J_USER']
    password = os.environ['NEO4J_PASSWORD']
    port = os.environ['NEO4J_PORT']
    driver = GraphDatabase.driver(
        f"bolt://{host}:{port}", 
        auth=(user, password)
    )

    with driver.session() as session:
        nodes = session.run("MATCH (n:Entity) RETURN n LIMIT 25").data()

    if nodes:
        print("There is data in the database")
        return 0
    
    entities = pd.read_csv("relation_extraction/info/entities.csv", index_col=0)
    create_template = "CREATE (e:Entity{name:\"%s\"})"
    with driver.session() as session:
        for _, row in entities.iterrows():
            name = escape(row['name'])
            insert_stmt = create_template % (name)
            session.run(insert_stmt)
        session.run("CREATE INDEX FOR (e:Entity) ON (e.name)")

    
    resources = pd.read_csv("relation_extraction/info/urls.csv", index_col=0)
    create_template = "CREATE (e:Resource{uri:\"%s\"})"
    with driver.session() as session:
        for _, row in resources.iterrows():
            url = row['url']
            insert_stmt = create_template % (url) 
            session.run(insert_stmt)
        session.run("CREATE INDEX FOR (r:Resource) ON (r.uri)")

    wikia_rels = pd.read_csv("relation_extraction/info/entities.wikia.csv", index_col=0)
    gamepedia_rels = pd.read_csv("relation_extraction/info/entities.gamepedia.csv", index_col=0)

    relationship_template = """MATCH (from:Resource{uri:\"%s\"}),(to:Entity{name:\"%s\"})
    MERGE (from)-[r:Represents]->(to)
    SET r.%s=true"""

    for site, rels in zip(["wikia","gamepedia"],[ wikia_rels, gamepedia_rels]):
        print(site)
        with driver.session() as session:
            for i, row in rels.iterrows():
                if (i+1 )% 1500 == 0:
                    print(i)
                try:
                    name = escape(row['name'])
                    relationship_stmt = relationship_template % (row['page'], name, site)
                    session.run(relationship_stmt)
                except Exception as inst:
                    print("Error", i)
                    print(inst)
                    break

    hard_relationships = pd.read_csv("relation_extraction/info/hard_relationships.csv", index_col=0)
    relationship_template = """MATCH (from:Resource{uri:\"%s\"}),(to:Resource{uri:\"%s\"})
    MERGE (from)-[r:%s{verb:\"%s\",preposition:\"%s\"}]->(to)"""
    with driver.session() as session:
        for i, r in hard_relationships.iterrows():
            one = r["url"]
            verb = r["relation1"]
            preposition = r["relation2"]
            relation = r["attribute"]
            two = r["related_url"]
            create_stmt = relationship_template % (one, two, relation, verb, preposition)
            session.run(create_stmt)


if __name__ == "__main__":
    main()