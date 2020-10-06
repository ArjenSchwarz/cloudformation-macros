import boto3
from moto import mock_s3
import mock
import os
import macro
import json
import unittest


class TestStringMethods(unittest.TestCase):
    def testNonSSOPassedThrough(self):
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

    def testSSOPolicyDocumentTranslated(self):
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        event["fragment"] = {"Resources": {"PermSet": {
            "Type": "AWS::SSO::PermissionSet", "Properties": { "PolicyDocument": { "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*"
                }
            ]}}}}}
        expected_policy = "{\"Version\": \"2012-10-17\", \"Statement\": [{\"Effect\": \"Allow\", \"Action\": \"*\", \"Resource\": \"*\"}]}"
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["PermSet"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(
            fragment["Resources"]["PermSet"]["Type"], "AWS::SSO::PermissionSet")
        properties_totest = fragment["Resources"]["PermSet"]["Properties"]
        self.assertEqual(properties_totest["InlinePolicy"], expected_policy)
        self.assertRaises(KeyError, lambda: properties_totest["PolicyDocument"])

    def testSSOPolicyDocumentNotPresent(self):
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        event["fragment"] = {"Resources": {"PermSet": {
            "Type": "AWS::SSO::PermissionSet", "Properties": { "InlinePolicy": "just a string" }}}}
        expected_policy = "just a string"
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["PermSet"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(
            fragment["Resources"]["PermSet"]["Type"], "AWS::SSO::PermissionSet")
        properties_totest = fragment["Resources"]["PermSet"]["Properties"]
        self.assertEqual(properties_totest["InlinePolicy"], expected_policy)
        self.assertRaises(KeyError, lambda: properties_totest["PolicyDocument"])

    @mock_s3
    @mock.patch.dict(os.environ, {"BUCKET_NAME": "testbucket", "LOOKUPTABLE_PREFIX": "lookuptable.json"})
    def testSSOPrincipalName(self):
        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket='testbucket')
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.put_object(Bucket='testbucket', Key="lookuptable.json", Body="{\"My Name\":\"abcdef-123456\"}")
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        event["fragment"] = {"Resources": {"Assmnt": {
            "Type": "AWS::SSO::Assignment", "Properties": { "PrincipalName": "My Name" }}}}
        expected_policy = "abcdef-123456"
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["Assmnt"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(
            fragment["Resources"]["Assmnt"]["Type"], "AWS::SSO::Assignment")
        properties_totest = fragment["Resources"]["Assmnt"]["Properties"]
        self.assertEqual(properties_totest["PrincipalId"], expected_policy)
        self.assertRaises(KeyError, lambda: properties_totest["PrincipalName"])

    @mock_s3
    @mock.patch.dict(os.environ, {"BUCKET_NAME": "", "LOOKUPTABLE_PREFIX": ""})
    def testSSOPrincipalNameNoLookuptable(self):
        conn = boto3.resource('s3', region_name='us-east-1')
        conn.create_bucket(Bucket='testbucket')
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.put_object(Bucket='testbucket', Key="lookuptable.json", Body="{\"My Name\":\"abcdef-123456\"}")
        event = {}
        event["region"] = "ap-southeast-2"
        event["requestId"] = "testRequest"
        event["fragment"] = {"Resources": {"Assmnt": {
            "Type": "AWS::SSO::Assignment", "Properties": { "PrincipalName": "My Name" }}}}
        expected_policy = "abcdef-123456"
        result = macro.handler(event, None)
        fragment = result["fragment"]
        expected_resources = ["Assmnt"]
        expected_resources.sort()
        actual_resources = list(fragment["Resources"].keys())
        actual_resources.sort()
        self.assertEqual(expected_resources, actual_resources)
        self.assertEqual(
            fragment["Resources"]["Assmnt"]["Type"], "AWS::SSO::Assignment")
        properties_totest = fragment["Resources"]["Assmnt"]["Properties"]
        self.assertEqual(properties_totest["PrincipalName"], "My Name")
        self.assertRaises(KeyError, lambda: properties_totest["PrincipalId"])

if __name__ == '__main__':
    unittest.main()
