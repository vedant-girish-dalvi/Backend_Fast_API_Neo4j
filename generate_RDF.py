import json
from rdflib import Graph, Literal, RDF, RDFS, Namespace, XSD, OWL, URIRef, BNode

# Namespaces
EX = Namespace("http://example.org/damageInstances#")
CDO = Namespace("https://w3id.org/damagemodels/cdo#")
DCE = Namespace("http://purl.org/dc/elements/1.1/")
DCO = Namespace("https://w3id.org/dco#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
OWLNS = Namespace("http://www.w3.org/2002/07/owl#")
RDFNS = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
XSDNS = Namespace("http://www.w3.org/2001/XMLSchema#")
RDFSNS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
VANN = Namespace("http://purl.org/vocab/vann/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
VOAF = Namespace("http://purl.org/vocommons/voaf#")
DOT = Namespace("https://w3id.org/dot#")
IFC = Namespace("https://standards.buildingsmart.org/IFC/DEV/IFC4_2/OWL#")

def json_to_rdf(json_file, rdf_output):
    # Load JSON inference file
    with open(json_file, "r") as f:
        data = json.load(f)

    g = Graph()

    # Bind prefixes
    g.bind("ex", EX)
    g.bind("cdo", CDO)
    g.bind("dce", DCE)
    g.bind("dco", DCO)
    g.bind("foaf", FOAF)
    g.bind("owl", OWLNS)
    g.bind("rdf", RDFNS)
    g.bind("xsd", XSDNS)
    g.bind("rdfs", RDFSNS)
    g.bind("vann", VANN)
    g.bind("dcterms", DCTERMS)
    g.bind("voaf", VOAF)
    g.bind("dot", DOT)
    g.bind("ifc", IFC)

    #################################################################
    # Ontology Metadata
    #################################################################
    ontology_uri = URIRef("https://w3id.org/damagemodels/cdo#")
    g.add((ontology_uri, RDF.type, OWL.Ontology))
    g.add((ontology_uri, RDF.type, VOAF.Vocabulary))
    g.add((ontology_uri, OWL.versionIRI, URIRef("https://w3id.org/damagemodels/cdo#/0.5.0")))
    g.add((ontology_uri, OWL.versionInfo, Literal("0.5.0")))
    g.add((ontology_uri, RDFS.comment, Literal("Ontology for damage and defects in reinforced concrete.", lang="en")))
    g.add((ontology_uri, DCTERMS.license, Literal("https://creativecommons.org/licenses/by/1.0")))
    g.add((ontology_uri, DCTERMS.description, Literal("Ontology for damage and defects in reinforced concrete.", lang="en")))
    g.add((ontology_uri, DCTERMS.modified, Literal("2019-12-17", datatype=XSD.date)))
    g.add((ontology_uri, DCTERMS.issued, Literal("2018-10-25", datatype=XSD.date)))
    g.add((ontology_uri, DCTERMS.title, Literal("Concrete Damage Ontology", lang="en")))
    g.add((ontology_uri, VANN.preferredNamespacePrefix, Literal("cdo")))
    g.add((ontology_uri, VANN.preferredNamespaceUri, Literal("https://w3id.org/damagemodels/cdo#")))

    # Creator metadata as a blank node
    creator = BNode()
    g.add((ontology_uri, DCTERMS.creator, creator))
    g.add((creator, RDF.type, FOAF.Person))
    g.add((creator, FOAF.name, Literal("Vedant Dalvi")))

    #################################################################
    # Property Definitions
    #################################################################
    g.add((CDO.hasCoordinates, RDF.type, OWL.DatatypeProperty))
    g.add((CDO.hasCoordinates, RDFS.domain, DOT.ClassifiedDamage))
    g.add((CDO.hasCoordinates, RDFS.range, XSD.string))
    g.add((CDO.hasCoordinates, RDFS.label, Literal("has coordinates", lang="en")))

    g.add((CDO.isStructural, RDF.type, OWL.DatatypeProperty))
    g.add((CDO.isStructural, RDFS.domain, DOT.ClassifiedDamage))
    g.add((CDO.isStructural, RDFS.range, XSD.boolean))
    g.add((CDO.isStructural, RDFS.label, Literal("is structural", lang="en")))

    g.add((CDO.damageLocatedOn, RDF.type, OWL.ObjectProperty))
    g.add((CDO.damageLocatedOn, RDFS.domain, DOT.ClassifiedDamage))
    g.add((CDO.damageLocatedOn, RDFS.range, CDO.BuildingElement))
    g.add((CDO.damageLocatedOn, RDFS.label, Literal("damage located on", lang="en")))

    g.add((CDO.ifcGlobalId, RDF.type, OWL.DatatypeProperty))
    g.add((CDO.ifcGlobalId, RDFS.domain, CDO.BuildingElement))
    g.add((CDO.ifcGlobalId, RDFS.range, XSD.string))
    g.add((CDO.ifcGlobalId, RDFS.label, Literal("IFC GlobalId", lang="en")))
    g.add((CDO.ifcGlobalId, RDFS.comment, Literal("Links a building element to its IFC GUID.", lang="en")))

    #################################################################
    # Building Element Classes
    #################################################################
    g.add((CDO.BuildingElement, RDF.type, OWL.Class))
    g.add((CDO.BuildingElement, RDFS.label, Literal("Building Element", lang="en")))

    g.add((CDO.Beam, RDF.type, OWL.Class))
    g.add((CDO.Beam, RDFS.subClassOf, CDO.BuildingElement))
    g.add((CDO.Beam, RDFS.label, Literal("Beam", lang="en")))
    g.add((CDO.Beam, OWL.equivalentClass, IFC.IfcBeam))

    g.add((CDO.Column, RDF.type, OWL.Class))
    g.add((CDO.Column, RDFS.subClassOf, CDO.BuildingElement))
    g.add((CDO.Column, RDFS.label, Literal("Column", lang="en")))
    g.add((CDO.Column, OWL.equivalentClass, IFC.IfcColumn))

    g.add((CDO.Wall, RDF.type, OWL.Class))
    g.add((CDO.Wall, RDFS.subClassOf, CDO.BuildingElement))
    g.add((CDO.Wall, RDFS.label, Literal("Wall", lang="en")))
    g.add((CDO.Wall, OWL.equivalentClass, IFC.IfcWall))

    g.add((CDO.Slab, RDF.type, OWL.Class))
    g.add((CDO.Slab, RDFS.subClassOf, CDO.BuildingElement))
    g.add((CDO.Slab, RDFS.label, Literal("Slab", lang="en")))
    g.add((CDO.Slab, OWL.equivalentClass, IFC.IfcSlab))

    #################################################################
    # Building Elements and Damage Instances from JSON
    #################################################################
    element_counter = 1
    damage_counter = 1

    for result in data["inference_results"]:
        for det in result["detections"]:
            damage_class = det["damage_class"]
            params = det["damage_parameters"]
            coords = det["damage_location_3D"]
            ifc_element = det["ifc_element"]
            ifc_guid = det["ifc_guid"]

            # Building Element instance
            elem_uri = EX[f"{ifc_element.lower()}_{element_counter:03d}"]
            g.add((elem_uri, RDF.type, CDO[ifc_element]))
            g.add((elem_uri, RDFS.label, Literal(f"{ifc_element} instance {element_counter}")))
            g.add((elem_uri, CDO.ifcGlobalId, Literal(ifc_guid, datatype=XSD.string)))

            # Damage instance
            damage_uri = EX[f"{damage_class}_{damage_counter:03d}"]
            g.add((damage_uri, RDF.type, CDO[damage_class.capitalize()]))

            # Add parameters
            for k, v in params.items():
                if isinstance(v, (int, float)):
                    g.add((damage_uri, CDO[k], Literal(v, datatype=XSD.decimal)))
                else:
                    g.add((damage_uri, CDO[k], Literal(v, datatype=XSD.string)))

            # Add coordinates
            coord_str = "POLYGON((" + ", ".join([f"{p['x']} {p['y']} {p['z']}" for p in coords]) + "))"
            g.add((damage_uri, CDO.hasCoordinates, Literal(coord_str, datatype=XSD.string)))

            # isStructural heuristic
            is_structural = params.get("severity_level", "").lower() in ["medium", "high"]
            g.add((damage_uri, CDO.isStructural, Literal(is_structural, datatype=XSD.boolean)))

            # Link to element
            g.add((damage_uri, CDO.damageLocatedOn, elem_uri))

            element_counter += 1
            damage_counter += 1

    # Serialize RDF to TTL
    g.serialize(rdf_output, format="turtle")
    print(f"Full RDF ontology saved to {rdf_output}")


if __name__ == "__main__":
    json_to_rdf("inference_data.json", "ontology_output.ttl")
