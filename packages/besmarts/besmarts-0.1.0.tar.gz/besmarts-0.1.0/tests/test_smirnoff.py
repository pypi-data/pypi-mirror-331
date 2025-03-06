

from besmarts.mechanics import smirnoff_xml, smirnoff_models
from besmarts.perception import perception_rdkit

pcp = perception_rdkit.perception_model_rdkit()

xml = smirnoff_xml.smirnoff_xml_read("./openff-2.1.0.offxml")
smirnoff_xml.smirnoff_xml_write(xml, "test.offxml")
xml = smirnoff_xml.smirnoff_xml_read("test.offxml")
smirnoff_xml.smirnoff_xml_write(xml, "test.offxml")

csys = smirnoff_models.smirnoff_load("./openff-2.1.0.offxml", pcp)
smirnoff_models.smirnoff_write_version_0p3(csys, "test2.offxml")

csys = smirnoff_models.smirnoff_load("./test2.offxml", pcp)
smirnoff_models.smirnoff_write_version_0p3(csys, "test3.offxml")
