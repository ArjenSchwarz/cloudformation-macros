import macro
import json
import unittest


class TestStringMethods(unittest.TestCase):
    def testNonEcrPassedThrough(self):
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        event["fragment"] = {"Resources": {"S3Bucket": {
            "Type": "AWS::S3::Bucket"}}}
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["S3Bucket"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(
            fragment["Resources"]["S3Bucket"]["Type"], "AWS::S3::Bucket")

    def testSingleRepoCreatesResource(self):
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        event["fragment"] = {"Resources": {"Repos": {
            "Type": "IgnoreMe::ECR::Repository", "Properties": { "Repositories": ["test_repo"]}}}}
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["testRepo"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(fragment["Resources"]["testRepo"]["Type"], "AWS::ECR::Repository")
        self.assertEqual(fragment["Resources"]["testRepo"]["Properties"]["RepositoryName"], "test_repo")

    def testMultiReposCreateResources(self):
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        event["fragment"] = {"Resources": {"Repos": {
            "Type": "IgnoreMe::ECR::Repository", "Properties": { "Repositories": ["test_repo", "second-repo"]}}}}
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["testRepo", "secondRepo"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(fragment["Resources"]["testRepo"]["Type"], "AWS::ECR::Repository")
        self.assertEqual(fragment["Resources"]["testRepo"]["Properties"]["RepositoryName"], "test_repo")
        self.assertEqual(fragment["Resources"]["secondRepo"]["Type"], "AWS::ECR::Repository")
        self.assertEqual(fragment["Resources"]["secondRepo"]["Properties"]["RepositoryName"], "second-repo")

    def testSingleRepoCreatesOutput(self):
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        event["fragment"] = {"Resources": {"Repos": {
            "Type": "IgnoreMe::ECR::Repository", "Properties": {"Repositories": ["test_repo"]}}}}
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["testRepoOutput"]
        expected_resources.sort()
        actual_resources = list(fragment["Outputs"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(fragment["Resources"]["testRepo"]["Type"], "AWS::ECR::Repository")
        self.assertEqual(fragment["Resources"]["testRepo"]["Properties"]["RepositoryName"], "test_repo")

    def testTagsAreCarriedOver(self):
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        tags = [{"Key": "Environment", "Value": "Test"}]
        event["fragment"] = {"Resources": {"Repos": {
            "Type": "IgnoreMe::ECR::Repository", "Properties": {"Repositories": ["test_repo"],"Tags": tags}}}}
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["testRepo"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(fragment["Resources"]["testRepo"]["Type"], "AWS::ECR::Repository")
        self.assertEqual(fragment["Resources"]["testRepo"]["Properties"]["Tags"], tags)

    def testLifecyclePoliciesAreCarriedOver(self):
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        tags = [{"Key": "Environment", "Value": "Test"}]
        event["fragment"] = {"Resources": {"Repos": {
            "Type": "IgnoreMe::ECR::Repository", "Properties": {"Repositories": ["test_repo"], "LifecyclePolicy": tags}}}}
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["testRepo"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(fragment["Resources"]["testRepo"]["Type"], "AWS::ECR::Repository")
        self.assertEqual(fragment["Resources"]["testRepo"]["Properties"]["LifecyclePolicy"], tags)

    def testPolicyTextsAreCarriedOver(self):
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        tags = [{"Key": "Environment", "Value": "Test"}]
        event["fragment"] = {"Resources": {"Repos": {
            "Type": "IgnoreMe::ECR::Repository", "Properties": {"Repositories": ["test_repo"], "RepositoryPolicyText": tags}}}}
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["testRepo"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(fragment["Resources"]["testRepo"]["Type"], "AWS::ECR::Repository")
        self.assertEqual(fragment["Resources"]["testRepo"]["Properties"]["RepositoryPolicyText"], tags)

if __name__ == '__main__':
    unittest.main()
