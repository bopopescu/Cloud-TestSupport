import logging, sys, os, time, datetime
from boto.ec2.connection import EC2Connection
from boto import regioninfo
from boto import ec2
import boto

BASE_AMI = 'ami-b8400dea'

AWS_ACCESS_KEY = 'AKIAJRUIZQWYMPGNTACQ'
AWS_SECRET_KEY = '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'

ec2conn = boto.ec2.connect_to_region(region_name='ap-southeast-1', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

def get_install_script(pkgName,browser,enve,dirs,mailids=[]):
    return  """<script>
ipconfig /all > c:\ipconfig.txt
@ECHO off
ECHO Hello World!
wget --no-check-certificate -O C:\stestcase.zip "{PKG_URL}"
7za e C:\stestcase.zip -oC:\stest-support\stestcases -y
For %%X in (C:\stest-support\stestcases\*.py) do (python %%X {BROWSER} {ENVE})
copy *.html C:\stest-support\stest-results /y
copy *.log.txt C:\stest-support\stest-results /y
python C:\stest-support\mailtest.py "{MAILID}" {DIRS}
shutdown -s
</script>
""".format(PKG_URL=pkgName,BROWSER=browser,ENVE=enve,DIRS=dirs,MAILID=mailids)

def run_instance(pkgUrl, browser, envrmt, dir_path, mailids):
    instance_type = 't1.micro'
    placement = 'ap-southeast-1a'
    user_data = get_install_script(pkgUrl, browser, envrmt, dir_path, mailids)
    print user_data
    logging.info('Launching Instance %s'%(user_data))
    insts = ec2conn.run_instances(BASE_AMI, key_name='cloud', instance_type=instance_type, placement=placement, user_data=user_data, security_groups=['cloudtest'], instance_initiated_shutdown_behavior = 'terminate')
    logging.info('Instance Launched %s'%(insts))
    return insts
