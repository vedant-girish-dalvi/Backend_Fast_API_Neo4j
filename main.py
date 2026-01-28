from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from neo4j import GraphDatabase
from typing import Annotated
from dotenv import load_dotenv
import os, json

# --- Load environment variables ---
load_dotenv()
uri = os.getenv('uri')
user = os.getenv('user')
pwd = os.getenv('pwd')

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


# --- Root / Health Check ---
@app.get("/")
async def root():
    return {"message": "FastAPI + Neo4j API is running!"}


# --- Upload JSON Format ---
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
