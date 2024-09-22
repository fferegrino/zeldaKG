from neo4j import GraphDatabase
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

node_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
WITH label AS nodeLabels, collect(property) AS properties
RETURN {labels: nodeLabels, properties: properties} AS output

"""

rel_properties_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE NOT type = "RELATIONSHIP" AND elementType = "relationship"
WITH label AS nodeLabels, collect(property) AS properties
RETURN {type: nodeLabels, properties: properties} AS output
"""

rel_query = """
CALL apoc.meta.data()
YIELD label, other, elementType, type, property
WHERE type = "RELATIONSHIP" AND elementType = "node"
RETURN {source: label, relationship: property, target: other} AS output
"""

class ZeldaKG:
    def __init__(self, uri=None, user=None, password=None):
        if not uri:
            uri = f"bolt://{os.getenv('NEO4J_HOST')}:{os.getenv('NEO4J_PORT')}"
        if not user:
            user = os.getenv('NEO4J_USER')
        if not password:
            password = os.getenv('NEO4J_PASSWORD')

        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password)
        )

    def close(self):
        self.driver.close()

    def query_database(self, neo4j_query, params={}):
        with self.driver.session() as session:
            result = session.run(neo4j_query, params)
            output = [r.values() for r in result]
            output.insert(0, result.keys())
            return output
        
    def _get_node_schema(self):
        properties_descriptions = {
            'name': 'Name of the entity',
            'uri': 'URI of the entity, it is a unique identifier',
            'gender': 'Gender of the entity, if applicable',
        }

        node_props = self.query_database(node_properties_query)
        nodes = [node[0] for node in node_props[1:]]

        node_descriptions = []
        for node in nodes:
            listable_properties = sorted([prop for prop in node['properties'] if prop in properties_descriptions])
            node_description = f" - {node['labels']}, with properties: {', '.join(listable_properties)}"
            node_descriptions.append(node_description)

        prop_descriptions = [
            f" - {prop}: {properties_descriptions[prop]}" for prop in sorted(properties_descriptions)
        ]

        property_description_instructions = [
            "### Nodes",
            "",
            "The following are the nodes in the graph database, along with their properties.",
            "The property descriptions are listed at the end.",
            "",
            *node_descriptions,
            "",
            "Property descriptions:",
            *prop_descriptions,
        ]

        return "\n".join(property_description_instructions)

    
    def _get_rel_schema(self):
        rels = self.query_database(rel_query)
        rels = [r[0] for r in rels[1:]]

        rel_descriptions = []
        for rel in rels:
            targets = ", ".join([f"`{t}`" for t in rel['target']])
            rel_description = f" - `{rel['relationship']}`, that relates `{rel['source']}` with {targets}"
            rel_descriptions.append(rel_description)

        rel_props_descriptions = {
            'relation':'When used as a property of `related_to`, it specifies the type of relationship between two entities (father, mother, etc)'
        }

        rel_props_descriptions = [
            f" - {prop}: {rel_props_descriptions[prop]}" for prop in sorted(rel_props_descriptions)
        ]

        rels_description_instructions = [
            "### Relationships",
            "",
            "The following are the relationships in the graph database",
            "",
            *rel_descriptions,
            "",
            "Property descriptions:",
            *rel_props_descriptions,
        ]

        return "\n".join(rels_description_instructions)
    
    def _get_system_message(self):

        node_schema = self._get_node_schema()
        rel_schema = self._get_rel_schema()
        return f"""
## Task:

Generate Cypher queries to query a Neo4j graph database based on the provided schema definition.

## Instructions:

You are an expert at generating Cypher queries to query a Neo4j graph database based on the provided schema definition.
Use only the provided relationship types and properties.
Do not use any other relationship types or properties that are not provided.
If you cannot generate a Cypher statement based on the provided schema, explain the reason to the user.
Try to eliminate duplicate results.
Remove any markdown formatting from your response.

## Schema:

{node_schema}
{rel_schema}

Note: Do not include any explanations or apologies in your responses, nor markdown formatting.
        """.strip()
    
    def get_proposed_cypher(self, question):
        messages = [
            {"role": "system", "content": self._get_system_message()},
            {"role": "user", "content": question},
        ]
        completions = openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            temperature=0.0,
            max_tokens=1000,
            messages=messages
        )

        return completions.choices[0].message.content