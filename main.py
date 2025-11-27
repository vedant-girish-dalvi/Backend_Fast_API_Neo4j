from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from neo4j import GraphDatabase
from typing import Annotated
from dotenv import load_dotenv
import os, json

# --- Load environment variables ---
load_dotenv()
uri = os.getenv("uri", "bolt://localhost:7687")
user = os.getenv("user", "neo4j")
pwd = os.getenv("pwd", "your_password")

# --- Neo4j Driver Wrapper ---
class Neo4jConnection:
    def __init__(self, uri, user, pwd):
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None, db=None):
        with self.driver.session(database=db) if db else self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

# Dependency injection
def get_db():
    db = Neo4jConnection(uri, user, pwd)
    try:
        yield db
    finally:
        db.close()

# --- FastAPI Setup ---
app = FastAPI()

# # --- Data Models ---
# class Damage(BaseModel):
#     id: str = Field(..., min_length=1, description="Unique ID of the damage")
#     type: str = Field(..., min_length=1, description="Type of damage (e.g., Crack, Spalling)")
#     severity: str = Field(..., min_length=1, description="Severity level of the damage")

# class Relationship(BaseModel):
#     source_id: str = Field(..., min_length=1)
#     target_id: str = Field(..., min_length=1)
#     relation_type: str = Field(..., min_length=1)

# --- Root / Health Check ---
@app.get("/")
def root():
    return {"message": "FastAPI + Neo4j API is running!"}

## --- API Endpoints ---
## Add new damage instance
# @app.post("/damage")
# def create_damage(damage: Damage, db: Annotated[Neo4jConnection, Depends(get_db)]):
#     if not damage.id.strip() or not damage.type.strip() or not damage.severity.strip():
#         raise HTTPException(status_code=400, detail="Damage fields cannot be empty")
    
#     query = f"""
#     CREATE (d:Damage:{damage.type} {{id: $id, severity: $severity}})
#     RETURN d
#     """
#     try:
#         result = db.query(query, {"id": damage.id, "severity": damage.severity})
#         return {"status": "created", "damage": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Get damage instance info with ID
# @app.get("/damage/{id}")
# def get_damage(id: str, db: Annotated[Neo4jConnection, Depends(get_db)]):
#     if not id.strip():
#         raise HTTPException(status_code=400, detail="ID cannot be empty")
    
#     query = "MATCH (d:Damage {id: $id}) RETURN d"
#     try:
#         result = db.query(query, {"id": id})
#         if not result:
#             raise HTTPException(status_code=404, detail="Damage not found")
#         return result[0]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Delete a damage instance
# @app.delete("/damage/{id}")
# def delete_damage(id: str, db: Annotated[Neo4jConnection, Depends(get_db)]):
#     if not id.strip():
#         raise HTTPException(status_code=400, detail="ID cannot be empty")
    
#     query = """
#     MATCH (d:Damage {id: $id})
#     DETACH DELETE d
#     RETURN $id AS deleted_id
#     """
#     try:
#         result = db.query(query, {"id": id})
#         if not result:
#             raise HTTPException(status_code=404, detail="Damage not found")
#         return {"status": "deleted", "id": result[0]["deleted_id"]}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Add relatiionship between damage instances with IDs
# @app.post("/damage/relate")
# def relate_damages(relationship: Relationship, db: Annotated[Neo4jConnection, Depends(get_db)]):
#     if not relationship.source_id.strip() or not relationship.target_id.strip() or not relationship.relation_type.strip():
#         raise HTTPException(status_code=400, detail="Relationship fields cannot be empty")
    
