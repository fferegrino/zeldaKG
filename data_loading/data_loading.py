import csv
import json
import os

from neo4j import GraphDatabase


def escape(string):
    # Not sure why I decided to do this
    # six years ago, but I'll leave it in place
    # just in case
    return json.dumps(string)[1:-1]


def insert_other_appereances(driver):
    relationship_template = """
MATCH (from:ENTITY{{uri:"{from_uri}"}}),(to:ENTITY{{uri:"{to_uri}"}})
MERGE (from)-[r:appears_in]->(to)
""".strip()

    with driver.session() as session:
        with open("relation_extraction/info/other_appereances.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)
            for _, noun1, source, noun2 in reader:
                session.run(relationship_template.format(from_uri=noun1, to_uri=noun2))


def insert_hard_relationships(driver):
    valid_prepositions = {
        "for",
        "throughout",
        "during",
        "within",
        "like",
        "from",
        "of",
        "by",
        "before",
        "with",
        "to",
        "on",
        "in",
    }
    relationship_template = """
MATCH (from:ENTITY{{uri:"{from_uri}"}}),(to:ENTITY{{uri:"{to_uri}"}})
MERGE (from)-[r:appears_in{{verb:"{verb}", preposition:"{preposition}"}}]->(to)
""".strip()
    with driver.session() as session:
        with open("relation_extraction/info/hard_relationships.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)
            for _, noun1, verb, relationship, preposition, noun2 in reader:
                session.run(
                    """MATCH (e1:ENTITY{{uri:"{noun1}"}})
                            SET e1:{relationship}
                            RETURN e1""".format(
                        relationship=relationship.upper(), noun1=noun1
                    )
                )
                if preposition in valid_prepositions:
                    session.run(
                        relationship_template.format(
                            from_uri=noun1,
                            to_uri=noun2,
                            verb=verb.lower(),
                            relationship=relationship.lower(),
                            preposition=preposition.lower(),
                        )
                    )


def insert_entities(driver):
    create_template = """
MERGE (e:ENTITY{{name:"{name}", uri:"{uri}"}})
    ON CREATE
        SET e.{source} = true
    ON MATCH
        SET e.{source} = true
RETURN e
    """.strip()

    with driver.session() as session:
        session.run("CREATE INDEX FOR (e:ENTITY) ON (e.name)")
        session.run("CREATE INDEX FOR (e:ENTITY) ON (e.uri)")

        with open("relation_extraction/info/entities.wikia.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                session.run(create_template.format(name=escape(row[1]), uri=row[2], source="wikia"))

        with open("relation_extraction/info/entities.gamepedia.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                session.run(create_template.format(name=escape(row[1]), uri=row[2], source="gamepedia"))


def insert_genders(driver):
    create_template = """
MATCH (e:ENTITY{{uri:"{uri}"}})
SET e.gender = "{gender}"
RETURN e
    """.strip()

    with driver.session() as session:
        with open("relation_extraction/info/genders.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                session.run(create_template.format(uri=row[0], gender=row[1]))


def insert_races(driver):
    create_template = """
MATCH (from:ENTITY{{uri:"{from_uri}"}}),(to:ENTITY{{uri:"{to_uri}"}})
SET to:RACE
MERGE (from)-[r:is]->(to)
    """.strip()

    with driver.session() as session:
        with open("relation_extraction/info/race.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                session.run(create_template.format(from_uri=row[0], to_uri=row[1]))


def insert_kindred(driver):
    create_template = """
MATCH (from:ENTITY{{uri:"{from_uri}"}}),(to:ENTITY{{uri:"{to_uri}"}})
MERGE (from)-[r:related_to{{relation:"{relation}"}}]->(to)
    """.strip()

    with driver.session() as session:
        with open("relation_extraction/info/kindred.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)
            for [subject, relation, object] in reader:
                if relation:
                    session.run(create_template.format(from_uri=subject, to_uri=object, relation=relation))


def insert_locations(driver):
    create_template = """
MATCH (from:ENTITY{{uri:"{from_uri}"}}),(to:ENTITY{{uri:"{to_uri}"}})
MERGE (from)-[r:{location}]->(to)
    """.strip()

    with driver.session() as session:
        with open("relation_extraction/info/locations.csv", "r") as f:
            reader = csv.reader(f)
            next(reader)
            for [from_uri, location, to_uri] in reader:
                session.run(create_template.format(from_uri=from_uri, to_uri=to_uri, location=location.lower()))


def main():
    host = os.environ["NEO4J_HOST"]
    user = os.environ["NEO4J_USER"]
    password = os.environ["NEO4J_PASSWORD"]
    port = os.environ["NEO4J_PORT"]
    driver = GraphDatabase.driver(f"bolt://{host}:{port}", auth=(user, password))

    with driver.session() as session:
        nodes = session.run("MATCH (n:ENTITY) RETURN n LIMIT 25").data()

    if nodes:
        print("There is data in the database")
        return 0

    insert_entities(driver)

    insert_hard_relationships(driver)

    insert_other_appereances(driver)

    insert_genders(driver)

    insert_races(driver)

    insert_kindred(driver)

    insert_locations(driver)


if __name__ == "__main__":
    main()
