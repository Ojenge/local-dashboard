var request = require('superagent');


const BASE_URL = '/api/v1';

const TIMEOUT = {
    response: 3000,
    deadline: 5000
};

const API = {
    'ping': function(cb){
        request.get(BASE_URL + '/ping')
            .type('json')
            .accept('json')
            .timeout(TIMEOUT)
            .end(cb);
    },
    'get_system': function(cb) {
        request.get(BASE_URL + '/system')
            .type('json')
            .accept('json')
            .timeout(TIMEOUT)
            .end(cb);
    },
    'get_sim_connections': function(cb) {
        request.get(BASE_URL + '/networks/sim')
            .type('json')
            .accept('json')
            .timeout(TIMEOUT)
            .end(cb);
    }
}

export default API;