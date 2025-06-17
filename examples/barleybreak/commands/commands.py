import config.settings as config

whook_endpoint = config.ip_whook_endpoint
commands = [
              {'COMMAND': 'move', 'TITLE': 'пятнашки','PARAMS': 'text', 'EVENT_COMMAND_ADD': whook_endpoint}            
           ]