#     query = f"""
#     MATCH (a:Damage {{id: $source_id}}), (b:Damage {{id: $target_id}})
#     CREATE (a)-[r:{relationship.relation_type}]->(b)
#     RETURN a.id AS source, type(r) AS relation, b.id AS target
#     """
#     try:
#         result = db.query(query, {
#             "source_id": relationship.source_id,
#             "target_id": relationship.target_id
#         })
#         return {"status": "relationship_created", "details": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# # --- Upload JSON file with detections ---
# @app.post("/upload_json")
# async def upload_json(file: UploadFile = File(...), db: Annotated[Neo4jConnection, Depends(get_db)] = None):
#     if not file.filename.endswith(".json"):
#         raise HTTPException(status_code=400, detail="Only JSON files are allowed")

#     try:
#         contents = await file.read()
#         data = json.loads(contents.decode("utf-8"))

#         # Validate main structure
#         if "image_filename" not in data or "detections" not in data:
#             raise HTTPException(status_code=400, detail="Invalid JSON structure. Must include 'image_filename' and 'detections'.")

#         image_filename = data["image_filename"]
#         detections = data["detections"]

#         if not isinstance(detections, list):
#             raise HTTPException(status_code=400, detail="'detections' must be a list.")

#         created_nodes = []
#         created_rels = []

#         for idx, det in enumerate(detections):
#             damage_class = det.get("damage_class", "Unknown")
#             damage_params = det.get("damage_parameters", {})
#             location3D = det.get("damage_location_3D", [])
#             location2D = det.get("damage_location_2D", [])
#             ifc_element = det.get("ifc_element")
#             ifc_guid = det.get("ifc_guid")

#             # Create a unique ID based on filename + index
#             damage_id = f"{image_filename}_d{idx}"

#             # Create Damage node with properties
#             query = f"""
#             CREATE (d:Damage:{damage_class} {{
#                 id: $id,
#                 image: $image,
#                 severity: $severity,
#                 inspection_status: $inspection_status,
#                 ifc_element: $ifc_element,
#                 ifc_guid: $ifc_guid,
#                 location3D: $location3D,
#                 location2D: $location2D
#             }})
#             RETURN d
#             """
#             result = db.query(query, {
#                 "id": damage_id,
#                 "image": image_filename,
#                 "severity": damage_params.get("severity_level"),
#                 "inspection_status": damage_params.get("inspection_status"),
#                 "ifc_element": ifc_element,
#                 "ifc_guid": ifc_guid,
#                 "location3D": json.dumps(location3D),
#                 "location2D": json.dumps(location2D)
#             })
#             created_nodes.append(result)

#         # Create relationships after nodes are created
#         for idx, det in enumerate(detections):
#             damage_id = f"{image_filename}_d{idx}"
#             relations = det.get("damage_relations", [])
#             for rel in relations:
#                 related_indices = rel.get("related_to_indices", [])
#                 rel_type = rel.get("relation_type", "RELATED_TO")
#                 for target_idx in related_indices:
#                     target_id = f"{image_filename}_d{target_idx}"
#                     query = f"""
#                     MATCH (a:Damage {{id: $source_id}}), (b:Damage {{id: $target_id}})
#                     CREATE (a)-[r:{rel_type}]->(b)
#                     RETURN a.id AS source, type(r) AS relation, b.id AS target
#                     """
#                     result = db.query(query, {
#                         "source_id": damage_id,
#                         "target_id": target_id
#                     })
#                     created_rels.extend(result)

#         return {
#             "status": "uploaded",
#             "image_filename": image_filename,
#             "damages_created": len(created_nodes),
#             "relationships_created": len(created_rels),
#             "nodes": created_nodes,
#             "relationships": created_rels
#         }

