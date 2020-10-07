# SSOFixer

The SSOFixer macro does 2 things to fix what is wrong with the current SSO Permission Set and Attachment implementation.

## Support for a validatable Inline Policy Document

The default implementation of the SSO permission set only lets you pass a JSON string for the inline policy, not an actual JSON object. This means that it can't be validated and looks unwieldy. With the new `PolicyDocument` property you can instead provide an inline policy that can be parsed. The provided cfn-lint config will recognise this as a PolicyDocument object from `AWS::IAM::Policy` and if you use the included [SSOPolicy rule](cfn-lint/rules/SSOPolicy.py) cfn-lint will validate it the same as a PolicyDocument in an IAM policy.

```yaml
  PermissionSet:
    Type: AWS::SSO::PermissionSet
    Properties:
      InstanceArn: 'arn:aws:sso:::instance/ssoins-instanceId'
      Name: 'PermissionSet'
      Description: 'This is a sample permission set.'
      ManagedPolicies:
        - 'arn:aws:iam::aws:policy/AdministratorAccess'
      PolicyDocument:
        Version: 2012-10-17
        Statement:
        - Effect: Allow
          Action: '*'
          Resource: '*'
```

After submitting to CloudFormation, the document will be converted to a string and filled into the `InlinePolicy` property.

### Using cfn-lint

To validate with cfn-lint using the custom rule you can use the below command when run from this directory:

```bash
$ cfn-lint --override-spec cfn-lint/override-file.json --append-rules cfn-lint/rules --template example-policy.yml && echo "All good"
All good
```

## Support for a lookup table for a PrincipalId

The default implementation of the SSO Assignment means you have to use internal ids when assigning a user or group to a permission set and account combination. With the new `PrincipalName` property you can instead use the name and using a lookup table (stored in S3) it will then transform this into the PrincipalId required by the CloudFormation.

```yaml
  Assignment:
    Type: AWS::SSO::Assignment
    Properties:
      InstanceArn: 'arn:aws:sso:::instance/ssoins-instanceId'
      PermissionSetArn: !GetAtt PermissionSet.PermissionSetArn
      TargetId: 'accountId'
      TargetType: 'AWS_ACCOUNT'
      PrincipalType: 'USER'
      PrincipalName: 'Arjen Schwarz'
```

## Deployment

As the source code is in a separate file, you will need to package the CloudFormation template first. You can do so with the below command, where you replace `${ARTIFACTS_BUCKET}` with the S3 bucket you wish to use for temporary storing the zipped file.

```bash
aws cloudformation package --template-file ./macro-template.yml --s3-bucket ${ARTIFACTS_BUCKET} --output-template-file packaged-macro.yml
```

After this you can then deploy the packaged-macro.yml CloudFormation template using a regular CloudFormation deployment. From the CLI this would mean:

```bash
aws cloudformation deploy --template-file ./packaged-macro.yml --stack-name Macro-SSOFixer --capabilities CAPABILITY_IAM --parameter-overrides BucketName=mybucket LookupTablePrefix=ssolookuptable.json
```

The parameters used in this example assume that your lookup table is stored in `s3://mybucket/ssolookuptable.json`. If you don't provide parameters for the lookup table, it will not be used and no IAM permissions for access to an S3 bucket will be created.

## Development

Feel free to add extra functionality, or fix my mistakes, and create a PR. Please ensure all tests run correctly before creating the PR.

Tests require [moto](https://github.com/spulec/moto) to be installed, at least the S3 module. See the linked GitHub page for installation.

```bash
$ python3 test.py
.....
----------------------------------------------------------------------
Ran 5 tests in 0.332s

OK
```
