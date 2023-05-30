#!/bin/bash

environment=$(git branch --show-current)
stackname="test-$environment"
parameterfile="param-$environment.json"
outputfile="output-$environment.yaml"
s3="philipp-2705-templates"
s3_prefix=$stackname

aws cloudformation package --template-file main.yaml \
--s3-bucket $s3 \
--s3-prefix $s3_prefix \
--output-template-file $outputfile

aws cloudformation deploy --capabilities CAPABILITY_NAMED_IAM \
--region us-east-1 \
--template-file $outputfile \
--stack-name $stackname  --parameter-overrides file://$parameterfile \
# --disable-rollback

rm -rf $outputfile

