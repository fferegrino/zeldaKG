from neo4j import GraphDatabase
import anthropic
import openai
import os

def format_results_as_markdown_table(results):
    if not results:
        return ""

    headers = results[0]

    columns = len(headers)

    column_widths = [len(header) for header in headers]
    
    for result in results[1:]:
        column_widths = [
            max(column_width, len(value)) for column_width, value in zip(column_widths, result)
        ]

    rows = []
    def format_row(row, space_char=" "):
        return "|" + ("|".join([f"{space_char}{value:<{column_widths[i]}}{space_char}" for i, value in enumerate(row)])) + "|"

    rows.append(format_row(headers))
    rows.append(format_row(["-" * column_widths[i] for i in range(columns)], "-"))
    for result in results[1:]:
        rows.append(format_row(result))
    rows.append("")
    return "\n".join(rows)

class ZeldaKG:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            f"bolt://{os.environ['NEO4J_HOST']}:{os.environ['NEO4J_PORT']}", 
            auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"])
        )

    def query_database(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            output = [r.values() for r in result]
            output.insert(0, result.keys())
            return output
        
    def get_cypher_system_prompt(self):
        node_schema = self._get_nodes_schema()
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

    ## Schema:

    {node_schema}
    {rel_schema}

    Note: Do not include any explanations or apologies in your responses.""".strip()
        


    def _get_nodes_schema(self):
        node_properties_query = """CALL apoc.meta.data()
    YIELD label, other, elementType, type, property
    WHERE NOT type = "RELATIONSHIP" AND elementType = "node"
    WITH label AS nodeLabels, collect(property) AS properties
    RETURN {labels: nodeLabels, properties: properties} AS output
    """

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
    
    def get_candidate_cypher_query(self, question):
        anthropic_client = anthropic.Anthropic()
        message = anthropic_client.messages.create(
        model=os.environ["ANTHROPIC_MODEL"],
        max_tokens=1000,
        temperature=0,
        system=self.get_cypher_system_prompt(),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    }
                ]
            }
        ]
    )

        return message.content[0].text
    

    def generate_response(self, question,  results_table):
        generation_system_instruction = """
You are a Zelda expert, and your goal is to answer the user's question.
You will be provided with a table of results from a graph database query.
The results are related to the user's question and may represent appereances, counts, or relationships between entities in the Zelda universe.
Do not mention that the results are coming from a neo4j database.
Your task is to generate a response to the user's question based on the provided results.
Do not use any information that is not provided in the results.  
If the results are empty, explain it to the user. 
Use all the information provided to you to answer the question.
Do not return any links, urls or references.
Be as comprehensive as possible. 
        """.strip()

        generation_prompt = f"""These are the results from a graph database query related to the user's question:

{{results_table}}

And the user's question you must answer using the results:

{{question}}
        """
        openai_client = openai.OpenAI()
        prompt = generation_prompt.format(results_table=results_table, question=question)
        messages = [
            {"role": "system", "content": generation_system_instruction},
            {"role": "user", "content": prompt},
        ]
        completions = openai_client.chat.completions.create(
            model=os.environ["OPENAI_MODEL"],
            temperature=0.0,
            max_tokens=1000,
            messages=messages
        )

        return completions.choices[0].message.content

    def _get_rel_schema(self):
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

