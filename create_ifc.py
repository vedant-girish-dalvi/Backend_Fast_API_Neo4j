import ifcopenshell
import ifcopenshell.guid

# Create a new IFC file
ifc_file = ifcopenshell.file(schema="IFC4")

# Create project and context
project = ifc_file.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="Example Project")
site = ifc_file.create_entity("IfcSite", GlobalId=ifcopenshell.guid.new(), Name="Example Site")
building = ifc_file.create_entity("IfcBuilding", GlobalId=ifcopenshell.guid.new(), Name="Example Building")
storey = ifc_file.create_entity("IfcBuildingStorey", GlobalId=ifcopenshell.guid.new(), Name="Storey 1")

# Relate hierarchy
ifc_file.create_entity("IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=project, RelatedObjects=[site])
ifc_file.create_entity("IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=site, RelatedObjects=[building])
ifc_file.create_entity("IfcRelAggregates", GlobalId=ifcopenshell.guid.new(), RelatingObject=building, RelatedObjects=[storey])

# Create building elements with specific GUIDs from your RDF example
beam = ifc_file.create_entity(
    "IfcBeam", 
    GlobalId="3k9HsYt7n9fhP5v$yY1B2a", 
    Name="Main Beam 1"
)
column = ifc_file.create_entity(
    "IfcColumn", 
    GlobalId="2Yh5Xdr4a7b97Xj1KdfkZe", 
    Name="Corner Column"
)
wall = ifc_file.create_entity(
    "IfcWall", 
    GlobalId="1AbcDeFgHiJkLmNoPqRstU", 
    Name="South Wall"
)
slab = ifc_file.create_entity(
    "IfcSlab", 
    GlobalId="4WxyZ12OP34QrSt56UvWxy", 
    Name="First Floor Slab"
)

# Relate elements to storey
ifc_file.create_entity("IfcRelContainedInSpatialStructure", GlobalId=ifcopenshell.guid.new(), RelatingStructure=storey, RelatedElements=[beam, column, wall, slab])

# Save IFC
ifc_file.write("example.ifc")
print("Minimal example IFC file 'example.ifc' created!")
