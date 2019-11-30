#!/bin/bash

STACK_NAME=""
LAMBDA_BUCKET=""

usage() {
  printf "
    Usage: Creates a CF json2csv stack

    Where:
        -s = Stack name - Name of the Cloudformation stack
        -l = Lambda bucket - S3 bucket name where to store the lambda - Will be created if doesn't exist

    "
}


deploy() {

  aws s3 mb s3://"$LAMBDA_BUCKET"

  aws cloudformation package \
    --template template.yml \
    --s3-bucket "$LAMBDA_BUCKET" \
    --output-template-file packaged-template.yml


  aws cloudformation create-stack \
    --stack-name "$STACK_NAME" \
    --template-body file://packaged-template.yml \
    --capabilities CAPABILITY_AUTO_EXPAND

}



while getopts "s:l:" o; do
    case "${o}" in
        s)
            STACK_NAME=${OPTARG}
            ;;
        l)
            LAMBDA_BUCKET=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done

shift $((OPTIND-1))

if [ -z "${STACK_NAME}" ] || [ -z "${LAMBDA_BUCKET}" ]  ; then
    usage
else
    deploy
fi


