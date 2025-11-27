import ifcopenshell
import ifcopenshell.guid
from rdflib import Graph, Namespace

# Namespaces
CDO = Namespace("https://w3id.org/damagemodels/cdo#")

def add_damages_from_rdf(ifc_file_path, rdf_file_path, output_ifc_path):
    # Load IFC model
    model = ifcopenshell.open(ifc_file_path)

    # Load RDF
    g = Graph()
    g.parse(rdf_file_path, format="ttl")

    for damage in g.subjects():
        # Collect damage type(s)
        damage_types = list(g.objects(damage, CDO['Crack'])) + list(g.objects(damage, CDO['Spalling']))
        if not damage_types:
            continue

        damage_name = str(g.value(damage, CDO['hasName'])) or "Unnamed Damage"
        width = g.value(damage, CDO['hasWidth'])
        depth = g.value(damage, CDO['hasDepth'])
        severity = g.value(damage, CDO['hasSeverity'])
        coords = g.value(damage, CDO['hasCoordinates'])
        damage_class = ", ".join([str(dt).split("#")[-1] for dt in damage_types])

        # Get IFC element GUID
        ifc_element = None
        for obj in g.objects(damage, CDO['damageLocatedOn']):
            ifc_guid = g.value(obj, CDO['ifcGlobalId'])
            if ifc_guid:
                ifc_element = model.by_guid(str(ifc_guid))
                break
        if not ifc_element:
            print(f"Warning: IFC element for damage {damage} not found. Skipping.")
            continue

        # Create IfcProxy to represent damage
        damage_proxy = model.create_entity(
            "IfcProxy",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name=damage_name,
            Description="Damage instance from RDF",
            ObjectType=damage_class,
            Tag=None,
            ProxyType="NOTDEFINED"
        )

        # === Property Set: Damage Properties ===
        pset_damage = model.create_entity(
            "IfcPropertySet",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name="PSet_DamageProperties",
            Description="Damage metadata",
            HasProperties=[]
        )

        def add_property(pset, name, value):
            if value is not None:
                prop = model.create_entity(
                    "IfcPropertySingleValue",
                    Name=name,
                    Description=None,
                    NominalValue=ifcopenshell.util.element.add_simple_value(str(value)),
                    Unit=None
                )
                pset.HasProperties.append(prop)

        add_property(pset_damage, "DamageClass", damage_class)
        add_property(pset_damage, "Width", width)
        add_property(pset_damage, "Depth", depth)
        add_property(pset_damage, "Severity", severity)
        add_property(pset_damage, "Coordinates", coords)

        # Link properties to proxy
        model.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            RelatedObjects=[damage_proxy],
            RelatingPropertyDefinition=pset_damage
        )

        # === Property Set: Label damage class on original element ===
        pset_label = model.create_entity(
            "IfcPropertySet",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            Name="PSet_DamageLabels",
            Description="Damage labels for element",
            HasProperties=[]
        )
        add_property(pset_label, "DamageClass", damage_class)

        model.create_entity(
            "IfcRelDefinesByProperties",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            RelatedObjects=[ifc_element],
            RelatingPropertyDefinition=pset_label
        )

        # === Link proxy damage to IFC element ===
        model.create_entity(
            "IfcRelAggregates",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=None,
            RelatingObject=ifc_element,
            RelatedObjects=[damage_proxy]
        )

    # Save updated IFC
    model.write(output_ifc_path)
    print(f"Updated IFC saved to: {output_ifc_path}")


# Example usage
add_damages_from_rdf(
    ifc_file_path="example.ifc",
    rdf_file_path="ontology_output.ttl",
    output_ifc_path="example_with_damages.ifc"
)
