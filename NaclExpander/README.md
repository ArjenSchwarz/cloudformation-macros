# NaclExpander

This is an improved version of the Macro in my [CloudFormation Macro workshop](https://github.com/ArjenSchwarz/workshop-cfn-macros), if you wish a step-by-step explanation of how to build something like this I recommend you check that out. The main difference is that the version in the workshop will not be touched, while this one will receive improvements over time.

NaclExpander converts a short form syntax for Network ACLs into the expansive version that CloudFormation expects. It does so by overloading the `AWS::EC2::NetworkAcl` CloudFormation resource into something that contains the versions of the other required resources.

Using that you can write your Network ACLs like this

```yaml
Resources:
  NaclPublic:
    Type: AWS::EC2::NetworkAcl
    Properties:
      VpcId: !Ref VPC
      Inbound:
        - "100,6,allow,0.0.0.0/0,443"
      Outbound:
        - "100,6,allow,0.0.0.0/0,443"
      Association:
        - SubnetA
```

which NaclExpander will then turn into

```yaml
  NaclPublic:
    Type: AWS::EC2::NetworkAcl
    Properties:
      VpcId: !Ref VPC

  SubnetANaclPublic:
    Type: AWS::EC2::SubnetNetworkAclAssociation
    Properties:
      NetworkAclId: !Ref NaclPublic
      SubnetId: !Ref SubnetA

  NaclPublicInbound100:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      Egress: false
      NetworkAclId: !Ref 'NaclPublic'
      Protocol: '6'
      RuleAction: allow
      RuleNumber: '100'
      CidrBlock: '0.0.0.0/0'
      PortRange:
        From: '443'
        To: '443'

  NaclPublicOutbound100:
    Type: AWS::EC2::NetworkAclEntry
    Properties:
      Egress: true
      NetworkAclId: !Ref 'NaclPublic'
      Protocol: '6'
      RuleAction: allow
      RuleNumber: '100'
      CidrBlock: '0.0.0.0/0'
      PortRange:
        From: '443'
        To: '443'
```

The syntax for the Inbound and Outbound entries is:

```
"rule number,protocol,allow/deny,CIDR,ports"
```

It also supports Ref, GetAtt, and other CloudFormation functions. These however need to be passed in as escaped JSON strings, regardless of whether you write your template in JSON or YAML.

Some examples of entries:

```yaml
Resources:
  NaclPublic:
    Type: AWS::EC2::NetworkAcl
    Properties:
      VpcId: !Ref VPC
      Inbound:
        - "100,6,allow,0.0.0.0/0,443" # open port 443 on tcp to the world
        - "110,6,deny,0.0.0.0/0,22-52" # block ports 22 till 52 for everyone
        - "200,6,allow,'{\"Fn::GetAtt\":[\"VPC\",\"CidrBlock\"]}',80" # allow port 80 in the VPC's CidrBlock
        - "300,-1,allow,10.0.0.0/8,-1" # Allow all ports from all protocols from 10.0.0.0/8
```

## Deployment

As the source code is in a separate file, you will need to package the CloudFormation template first. You can do so with the below command, where you replace `${ARTEFACTS_BUCKET}` with the S3 bucket you wish to use for temporary storing the zipped file.

```bash
aws cloudformation package --template-file ./macro-template.yml --s3-bucket ${ARTEFACTS_BUCKET} --output-template-file packaged-macro.yml
```

After this you can then deploy the packaged-macro.yml CloudFormation template using a regular CloudFormation deployment. From the CLI this would mean:

```bash
aws cloudformation deploy --template-file ./packaged-macro.yml --stack-name Macro-NaclExpander --capabilities CAPABILITY_IAM
```

## cfn-lint

If you use [cfn-lint](https://github.com/aws-cloudformation/cfn-python-lint) to lint your templates, you can use the override configuration in the cfn-lint directory to make it understand the changes.

## TODO

* Support for the ICMP codes and types. There are extra requirements when dealing with ICMP according to the spec, so these need to be available.
