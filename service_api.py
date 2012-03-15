import requests, json
from flask import session

from config import GATEWAY_HOST, GATEWAY_PORT

SERVICE_GATEWAY_BASE_URL = 'http://%s:%d/ion-service' % (GATEWAY_HOST, GATEWAY_PORT)
AGENT_GATEWAY_BASE_URL = 'http://%s:%d/ion-agent' % (GATEWAY_HOST, GATEWAY_PORT)

SERVICE_REQUEST_TEMPLATE = {
    'serviceRequest': {
        'serviceName': '', 
        'serviceOp': '',
        'params': {} # Example -> 'object_name': ['restype', {}] }
    }
}

AGENT_REQUEST_TEMPLATE = {
    "agentRequest": { 
        "agentId": "",
        "agentOp": "",
        "params": { "command": ["AgentCommand", { "command": "" }]}
    }
}

class ServiceApi(object):

    @staticmethod
    def find_resources_by_resource_type(resource_type, user_indentity_id=None):
        if user_indentity_id:
            resources = service_gateway_get('resource_registry', 'find_subject', params={'subject_type': resource_type , 'predicate': 'hasOwner', 'object_id': user_indentity_id})
            return resources
        
        resources = service_gateway_get('resource_type', 'find_resources', params={'restype': resource_type})
        return resources

    @staticmethod
    def enroll_user(marine_facility_id):
        org_id = service_gateway_get('marine_facility_management', 'find_marine_facility_org', params={'marine_facility_id': marine_facility_id})
    
    @staticmethod
    def instrument_agent_start(instrument_device_id):
        instrument_agent_instance_id = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_device_id, 'predicate':'hasAgentInstance'})[0][0]['_id']
        agent_request = service_gateway_get('instrument_management', 'start_instrument_agent_instance', params={'instrument_agent_instance_id': str(instrument_agent_instance_id)})
        
        return agent_request

    @staticmethod
    def instrument_agent_initialize(instrument_device_id):
        # instrument_agent_instance_id = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_device_id, 'predicate':'hasAgentInstance'})[0][0]['_id']
        
        url = '%s/%s/%s' % (AGENT_GATEWAY_BASE_URL, instrument_device_id, "execute_agent")
        
        print '===================================='
        print url
        print '===================================='
        
        print '===================================='
        print payload
        print '===================================='
        
        
        { "command": ["AgentCommand", { "command": "initialize" }]}
        
        agent_request = requests.post(url, data={"payload": json.dumps(payload)})
        
        print '===================================='
        print str(agent_request.content)
        print '===================================='
        
        return str(agent_request.content)
    
    @staticmethod
    def instrument_agent_get_capabilities(instrument_device_id):        
        agent_command = "get_capabilities"
        
        payload = AGENT_REQUEST_TEMPLATE
        payload["agentRequest"]["agentId"] = instrument_device_id
        payload["agentRequest"]["agentOp"] = agent_command
        payload["agentRequest"]["params"] = {} #["command"][1]["command"] = agent_command
        
        url = '%s/%s/%s' % (AGENT_GATEWAY_BASE_URL, instrument_device_id, agent_command)
        
        print '===================================='
        print url
        print '===================================='
        
        print '===================================='
        print payload
        print '===================================='
        
        
        
        agent_request = requests.post(url, data={"payload": json.dumps(payload)})
        
        print '===================================='
        print str(agent_request.content)
        print '===================================='
        
        return str(agent_request.content)
        
    
    @staticmethod
    def instrument_agent_reset(instrument_device_id):        
        agent_command = "execute_agent"

        payload = AGENT_REQUEST_TEMPLATE
        payload["agentRequest"]["agentId"] = instrument_device_id
        payload["agentRequest"]["agentOp"] = agent_command
        payload["agentRequest"]["params"]["command"][1]["command"] = 'reset'

        url = '%s/%s/%s' % (AGENT_GATEWAY_BASE_URL, instrument_device_id, agent_command)

        print '===================================='
        print url


        print '===================================='
        print payload

        agent_request = requests.post(url, data={"payload": json.dumps(payload)})
        params={'user_id': user_id, 'user_info': ['UserInfo', user_info]}
        params = { "command": ["AgentCommand", { "command": "reset" }]}
        return service_gateway_agent_request(instrument_device_id, operation, params)

        print '===================================='
        print str(agent_request.content)

        return str(agent_request.content)


    @staticmethod
    def instrument_agent_capabilities(instrument_device_id):
        params={'subject': instrument_device_id, 'predicate':'hasAgentInstance'}
        instrument_agent_instance_id = service_gateway_get('resource_registry', 'find_objects', params)[0][0]['_id']
        return

    @staticmethod
    def instrument_agent_activate(instrument_device_id):
        params={'subject': instrument_device_id, 'predicate':'hasAgentInstance'}
        instrument_agent_instance_id = service_gateway_get('resource_registry', 'find_objects', params)[0][0]['_id']
        return   
    
    @staticmethod
    def signon_user(certificate):
        params={'certificate': certificate}
        user_id, valid_until, is_registered = service_gateway_post('identity_management', 'signon', params)
    
        # set user id, valid until and is registered info in session
        # TODO might need to address issues that arise with using
        # session to set cookie when web server ends up being a pool
        # of web servers?
        session['user_id'] = user_id
        session['valid_until'] = valid_until
        session['is_registered'] = is_registered
    
        # get roles and stash
        session['roles'] = service_gateway_get('org_management', 'find_all_roles_by_user', params={'user_id': user_id})
    
    @staticmethod
    def find_user_info(user_id):
        params={'user_id': user_id}
        return service_gateway_post('identity_management', 'find_user_info_by_id', params)
    
    @staticmethod
    def create_user_info(user_id, user_info):
        params={'user_id': user_id, 'user_info': ['UserInfo', user_info]}
        return service_gateway_post('identity_management', 'create_user_info', params)
    
    @staticmethod
    def update_user_info(user_info):
        params={'user_info': ['UserInfo', user_info]}
        return service_gateway_get('identity_management', 'update_user_info', params)
    
    @staticmethod
    def find_user_details(user_id):
        user = service_gateway_get('identity_management', 'read_user_identity', params={'user_id': user_id})
        
        if user.has_key('_id'):
            # CREDENTIALS
            user['credentials'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': user_id, 'predicate': 'hasCredentials', 'object_type': 'UserCredentials'})

            # USER INFO
            user['user_info'] = service_gateway_get('identity_management', 'find_user_info_by_id', params={'user_id':user_details['_id']})

            # ROLES
            user['roles'] = service_gateway_get('org_management', 'find_all_roles_by_user', params={'user_id': user_id})

            # POLICIES
            user['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': user_id})

            # OWNED RESOURCES
            user['owned_resources'] = service_gateway_get('resource_registry', 'find_subjects', params={'predicate': 'hasOwner', 'object': user_id, 'id_only': False})
            
            # EVENTS
            user['recent_events'] = []
            user['user_requests'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': user_id, 'predicate': 'hasRequest'})

        return user

    @staticmethod
    def find_observatory(marine_facility_id):
        marine_facility = service_gateway_get('marine_facility_management', 'read_marine_facility', params={'marine_facility_id': marine_facility_id})
        
        if marine_facility.has_key('_id'):

            org_id = service_gateway_get('marine_facility_management', 'find_marine_facility_org', params={'marine_facility_id': marine_facility_id})

            # GENERAL
            marine_facility['data_products'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': org_id, 'predicate': 'hasResource', 'object_type': 'DataProduct'})[0]
            marine_facility['platforms'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': org_id, 'predicate': 'hasResource', 'object_type': 'PlatformDevice'})[0]
            marine_facility['instruments'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': org_id, 'predicate': 'hasResource', 'object_type': 'InstrumentDevice'})[0]

            # ADMINISTRATION            
            marine_facility['participants'] = []
            participants = service_gateway_get('resource_registry', 'find_objects', params={'subject': org_id, 'predicate': 'hasMembership'})[0]
            
            for participant in participants:
                user_info = service_gateway_get('resource_registry', 'find_objects', params={'subject': participant.get('_id'), 'predicate': 'hasInfo'})[0][0]
                marine_facility['participants'].append(user_info)

            marine_facility['policies'] = service_gateway_get('org_management', 'find_org_roles', params={'org_id': org_id})
            
            # SOFTWARE
            marine_facility['instrument_agents'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': org_id, 'predicate': 'hasResource', 'object_type': 'InstrumentAgent'})[0]
            marine_facility['data_process_definitions'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': org_id, 'predicate': 'hasResource', 'object_type': 'DataProcessDefinition'})[0]
            
            # EVENTS
            marine_facility['recent_events'] = []
            marine_facility['user_requests'] = service_gateway_get('org_management', 'find_requests', params={'org_id': org_id})
            
            # DEFINITIONS
            marine_facility['platform_models'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': org_id, 'predicate': 'hasResource', 'object_type': 'PlatformModel'})[0]
            marine_facility['instrument_models'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': org_id, 'predicate': 'hasResource', 'object_type': 'InstrumentModel'})[0]
        
            # FRAMES OF REFERENCE
            marine_facility['subordinates'] = service_gateway_get('marine_facility_management', 'find_subordinate_frames_of_reference', params={'input_resource_id': marine_facility_id})
            
            # OWNER
            marine_facility['owner'] = find_owner(marine_facility_id)

            # POLICIES
            marine_facility['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': marine_facility_id})
        
        return marine_facility
    
    @staticmethod
    def find_platform(platform_device_id):
        platform = service_gateway_get('instrument_management', 'read_platform_device', params={'platform_device_id': platform_device_id})
        
        if platform.has_key('_id'):
            # DEPLOYMENTS
            platform['primary_deployment'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': platform_device_id, 'predicate': 'hasPrimaryDeployment', 'object_type': 'LogicalPlatform', 'id_only': False})[0]
            platform['deployments'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': platform_device_id, 'predicate': 'hasDeployment', 'object_type': 'LogicalPlatform', 'id_only': False})[0]
        
            # ADMINISTRATION        
            platform['instrument_agents'] = service_gateway_get('resource_registry', 'find_resources', params={'restype': 'InstrumentAgent'})
            platform['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': platform_device_id})
        
            # INSTRUMENTS - ERROR WITH PRELOAD DATA
            # logical_platform_id = platform['deployments'][0]['_id']
            # logical_instruments = service_gateway_get('resource_registry', 'find_objects', params={'subject': logical_platform_id, 'predicate': 'hasInstrument', 'id_only': False})[0]
            # platform['instruments'] = service_gateway_get('instrument_management', 'find_instrument_device_by_platform_device', params={'platform_device_id': platform_device_id})
        
            # EVENTS
            platform['recent_events'] = []
            platform['user_requests'] = []
        
            # FRAMES OF REFERENCE
            platform['subordinates'] = service_gateway_get('marine_facility_management', 'find_subordinate_frames_of_reference', params={'input_resource_id': platform['deployments'][0]['_id']})
            platform['superiors'] = service_gateway_get('marine_facility_management', 'find_superior_frames_of_reference', params={'input_resource_id': platform['deployments'][0]['_id']})
            
            # OWNER
            platform['owner'] = find_owner(platform_device_id)

            # POLICIES
            platform['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': platform_device_id})

            # DEFINITIONS TBD
        
        return platform
    
    @staticmethod
    def find_platform_model(platform_model_id):
        platform_model = service_gateway_get('resource_registry', 'read', params={'object_id': platform_model_id})
        
        if platform_model.has_key('_id'):
            # RELATED DEVICES
            platform_model['related_devices'] = service_gateway_get('resource_registry', 'find_subjects', params={'subject_type': 'PlatformDevice', 'predicate': 'hasModel', 'object': platform_model_id, 'id_only': False})[0]
            
            # OWNER
            platform_model['owner'] = find_owner(platform_model_id)

            # POLICIES
            platform_model['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': platform_model_id})
        
        return platform_model

    @staticmethod
    def find_instrument(instrument_device_id):
        instrument = service_gateway_get('instrument_management', 'read_instrument_device', params={'instrument_device_id': instrument_device_id})
        
        if instrument.has_key('_id'):
            # DATA PRODUCTS
            instrument['data_products'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_device_id, 'predicate': 'hasOutputProduct', 'id_only': False})
            for data_product in instrument['data_products']:
                if 'raw' in data_product['name'].lower():
                    instrument['raw_data_product'] = data_product
                elif 'parsed' in data_product['name'].lower():
                    instrument['parsed_data_product'] = data_product

            # LAST UPDATE
            instrument['last_update'] = {}
            if instrument['parsed_data_product']:
                instrument['last_update'] = service_gateway_get('data_product_management', 'get_last_update', params={'data_product_id': instrument['parsed_data_product']['_id']})
                # TODO use last update to populate 'Latest Readings'
                # TODO get visualization
                # instrument['visualization'] = service_gateway_get('visualization', 'get_google_dt', params={'data_product_id': instrument['parsed_data_product']['_id']})

            # DATA
            instrument['data'] = []

            # RELATED MODEL
            instrument['related_model'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_device_id, 'predicate': 'hasModel', 'object_type': 'InstrumentModel', 'id_only': False})[0]
        
            # DEPLOYMENTS
            instrument['primary_deployment'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_device_id, 'predicate': 'hasPrimaryDeployment', 'object_type': 'LogicalInstrument', 'id_only': False})[0]
            instrument['deployments'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_device_id, 'predicate': 'hasDeployment', 'object_type': 'LogicalInstrument', 'id_only': False})[0]
        
            # ADMINISTRATION
            instrument['instrument_agent'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_device_id, 'predicate': 'hasAgentInstance', 'object_type': 'InstrumentAgentInstance', 'id_only': False})[0]
        
            # FRAME OF REFERENCES
            instrument['superiors'] = service_gateway_get('marine_facility_management', 'find_superior_frames_of_reference', params={'input_resource_id': instrument['deployments'][0]["_id"]})
            
            # OWNER
            instrument['owner'] = find_owner(instrument_device_id)
        
            # POLICIES
            instrument['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': instrument_device_id})

        
        return instrument

    @staticmethod
    def find_instrument_model(instrument_model_id):
        instrument_model = service_gateway_get('resource_registry', 'read', params={'object_id': instrument_model_id})
        
        if instrument_model.has_key('_id'):
            # RELATED INSTRUMENTS
            instrument_model['related_instruments'] = service_gateway_get('resource_registry', 'find_subjects', params={'subject_type': 'InstrumentDevice', 'predicate': 'hasModel', 'object': instrument_model_id, 'id_only': False})[0]
        
            # INSTRUMENT AGENTS
            instrument_model['instrument_agents'] = service_gateway_get('resource_registry', 'find_subjects', params={'subject_type': 'InstrumentAgent', 'predicate': 'hasModel', 'object': instrument_model_id, 'id_only': False})[0]
            
            # OWNER
            instrument_model['owner'] = find_owner(instrument_model_id)
        
            # POLICIES
            instrument_model['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': instrument_model_id})
        
        return instrument_model

    @staticmethod
    def find_instrument_agent(instrument_agent_id):
        instrument_agent = service_gateway_get('resource_registry', 'read', params={'object_id': instrument_agent_id})
        
        if instrument_agent.has_key('_id'):            
            # RELATED INSTRUMENT MODELS
            instrument_agent['related_models'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_agent_id, 'predicate': 'hasModel', 'id_only': False})

            # RELATED INSTRUMENT AGENT INSTANCES
            instrument_agent['related_instances'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_agent_id, 'predicate': 'hasInstance', 'id_only': False})

            # RELATED DATA PROCESS DEFINITIONS
            instrument_agent['related_process_definitions'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': instrument_agent_id, 'predicate': 'hasProcessDefinition', 'id_only': False})

            # OWNER
            instrument_agent['owner'] = find_owner(instrument_agent_id)
        
            # POLICIES
            instrument_agent['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': instrument_agent_id})

        return instrument_agent
    
    @staticmethod
    def find_data_process_definition(data_process_definition_id):
        data_process_definition = service_gateway_get('resource_registry', 'read', params={'object_id': data_process_definition_id})
        
        if data_process_definition.has_key('_id'):
            # STREAM DEFINITIONS
            data_process_definition['input_stream_definitions'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': data_process_definition_id, 'predicate': 'hasInputStreamDefinition', 'object_type': 'StreamDefinition', 'id_only': False})
            data_process_definition['output_stream_definitions'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': data_process_definition_id, 'predicate': 'hasStreamDefinition', 'object_type': 'StreamDefinition', 'id_only': False})

            # USED IN
            data_process_definition['data_process'] = service_gateway_get('resource_registry', 'find_objects', params={'subject': data_process_definition_id, 'predicate': 'hasInstance', 'object_type': 'DataProcess', 'id_only': False})
        
            # OWNER
            data_process_definition['owner'] = find_owner(data_process_definition_id)

            # POLICIES
            data_process_definition['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': data_process_definition_id})

        return data_process_definition
    
    @staticmethod
    def find_data_product(data_product_id):
        data_product = service_gateway_get('resource_registry', 'read', params={'object_id': data_product_id})
        
        if data_product.has_key('_id'):            
            # LAST UPDATE
            data_product['last_update'] = service_gateway_get('data_product_management', 'get_last_update', params={'data_product_id': data_product_id})
            # TODO use last update to populate 'Latest Readings'
            # TODO get visualization
            # instrument['visualization'] = service_gateway_get('visualization', 'get_google_dt', params={'data_product_id': data_product_id})
        
            # INPUT PROCESS
            data_product['input_process'] = service_gateway_get('resource_registry', 'find_subjects', params={'subject_type': 'DataProcess', 'predicate': 'hasInputProduct', 'object': data_product_id, 'id_only': False})
        
            # OUTPUT PROCESS
            data_product['output_process'] = service_gateway_get('resource_registry', 'find_subjects', params={'subject_type': 'DataProcess', 'predicate': 'hasOutputProduct', 'object': data_product_id, 'id_only': False})
        
            # FRAME OF REFERENCES TBD

            # OWNER
            data_product['owner'] = find_owner(data_product_id)

            # POLICY
            data_product['policies'] = service_gateway_get('policy_management', 'find_resource_policies', params={'resource_id': data_product_id})

        return data_product
    
    @staticmethod
    def find_frame_of_reference(frame_of_reference_id):
        frame_of_reference = service_gateway_get('resource_registry', 'read', params={'object_id': frame_of_reference_id})
        
        if frame_of_reference.has_key('_id'):
            # SUBORDINATES
            frame_of_reference['subordinates'] = service_gateway_get('marine_facility_management', 'find_subordinate_frames_of_reference', params={'input_resource_id': frame_of_reference_id})

            # SUPERIORS
            frame_of_reference['superiors'] = service_gateway_get('marine_facility_management', 'find_superior_frames_of_reference', params={'input_resource_id': frame_of_reference_id})

            # OWNER
            frame_of_reference['owner'] = find_owner(frame_of_reference_id)
    
    @staticmethod
    def find_by_resource_type(resource_type):
        resources = service_gateway_get('resource_registry', 'find_resources', params={'restype': resource_type})[0]
        
        if resources.has_key('_id'):            
            # OWNER
            resources['owner'] = find_owner(resource_type)

        return resources

    @staticmethod
    def find_owner(resource_id):
        owner_id = service_gateway_get('resource_registry', 'find_objects', params={'subject': resource_id, 'predicate': 'hasOwner'})[0][0]['_id']
        return service_gateway_get('resource_registry', 'find_objects', params={'subject': owner_id, 'predicate': 'hasInfo', 'id_only': False})[0][0]


def build_get_request(service_name, operation_name, params={}):
    url = '%s/%s/%s' % (SERVICE_GATEWAY_BASE_URL, service_name, operation_name)    
    if len(params) > 0:
        param_string = '?'
        for (k, v) in params.iteritems():
            param_string += '%s=%s&' % (k,v)
        url += param_string[:-1]

    pretty_console_log('SERVICE GATEWAY GET URL', url)

    return url

def service_gateway_get(service_name, operation_name, params={}):    
    resp = requests.get(build_get_request(service_name, operation_name, params))
    pretty_console_log('SERVICE GATEWAY GET RESPONSE', resp.content)

    if resp.status_code == 200:
        resp = json.loads(resp.content)

        if type(resp) == dict:
            return resp['data']['GatewayResponse']
        elif type(resp) == list:
            return resp['data']['GatewayResponse'][0]

def build_post_request(service_name, operation_name, params={}):
    url = '%s/%s/%s' % (SERVICE_GATEWAY_BASE_URL, service_name, operation_name)    

    post_data = SERVICE_REQUEST_TEMPLATE
    post_data['serviceRequest']['serviceName'] = service_name   
    post_data['serviceRequest']['serviceOp'] = operation_name   
    if len(params) > 0:
        post_data['serviceRequest']['params'] = params

    # conditionally add user id and expiry to request
    if "user_id" in session:
        post_data['serviceRequest']['requester'] = session['user_id']
        post_data['serviceRequest']['expiry'] = session['valid_until']

    data={'payload': json.dumps(post_data)}

    pretty_console_log('SERVICE GATEWAY POST URL/DATA', url, data)

    return url, data

def service_gateway_post(service_name, operation_name, params={}):
    url, data = build_post_request(service_name, operation_name, params)
    resp = requests.post(url, data)
    pretty_console_log('SERVICE GATEWAY POST RESPONSE', resp.content)

    if resp.status_code == 200:
        resp = json.loads(resp.content)

        if type(resp) == dict:
            return resp['data']['GatewayResponse']
        elif type(resp) == list:
            return resp['data']['GatewayResponse'][0]

def build_agent_request(agent_id, operation_name, params={}):
    url = '%s/%s/%s' % (AGENT_GATEWAY_BASE_URL, agent_id, operation_name)    

    post_data = AGENT_REQUEST_TEMPLATE
    post_data['agentRequest']['agentId'] = agent_id   
    post_data['agentRequest']['agentOp'] = operation_name   
    if len(params) > 0:
        post_data['serviceRequest']['params'] = params

    # conditionally add user id and expiry to request
    if "user_id" in session:
        post_data['agentRequest']['requester'] = session['user_id']
        post_data['agentRequest']['expiry'] = session['valid_until']

    data={'payload': json.dumps(post_data)}

    pretty_console_log('SERVICE GATEWAY AGENT REQUEST POST URL/DATA', url, data)

    return url, data

def service_gateway_post(service_name, operation_name, params={}):
    url, data = build_post_request(service_name, operation_name, params)
    resp = requests.post(url, data)
    pretty_console_log('SERVICE GATEWAY POST RESPONSE', resp.content)

    if resp.status_code == 200:
        resp = json.loads(resp.content)

        if type(resp) == dict:
            return resp['data']['GatewayResponse']
        elif type(resp) == list:
            return resp['data']['GatewayResponse'][0]

def pretty_console_log(label, content, data=None):
    print '\n\n\n'
    print '-------------------------------------------'
    print '%s : %s' % (label, content)
    if data:
        print 'data : %s' % data
    print '-------------------------------------------'
