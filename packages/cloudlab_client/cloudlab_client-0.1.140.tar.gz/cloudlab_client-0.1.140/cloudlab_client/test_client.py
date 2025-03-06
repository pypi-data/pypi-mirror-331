import os
import logging
import unittest

from .client import CloudlabClient


log = logging.getLogger(__name__)


# class TestCloudlabClient(unittest.TestCase):

    # Uncomment to test
    # Must provide username / password

    # def setUp(self) -> None:
    #     self.cloudlab_client = CloudlabClient()
    #     username = os.environ.get("CLOUDLAB_USERNAME")
    #     password = os.environ.get("CLOUDLAB_PASSWORD")
    #     self.cloudlab_client.login(username, password)
    #     cookie = self.cloudlab_client.driver.get_cookie("NewLoginCookie")
    #     self.assertIsNotNone(cookie, "Login failed, cookie not set...")
    #     return super().setUp()


    # def test_experiment_calls(self):
    #     # # List
    #     experiments = self.cloudlab_client.experiment_list()
    #     log.info(experiments)
    #     self.assertTrue(experiments, "List failed, no experiments found...")
    #     print(self.cloudlab_client.driver.get_cookies())

    #     # # Get nodes
    #     nodes = self.cloudlab_client.experiment_list_nodes(
    #         name=experiments[0].name)
    #     log.info(nodes)
    #     self.assertTrue(nodes, "List nodes failed, no nodes found for"
    #                            " experiment...")

    #     # Request Extension
    #     reason = ("Running an experiment for research with advisor Asaf Cidon."
    #               " Research related to network performance and need two"
    #               " machines to test properly.")

    #     self.cloudlab_client.experiment_extend("udp-test", reason)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
