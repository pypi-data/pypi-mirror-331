from ua_parser import user_agent_parser

def parse_user_agent(ua_string):
    parsed_ua = user_agent_parser.Parse(ua_string)
    return {
        "browser_family": parsed_ua['user_agent']['family'],
        "browser_version": f"{parsed_ua['user_agent']['major']}.{parsed_ua['user_agent']['minor']}.{parsed_ua['user_agent']['patch']}",
        "os_family": parsed_ua['os']['family'],
        "os_version": f"{parsed_ua['os']['major']}.{parsed_ua['os']['minor']}.{parsed_ua['os']['patch']}",
        "device_family": parsed_ua['device']['family'],
        "device_brand": parsed_ua['device']['brand'],
        "device_model": parsed_ua['device']['model'],
    }
