import React, { useState, useContext, createContext } from "react";
import { useLocalStorage } from "./useLocalStorage"
import config from "../config"

const authContext = createContext();

// Provider component that wraps your app and makes auth object ...
// ... available to any child component that calls useAuth().
export function ProvideAuth({ children }) {
  const auth = useProvideAuth();
  return <authContext.Provider value={auth}>{children}</authContext.Provider>;
}

// Hook for child components to get the auth object ...
// ... and re-render when it changes.
export const useAuth = () => {
  return useContext(authContext);
};

// Provider hook that creates auth object and handles state
function useProvideAuth() {
  const [user, setUser] = useLocalStorage("token", null);
  const signin = (email, password) => {
    const data = new FormData()
    data.append('username', email)
    data.append('password', password)
    return fetch(`${config.url}/token`, {
      method: 'POST',
      // headers: {
      //   'Content-Type': 'multipart/form-data'
      // },
      body: data
    }).then(res => {
      if (res.ok)
        return res.json()
      else
        return null
    }).then(res => {
      setUser(res)
    }).catch(err => {
      setUser(null)
    })
  };

  const signout = () => {
    return fetch(`${config.url}/logout`).then(() => {
      setUser(null)
    }).catch(err => {
      setUser(null)
    })
  };
  // Return the user object and auth methods
  return {
    user,
    signin,
    signout,
  };
}