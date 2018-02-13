import Auth from './Auth';

var request = require('superagent');

const BASE_URL = 'http://local.brck.com/api/v1';
const AUTH_HEADER = 'X-Auth-Token-Key';

const TIMEOUT = {
    response: 10000,
    deadline: 15000
};

const LONG_TIMEOUT = {
    response: 20000,
    deadline: 25000
}


const handleError = (err) => {
    console.log(err);
    if (err) {
        if (err.status_code === 401) {
            Auth.clearCredentials();
            window.location = '/login';
        } else if (err.status_code === undefined) {
            window.location = '/';
        }
    }
}


const API = {
    getAuthHeaders: () => {
        return {[AUTH_HEADER]: Auth.getToken()};
    },
    ping: function(cb){
        request.get(BASE_URL + '/ping')
            .type('json')
            .accept('json')
            .timeout(TIMEOUT)
            .end(cb);
    },
    auth: (payload, cb) => {
        request.post(BASE_URL + '/auth')
            .send(payload)
            .timeout(TIMEOUT)
            .on('error', handleError)
            .then(cb);
    },
    change_password: (payload, cb) => {
        request.patch(BASE_URL + '/auth/password')
            .type('json')
            .set(AUTH_HEADER, Auth.getToken())
            .send(payload)
            .timeout(TIMEOUT)
            .on('error', handleError)
            .then(cb);
    },
    get_system: function(cb) {
        request.get(BASE_URL + '/system')
            .type('json')
            .accept('json')
            .set(AUTH_HEADER, Auth.getToken())
            .timeout(TIMEOUT)
            .on('error', handleError)
            .then(cb);
    },
    get_power_config: function(cb) {
        request.get(BASE_URL + '/power')
            .type('json')
            .accept('json')
            .set(AUTH_HEADER, Auth.getToken())
            .timeout(TIMEOUT)
            .on('error', handleError)
            .then(cb);
    },
    configure_power: function(payload, cb) {
        request.patch(BASE_URL + '/power')
            .type('json')
            .accept('json')
            .send(payload)
            .set(AUTH_HEADER, Auth.getToken())
            .timeout(LONG_TIMEOUT)
            .on('error', handleError)
            .then(cb);
    },
    get_sim_connections: function(cb) {
        request.get(BASE_URL + '/networks/sim/')
            .type('json')
            .accept('json')
            .set(AUTH_HEADER, Auth.getToken())
            .timeout(TIMEOUT)
            .on('error', handleError)
            .then(cb);
    },
    configure_sim_connection: function(sim_id, payload, cb) {
        request.patch(BASE_URL + '/networks/sim/' + sim_id)
            .type('json')
            .accept('json')
            .send(payload)
            .set(AUTH_HEADER, Auth.getToken())
            .timeout(LONG_TIMEOUT)
            .on('error', handleError)
            .then(cb);
    }
}

export default API;