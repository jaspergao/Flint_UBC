
aws emr create-cluster --name Meiji-test_1 \
                       --region us-west-1 \
                       --configurations file://configurations.json \
                       --use-default-roles \
                       --auto-scaling-role EMR_AutoScaling_DefaultRole \
                       --release-label emr-5.29.0 \
                       --instance-groups InstanceGroupType=MASTER,InstanceCount=1,InstanceType=c4.2xlarge,BidPrice=OnDemandPrice InstanceGroupType=CORE,InstanceCount=64,InstanceType=c4.2xlarge,BidPrice=OnDemandPrice \
                       --applications Name=Spark Name=Hadoop \
                       --ec2-attributes KeyName="jasperMohnLab",SubnetId="subnet-05fb2a63",EmrManagedMasterSecurityGroup="sg-0c17a6cf02648e9ad",EmrManagedSlaveSecurityGroup="sg-0e1b3fc876b5bf30c"\
                       --visible-to-all-users \
                       --bootstrap-actions Path="s3://flint-implementation/flint-master/amazon-emr/bootstrap_actions/AN2-setup.sh" \
                       --enable-debugging \
                       --log-uri 's3://aws-logs-970230676797-us-west-1/elasticmapreduce/' \
                       --ebs-root-volume-size "10" 