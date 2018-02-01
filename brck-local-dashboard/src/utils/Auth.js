const STORE_KEY = '_apiKey';

const Auth = {
    isAuthenticated: () => {
        console.log("checking authentication status");
        return localStorage.getItem(STORE_KEY) !== null;
    },
    storeCredentials: (apiKey) => {
        localStorage.setItem(STORE_KEY, apiKey);
    },

}

export default Auth;