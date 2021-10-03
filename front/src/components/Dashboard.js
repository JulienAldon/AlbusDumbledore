import { useEffect, useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import config from "../config"
import styles from './Dashboard.module.css'

const houses = {
    1: "Slytherin",
    2: "Hufflepuff",
    3: "Ravenclaw",
    4: "Gryffindor"
}

const LogRow = ({log}) => {

    console.log(log)

    return (
        <tr>
            <td className={styles.logImage}>
                <img className={`${styles.house}`} src={`${houses[log.house].toLowerCase()}.png`} alt="Gryffindor" />
            </td>
            <td>
                <div>{log.name}</div>
                <div>{log.reason}</div>
            </td>
            <td className={styles.logPoints}>{`${log.points > 0 ? "+" : ""}${log.points}`}</td>
        </tr>
    )
}

const Dashboard = () => {

    const [points, setPoints] = useState(null)
    const [logs, setLogs] = useState(null)

    useEffect(() => {
        updateScores()
        updateLogs()
        const handle = setInterval(() => {
            updateScores()
            updateLogs()
        }, 60000)

        return () => {
            clearInterval(handle)
        }
    }, [])

    const updateScores = () => {
        fetch(`${config.url}/houses`).then(res => res.json()).then((res) => {
            setPoints(res)
        }).catch(err => {
            console.error(err)
        })
    }
    
    const updateLogs = () => {
        fetch(`${config.url}/students/logs`).then(res => {
            if (res.status === 404) {
                return null
            }
            return res.json()
        }).then((res) => {
            setLogs(res)
        }).catch((err) => {
            console.error(err)
        })
    } 

    const scale = useMemo(() => {
        if (points === null) {
            return 100
        }
        return Math.max(100, ...Object.values(points))
    }, [points])

    console.log(points)

    return (
        <>
            {points !== null
                ? <main className={`${styles.gauges} gauges`} style={{background: `url(${process.env.PUBLIC_URL}/latest.png)`}}>
                    <div style={{"--size": points["Gryffindor"]/scale}} className={`${styles.gryffindor} gryffindor`}></div>
                    <div style={{"--size": points["Hufflepuff"]/scale}} className={`${styles.hufflepuff} hufflepuff`}></div>
                    <div style={{"--size": points["Ravenclaw"]/scale}} className={`${styles.ravenclaw} ravenclaw`}></div>
                    <div style={{"--size": points["Slytherin"]/scale}} className={`${styles.slytherin} slytherin`}></div>
                </main>
                : null}
            <aside className={`${styles.scores}`}>
                <div className="gryffindor">
                    <img className="large house" src="gryffindor.png" alt="Gryffindor" />
                    <h3>Gryffindor</h3>
                    <p>{points?.["Gryffindor"] ?? 0}</p>
                </div>
                <div className="hufflepuff">
                    <img className="large house" src="hufflepuff.png" alt="Hufflepuff" />
                    <h3>Hufflepuff</h3>
                    <p>{points?.["Hufflepuff"] ?? 0}</p>
                </div>
                <div className="ravenclaw">
                    <img className="large house" src="ravenclaw.png" alt="Ravenclaw" />
                    <h3>Ravenclaw</h3>
                    <p>{points?.["Ravenclaw"] ?? 0}</p>
                </div>
                <div className="slytherin">
                    <img className="large house" src="slytherin.png" alt="Slytherin" />
                    <h3>Slytherin</h3>
                    <p>{points?.["Slytherin"] ?? 0}</p>
                </div>
            </aside>
            <div className={`${styles.log}`}>
                <table>
                    <thead>
                        <tr>
                            <th>House</th>
                            <th>Login</th>
                            <th>Points</th>
                        </tr>
                    </thead>
                    <tbody>
                        {logs ? [...logs].reverse().map(log => <LogRow log={log} key={log.id}/>) : null}
                    </tbody>
                </table>
            </div>
            <Link className={styles.admin} to="/dumbledore">Admin</Link>
        </>
    )
}

export default Dashboard