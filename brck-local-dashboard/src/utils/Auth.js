const STORE_KEY = '_apiKey';

const Auth = {
    isAuthenticated: () => {
        return localStorage.getItem(STORE_KEY) !== null;
    },
    storeCredentials: (apiKey) => {
        localStorage.setItem(STORE_KEY, apiKey);
    },
    getToken: () => {
        return localStorage.getItem(STORE_KEY);
    },
    clearCredentials: () => {
        localStorage.removeItem(STORE_KEY);
    }

}

export default Auth;