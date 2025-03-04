from unittest import TestCase
from lxml import etree
from pnb.mcl.metamodel import standard
from pnb.mcl.io.xml import XmlExporter, XmlImporter
from pnb.mcl.test.examples import ex_1


class Test_XmlImporter_ex_1(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_by_uri = ex_1.make_model_by_uri(standard)
        cls.xml_by_uri = {uri: XmlExporter(model).xml for uri, model in cls.model_by_uri.items()}
        cls.xml_loader = staticmethod(lambda uri: cls.xml_by_uri[uri])

    def _test_importer(self, uri):
        messages = []
        importer = XmlImporter(self.xml_loader, uri)
        for model in importer.model_by_uri.values():
            reexported_xml_code = etree.tostring(
                XmlExporter(model).xml, encoding='unicode', pretty_print=True)
            expected_xml_code = etree.tostring(
                self.xml_by_uri[model.uri], encoding='unicode', pretty_print=True)
            if reexported_xml_code != expected_xml_code:
                messages += [
                    f'-------- {model.uri} --------\n\n--- reexported ---\n',
                    reexported_xml_code,
                    '--- expected ---\n',
                    expected_xml_code]
        if messages:
            print(f'\n\n########## {self} ##########\n')
            print('\n'.join(messages))
            self.fail()

    def test_ModelCore(self):
        self._test_importer('http://ModelCore')

    def test_ModelProcess(self):
        self._test_importer('http://ModelProcess')

    def test_ModelInstance1(self):
        self._test_importer('http://ModelInstance1')

    def test_ModelInstance2a(self):
        self._test_importer('http://ModelInstance2a')

    def test_ModelInstance2b(self):
        self._test_importer('http://ModelInstance2b')

    def test_ModelInstance3(self):
        self._test_importer('http://ModelInstance3')
