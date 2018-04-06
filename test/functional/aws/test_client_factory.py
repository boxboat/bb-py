import unittest
from bb.aws import client_factory


class TestClientFactory(unittest.TestCase):

    def test_asg_client(self):
        asg_client = client_factory.get_asg_client()
        groups = asg_client.describe_auto_scaling_groups()
        self.assertTrue(isinstance(groups['AutoScalingGroups'], list))

    def test_ec2_client(self):
        ec2_client = client_factory.get_ec2_client()
        instances = ec2_client.describe_instances()
        self.assertTrue(isinstance(instances['Reservations'][0]['Instances'], list))

    def test_s3_client(self):
        s3_client = client_factory.get_s3_client()
        buckets = s3_client.list_buckets()
        self.assertTrue(isinstance(buckets['Buckets'], list))


if __name__ == '__main__':
    unittest.main()
