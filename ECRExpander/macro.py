import re

REG = r"(.*?)[-_]([a-zA-Z])"

def camel(match):
    return match.group(1) + match.group(2).upper()

def handler(event, context):
    macro_response = {
        "requestId": event["requestId"],
        "status": "success"
    }
    # Globals
    fragment = event['fragment']
    result = fragment
    for resource in list(fragment["Resources"].keys()):
        if fragment['Resources'][resource]['Type'] == 'IgnoreMe::ECR::Repository':
            tags_to_copy = ""
            lifecycle_to_copy = ""
            policytext_to_copy = ""
            if "Tags" in fragment['Resources'][resource]['Properties']:
                tags_to_copy = fragment['Resources'][resource]['Properties']['Tags']
            if "LifecyclePolicy" in fragment['Resources'][resource]['Properties']:
                lifecycle_to_copy = fragment['Resources'][resource]['Properties']['LifecyclePolicy']
            if "RepositoryPolicyText" in fragment['Resources'][resource]['Properties']:
                policytext_to_copy = fragment['Resources'][resource]['Properties']['RepositoryPolicyText']
            if "Repositories" in fragment['Resources'][resource]['Properties']:
                for repository in fragment['Resources'][resource]['Properties']['Repositories']:
                    resourcename = re.sub(REG, camel, repository, 0)

                    repo_fragment = {
                        "Type": "AWS::ECR::Repository",
                        "Properties": {
                            "RepositoryName": repository
                        }
                    }
                    if tags_to_copy != "":
                        repo_fragment['Properties']['Tags'] = tags_to_copy
                    if lifecycle_to_copy != "":
                        repo_fragment['Properties']['LifecyclePolicy'] = lifecycle_to_copy
                    if policytext_to_copy != "":
                        repo_fragment['Properties']['RepositoryPolicyText'] = policytext_to_copy
                    result['Resources'][resourcename] = repo_fragment

                    outputname = resourcename + "Output"
                    output_frament = {
                        "Value": { "Ref": resourcename },
                        "Export": {
                            "Name": { "Fn::Join": ["-", ["ECR-REPO", resourcename]]}
                        }
                    }
                    if "Outputs" not in result:
                        result['Outputs'] = {}
                    result['Outputs'][outputname] = output_frament
                result['Resources'].pop(resource)


    macro_response['fragment'] = result
    return macro_response
