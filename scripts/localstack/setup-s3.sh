#!/usr/bin/env bash
awslocal s3 mb s3://admin
awslocal s3 mb s3://alert-api-1
awslocal s3 mb s3://alert-api-2
echo -n "" > my_file
awslocal s3 cp my_file s3://alert-api-2/my_file
