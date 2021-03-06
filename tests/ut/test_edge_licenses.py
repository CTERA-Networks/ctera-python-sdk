from unittest import mock

from cterasdk import exception
from cterasdk.edge import licenses
from cterasdk.edge.enum import License
from tests.ut import base_edge


class TestEdgeLicenses(base_edge.BaseEdgeTest):

    def test_edge_get_active_licenses(self):
        actual_licenses = ['NA', 'vGateway8', 'vGateway', 'vGateway32', 'vGateway64', 'vGateway128']
        expected_licenses = ['NA', 'EV8', 'EV16', 'EV32', 'EV64', 'EV128']
        for index, actual_license in enumerate(actual_licenses):
            self._filer.get = mock.MagicMock(return_value=actual_license)
            ret = licenses.Licenses(self._filer).get()
            self._filer.get.assert_called_once_with('/config/device/activeLicenseType')
            self.assertEqual(ret, expected_licenses[index])

    def test_apply_license(self):
        self._init_filer()
        ctera_licenses = ['vGateway8', 'vGateway', 'vGateway32', 'vGateway64', 'vGateway128']
        calls = [mock.call('/config/device/activeLicenseType', ctera_license) for ctera_license in ctera_licenses]
        licenses.Licenses(self._filer).apply(License.EV8)
        licenses.Licenses(self._filer).apply(License.EV16)
        licenses.Licenses(self._filer).apply(License.EV32)
        licenses.Licenses(self._filer).apply(License.EV64)
        licenses.Licenses(self._filer).apply(License.EV128)
        self._filer.put.assert_has_calls(calls)

    def test_apply_license_raise_input_error(self):
        with self.assertRaises(exception.InputError) as error:
            licenses.Licenses(self._filer).apply('Expected Failure')
        self.assertEqual('Invalid license type', error.exception.message)
