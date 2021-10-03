import { useRef } from 'react'
import { useHistory } from 'react-router'
import { useAuth } from '../hooks/use-auth'
import styles from "./Login.module.css"

const Login = () => {
    
    const auth = useAuth()

    const history = useHistory()

    const loginRef = useRef()
    const pwdRef = useRef()

    const submit = (e) => {
        e.preventDefault()
        if (loginRef.current.value == "" || pwdRef.current.value == "")
            return
        auth.signin(loginRef.current.value, pwdRef.current.value).then(() => {
            history.push('/dumbledore')
        })
    }

    return (
        <form className={styles.login} onSubmit={submit}>
            <div>
                <label htmlFor="username">Username</label>
                <input name="username" type="text" ref={loginRef}></input>
            </div>
            <div>
                <label htmlFor="password">Password</label>
                <input name="password" type="password" ref={pwdRef}></input>
            </div>
            <button type="submit">Let's go</button>
        </form>
    )
}

export default Login