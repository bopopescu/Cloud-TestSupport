SETTINGS = eval(open('config.json', 'r').read())
print SETTINGS
print SETTINGS['APP_NAME']
print SETTINGS['BASE_AMI']
print SETTINGS['AWS_ACCESS_KEY']
print SETTINGS['AWS_SECRET_KEY']
print SETTINGS['region_name']
print SETTINGS['instance_type']
print SETTINGS['placement']
print SETTINGS['key_name']
print SETTINGS['security_groups']
print SETTINGS['shutdown_behavior']
