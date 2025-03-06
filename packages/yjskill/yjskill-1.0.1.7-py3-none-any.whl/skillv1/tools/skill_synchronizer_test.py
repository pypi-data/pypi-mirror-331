import unittest

from .skill_synchronizer import SyncSkillKind


class TestSkillSynchronizer(unittest.TestCase):
    """
    Test Skill Synchronizer
    """

    def __init__(self, methodName='runTest'):
        super().__init__(methodName=methodName)

    def test_sync_kind(self):
        """
        test sync kind
        """

        kind = "Edge"
        sync_kind = SyncSkillKind[kind]
        print(sync_kind == SyncSkillKind.Edge)

    def test_map_len(self):
        """
        test map len
        """

        sync_model_result = {}
        sync_model_result["device_01"] = {
            "ID": "1234567890"
        }
        sync_model_result["device_02"] = {
            "ID": "1234567890"
        }
        print(f'len(sync_model_result) = {len(sync_model_result)}')


def suite():
    """
    test suite
    """

    suite = unittest.TestSuite()
    # suite.addTest(TestSkillSynchronizer('test_sync_kind'))
    suite.addTest(TestSkillSynchronizer('test_map_len'))
    return suite


if __name__ == '__main__':
    print('starting tests...')
    unittest.main(defaultTest='suite')
