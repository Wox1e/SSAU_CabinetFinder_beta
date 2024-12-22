from neo4j import GraphDatabase
import json
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DB

class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver is not None:
            self.driver.close()

# Метод, который передает запрос в БД
    def query(self, query, db=None):
        assert self.driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.driver.session(database=db) if db is not None else self.driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response
    


connection = Neo4jConnection(uri=NEO4J_URI, user=NEO4J_USER, password=NEO4J_PASSWORD)

try:
    print(f"Trying to connect to Neo4j ({NEO4J_URI})")
    connection.driver.verify_connectivity()
    print("Connected to Neo4j")
except:
    print("Cannot connect to Neo4J")


def dict_to_str(d):
    # Формируем строку, где ключи не будут в кавычках, а значения останутся как есть
    items = [f"{key}: {json.dumps(value)}" for key, value in d.items()]
    return "{%s}" % ", ".join(items)

def create_Node(category:str, properties:dict) -> str:

    '''
    Creates node by category and name \n
    Returns its elementID
    '''
    properties = dict_to_str(properties)

    query_string = f'CREATE (a:{category} {properties}) RETURN a'
    response = connection.query(query_string, db=NEO4J_DB)
    return response[0]['a'].element_id

def create_OneDirectionalEdge(sourceNode_elementID:str, destNode_elementID:str, RelationType:str):
    '''
    Warning: RelationType cannot contain spaces!\n
    Creates one directional edge from sourceNode to destNode\n
    Returns its elementID
    '''

    query_string = f'''
    MATCH(a)
    WHERE elementId(a)=	"{sourceNode_elementID}"
    MATCH(b)
    WHERE elementId(b)=	"{destNode_elementID}"
    CREATE (a)-[r:{RelationType}]->(b)
    RETURN r
    '''
    response = connection.query(query_string, db=NEO4J_DB)
    return response[0]['r'].element_id

def get_Node(elementId:str):

    '''
    Returns dict with Node data\n
    has atributes:\n
    _properties\n
    labels
    '''


    query_string = f'''
    MATCH(a)
    WHERE elementId(a)=	"{elementId}"
    RETURN a
    '''
    response = connection.query(query_string, db=NEO4J_DB)
    return response[0]['a']

def get_path_between_nodes(sourceNode_elementID:str, destNode_elementID:str):
    '''
    Returns list of nodes on shortest path from source to dest\n
    '''


    query_string = f'''
    MATCH (source:landmark),(target:landmark)
    WHERE elementId(source) = '{sourceNode_elementID}' AND elementId(target) = '{destNode_elementID}'
    MATCH p = shortestPath((source)-[*]-(target))
    return p;
    '''
    response = connection.query(query_string, db=NEO4J_DB)
    return response[0]['p'].nodes
    
def get_all_nodes():

    query_string = f'''
    MATCH(N)
    RETURN N
    '''
    response = connection.query(query_string, db=NEO4J_DB)
    l = []
    for record in response:
        l.append(record['N'])

    return l

def delete_Node(elementID:str) -> bool:
    
    query_string = f'''
    MATCH (a)
    WHERE elementID(a) = "{elementID}"
    DELETE a
    '''
    try:
        response = connection.query(query_string, db=NEO4J_DB)
    except:
        return False
    
def delete_edge(sourceNode_elementID:str, destNode_elementID:str, RelationType:str):
    ...

def add_properties_to_node(elementID:str, properties:dict) -> bool:

    for key in properties.keys():
        
        query_string = f'''

        MATCH (n:landmark)
        WHERE elementID(n) = "{elementID}"
        SET n.{key} = '{properties[key]}'
        RETURN n

        '''
        try:
            response = connection.query(query_string, db=NEO4J_DB)
        except:
            return False


