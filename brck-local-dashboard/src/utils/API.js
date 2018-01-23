var request = require('superagent');


const BASE_URL = 'http://localhost:9009/api/v1';

const TIMEOUT = {
    response: 3000,
    deadline: 5000
};

const Connector = {
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
            .end(cb)
    }
}

export default Connector;