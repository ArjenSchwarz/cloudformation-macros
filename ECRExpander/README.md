# ECRExpander

A CloudFormation Macro for expanding ECR entries.

## Usage

This Macro, using the `IgnoreMe::ECR::Repository` type, allows a more concise listing of multiple ECR repositories. For each entry in the `Repositories` property, it will generate a `AWS::ECR::Repository` CloudFormation object that as its `RepositoryName` will have the listed name. Aside from the new `Repositories`, and the generated `RepositoryName` property, this Macro allows all the same properties as `AWS::ECR::Repository` so you can group multiple repositories with, for example, the same `LifecyclePolicy` or `RepositoryPolicyText`.

The below example shows how you can use this similar to the regular `AWS::ECR::Repository`, but with two repositories instead of just one.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: ECR Repositories
Resources:
  Repos:
    Type: IgnoreMe::ECR::Repository
    Properties:
      Repositories:
        - test-repository
        - second-test-repository
      RepositoryPolicyText:
        Version: "2012-10-17"
        Statement:
          -
            Sid: AllowPushPull
            Effect: Allow
            Principal:
              AWS:
                - "arn:aws:iam::123456789012:user/Bob"
                - "arn:aws:iam::123456789012:user/Alice"
            Action:
              - "ecr:GetDownloadUrlForLayer"
              - "ecr:BatchGetImage"
              - "ecr:BatchCheckLayerAvailability"
              - "ecr:PutImage"
              - "ecr:InitiateLayerUpload"
              - "ecr:UploadLayerPart"
              - "ecr:CompleteLayerUpload"

Transform:
  - ECRExpander
```

After being parsed by the Macro, the template turns into this:

```yaml
AWSTemplateFormatVersion: 2010-09-09
Description: ECR Repositories
Resources:
  testRepository:
    Type: AWS::ECR::Repository
    Properties:
      RepositoryName: test-repository
      RepositoryPolicyText:
        Version: "2012-10-17"
        Statement:
          -
            Sid: AllowPushPull
            Effect: Allow
            Principal:
              AWS:
                - "arn:aws:iam::123456789012:user/Bob"
                - "arn:aws:iam::123456789012:user/Alice"
            Action:
              - "ecr:GetDownloadUrlForLayer"
              - "ecr:BatchGetImage"
              - "ecr:BatchCheckLayerAvailability"
              - "ecr:PutImage"
              - "ecr:InitiateLayerUpload"
              - "ecr:UploadLayerPart"
              - "ecr:CompleteLayerUpload"

  secondTestRepository:
    Type: AWS::ECR::Repository
    Properties:
      RepositoryName: second-test-repository
      RepositoryPolicyText:
        Version: "2012-10-17"
        Statement:
          -
            Sid: AllowPushPull
            Effect: Allow
            Principal:
              AWS:
                - "arn:aws:iam::123456789012:user/Bob"
                - "arn:aws:iam::123456789012:user/Alice"
            Action:
              - "ecr:GetDownloadUrlForLayer"
              - "ecr:BatchGetImage"
              - "ecr:BatchCheckLayerAvailability"
              - "ecr:PutImage"
              - "ecr:InitiateLayerUpload"
              - "ecr:UploadLayerPart"
              - "ecr:CompleteLayerUpload"
```

## Installation

As the source code is in a separate file, you will need to package the CloudFormation template first. You can do so with the below command, where you replace `${ARTEFACTS_BUCKET}` with the S3 bucket you wish to use for temporary storing the zipped file.

```bash
aws cloudformation package --template-file ./macro-template.yml --s3-bucket ${ARTEFACTS_BUCKET} --output-template-file packaged-macro.yml
```

After this you can then deploy the packaged-macro.yml CloudFormation template using a regular CloudFormation deployment. From the CLI this would mean:

```bash
aws cloudformation deploy --template-file ./packaged-macro.yml --stack-name Macro-ECRExpander --capabilities CAPABILITY_IAM
```

## cfn-lint

If you use [cfn-lint](https://github.com/aws-cloudformation/cfn-python-lint) to lint your templates, you can use the override configuration in the cfn-lint directory to make it understand the changes.
