import Auth from './Auth';

var request = require('superagent');

const BASE_URL = 'http://local.brck.com/api/v1';
const AUTH_HEADER = 'X-Auth-Token-Key';

const TIMEOUT = {
    response: 10000,
    deadline: 15000
};

const API = {
    'handle_error': (code) => {
        console.log("Handing Error: ", code);
        if (code === 401) {
            Auth.clearCredentials();
            window.location = '/login';
        }
    },
    'ping': function(cb){
        request.get(BASE_URL + '/ping')
            .type('json')
            .accept('json')
            .timeout(TIMEOUT)
            .end(cb);
    },
    'auth': (payload, cb) => {
        request.post(BASE_URL + '/auth')
            .send(payload)
            .timeout(TIMEOUT)
            .end(cb);
    },
    'get_system': function(cb) {
        request.get(BASE_URL + '/system')
            .type('json')
            .accept('json')
            .set(AUTH_HEADER, Auth.getToken())
            .timeout(TIMEOUT)
            .end(cb);
    },
    'get_sim_connections': function(cb) {
        request.get(BASE_URL + '/networks/sim/')
            .type('json')
            .accept('json')
            .set(AUTH_HEADER, Auth.getToken())
            .timeout(TIMEOUT)
            .end(cb);
    },
    'configure_sim_connection': function(sim_id, payload, cb) {
        request.patch(BASE_URL + '/networks/sim/' + sim_id)
            .type('json')
            .accept('json')
            .send(payload)
            .set(AUTH_HEADER, Auth.getToken())
            .timeout(TIMEOUT)
            .end(cb);
    }
}

export default API;