const STORE_KEY = '_apiKey';
const PASSWORD_STATE_KEY = '_password_changed';

const Auth = {
    isAuthenticated: () => {
        return localStorage.getItem(STORE_KEY) !== null;
    },
    requiresPasswordChange: () => {
        return localStorage.getItem(PASSWORD_STATE_KEY) === "false";
    },
    storeCredentials: (apiKey, password_changed) => {
        localStorage.setItem(STORE_KEY, apiKey);
        localStorage.setItem(PASSWORD_STATE_KEY, password_changed);
    },
    setPasswordStatus: (status) => {
        localStorage.setItem(PASSWORD_STATE_KEY, status);
    },
    getToken: () => {
        return localStorage.getItem(STORE_KEY);
    },
    clearCredentials: () => {
        localStorage.removeItem(STORE_KEY);
        localStorage.removeItem(PASSWORD_STATE_KEY);
    }
}

export default Auth;