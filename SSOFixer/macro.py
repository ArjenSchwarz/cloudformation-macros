import json
import boto3
import os

def handler(event, context):
    macro_response = {
        "requestId": event["requestId"],
        "status": "success"
    }
    # Globals
    fragment = event['fragment']
    result = fragment

    lookups = False
    if 'BUCKET_NAME' in os.environ and 'LOOKUPTABLE_PREFIX' in os.environ:
        bucketname = os.environ['BUCKET_NAME']
        lookuptableprefix = os.environ['LOOKUPTABLE_PREFIX']
        if bucketname != "" and lookuptableprefix != "":
            s3 = boto3.resource('s3')
            key = "lookuptable.json"
            obj = s3.Object(bucketname, lookuptableprefix)
            lookupstring = obj.get()['Body'].read().decode('utf-8')
            lookupdict = json.loads(lookupstring)
            lookups = True

    for resource in list(fragment["Resources"].keys()):
        # Turn Permission Set PolicyDocument into InlinePolicy
        if fragment['Resources'][resource]['Type'] == 'AWS::SSO::PermissionSet':
            if "PolicyDocument" in list(fragment['Resources'][resource]["Properties"]):
                policy = json.dumps(fragment['Resources'][resource]['Properties']['PolicyDocument'])
                result['Resources'][resource]['Properties']['InlinePolicy'] = policy
                result['Resources'][resource]['Properties'].pop('PolicyDocument')
        if fragment['Resources'][resource]['Type'] == 'AWS::SSO::Assignment':
            if lookups == True and "PrincipalName" in list(fragment['Resources'][resource]["Properties"]):
                result['Resources'][resource]['Properties']['PrincipalId'] = lookupdict[fragment['Resources'][resource]["Properties"]["PrincipalName"]]
                result['Resources'][resource]['Properties'].pop('PrincipalName')

    macro_response['fragment'] = result
    return macro_response
