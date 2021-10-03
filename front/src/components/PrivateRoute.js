import React from 'react';
import { useAuth } from '../hooks/use-auth';
import { Route, Redirect } from 'react-router-dom';

export const PrivateRoute = ({ component: Component, ...rest }) => {
    const { user } = useAuth()
    return (
        <Route {...rest} render={(props) => {
                if (!user) {
                        return(<Redirect to='/login' />)
                }
                else{
                        return( <Component {...props} /> )
                }
        }} />
    )
}