#     except json.JSONDecodeError:
#         raise HTTPException(status_code=400, detail="Invalid JSON file")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# --- Upload New Damage JSON Format (Adapted to New Structure) ---
@app.post("/upload_damage_json")
async def upload_damage_json(
    file: UploadFile = File(...),
    db: Annotated[Neo4jConnection, Depends(get_db)] = None
):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are allowed")

    try:
        contents = await file.read()
        data = json.loads(contents.decode("utf-8"))

        created_nodes = []
        created_relationships = []

        # Expect: { "Damage_001": { Metadata, Epochs } }
        for damage_key, damage_obj in data.items():

            if "Metadata" not in damage_obj or "Epochs" not in damage_obj:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid structure under '{damage_key}'. Required: Metadata + Epochs."
                )

            metadata = damage_obj["Metadata"]
            epochs = damage_obj["Epochs"]

            # ---------------------------------------
            # CREATE DAMAGE NODE (STATIC METADATA)
            # ---------------------------------------
            damage_id = metadata.get("Damage_ID", damage_key)

            damage_query = """
            MERGE (d:Damage {
                Damage_ID: $Damage_ID
            })
            SET d.DamageType = $DamageType,
                d.Image_Filename = $Image_Filename,
                d.IFC_Filepath = $IFC_Filepath,
                d.IFC_Data = $IFC_Data,
                d.IFC_Element = $IFC_Element,
                d.IFC_GUID = $IFC_GUID
            RETURN d
            """

            damage_params = {
                "Damage_ID": damage_id,
                "DamageType": metadata.get("DamageType"),
                "Image_Filename": metadata.get("Image_Filename"),
                "IFC_Filepath": metadata.get("IFC_Filepath"),
                "IFC_Data": metadata.get("IFC_Data"),
                "IFC_Element": metadata.get("IFC_Element"),
                "IFC_GUID": metadata.get("IFC_GUID")
            }

            damage_result = db.query(damage_query, damage_params)
            created_nodes.append(damage_result)

            # ---------------------------------------
            # CREATE EPOCH NODES
            # ---------------------------------------
            prev_epoch_id = None

            for ep in epochs:
                epoch_num = ep.get("Epoch")
                epoch_id = f"{damage_id}_epoch_{epoch_num}"

                epoch_query = """
                CREATE (e:Epoch {
                    epoch_id: $epoch_id,
                    Epoch: $Epoch,
                    Storage_Path: $Storage_Path,
                    ReferenceCoOrdinateSystem: $ReferenceCoOrdinateSystem,
                    Length_m: $Length_m,
                    Width_mm: $Width_mm,
                    Position_3D_Axis: $Position_3D_Axis,
                    Max_Width_3D_Position: $Max_Width_3D_Position
                })
                RETURN e
                """

                epoch_params = {
                    "epoch_id": epoch_id,
                    "Epoch": epoch_num,
                    "Storage_Path": ep.get("Storage_Path"),
                    "ReferenceCoOrdinateSystem": ep.get("ReferenceCoOrdinateSystem"),
                    "Length_m": ep.get("Length_m"),
                    "Width_mm": ep.get("Width_mm"),
                    "Position_3D_Axis": json.dumps(ep.get("Position_3D_Axis")),
                    "Max_Width_3D_Position": json.dumps(ep.get("Max_Width_3D_Position"))
                }

                epoch_result = db.query(epoch_query, epoch_params)
                created_nodes.append(epoch_result)

                # Relationship: Damage -> Epoch
                rel_query = """
                MATCH (d:Damage {Damage_ID: $Damage_ID}),
                      (e:Epoch {epoch_id: $epoch_id})
                MERGE (d)-[:HAS_EPOCH]->(e)
                """
                db.query(rel_query, {"Damage_ID": damage_id, "epoch_id": epoch_id})

                # Link epoch → next epoch
                if prev_epoch_id:
                    next_rel_query = """
                    MATCH (e1:Epoch {epoch_id: $e1}),
                          (e2:Epoch {epoch_id: $e2})
                    MERGE (e1)-[:NEXT_EPOCH]->(e2)
                    """
                    db.query(next_rel_query, {"e1": prev_epoch_id, "e2": epoch_id})
                    created_relationships.append(
                        {"from": prev_epoch_id, "to": epoch_id, "type": "NEXT_EPOCH"}
                    )

                prev_epoch_id = epoch_id

        return {
            "status": "success",
            "damage_nodes_created": len(created_nodes),
            "relationships_created": len(created_relationships),
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
