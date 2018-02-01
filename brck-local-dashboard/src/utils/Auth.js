const STORE_KEY = '_apiKey';

const Auth = {
    isAuthenticated: () => {
        console.log("checking authentication status");
        return localStorage.getItem(STORE_KEY) !== null;
    },
    storeCredentials: (apiKey) => {
        console.log("storing new key")
        localStorage.setItem(STORE_KEY, apiKey);
    },
    getToken: () => {
        console.log("got key: ", localStorage.getItem(STORE_KEY));
        return localStorage.getItem(STORE_KEY);
    },
    clearCredentials: () => {
        localStorage.removeItem(STORE_KEY);
    }

}

export default Auth;