import { useEffect, useState, useMemo, useRef } from 'react'
import { useHistory } from 'react-router'
import Select from 'react-select'
import { useAuth } from '../hooks/use-auth'
import config from "../config"
import styles from "./Dumbledore.module.css"

const customStyles = {
    option: (provided, state) => ({
        ...provided,
        color: state.isSelected ? 'white' : 'black',
    }),
}

const Dumbledore = () => {

    const auth = useAuth()

    const history = useHistory()

    const [bulkMode, setBulkMode] = useState(false)
    const [students, setStudents] = useState([])
    const [student, setStudent] = useState("")
    const [reason, setReason] = useState("")
    const [points, setPoints] = useState(0)

    const fileInput = useRef()

    const options = useMemo(() => {
        return students.map(student => ({
            value: student.id,
            label: student.name
        }))
    }, [students])

    useEffect(() => {
        fetch(`${config.url}/students`, {
            headers: {
                'Authorization': `Bearer ${auth.user.access_token}`,
            }
        }).then(res => res.json()).then((res => {
            setStudents(res)
        })).catch(err => {
            console.error(err)
        })
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    const submit = () => {
        fetch(`${config.url}/student/${student}/${points}?reason=${reason}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${auth.user.access_token}`,
            }
        }).then(res => {
            if (res.status === 200)
                history.push("/")
        })
    }

    const submitBulk = () => {
        const data = new FormData()
        console.log(fileInput.current.files[0])
        data.append('file', fileInput.current.files[0])
        fetch(`${config.url}/students/${points}?reason=${reason}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${auth.user.access_token}`,
            },
            body: data
        }).then(res => {
            if (res.status === 200)
                history.push("/")
        })
    }

    return (
        <div className={styles.dumbledore}>
            <div>
                <label htmlFor="bulk">bulk mode</label>
                <input type="checkbox" checked={bulkMode} onChange={e => setBulkMode(!bulkMode)} id="bulk"/>
            </div>
            {bulkMode
                ? <input placeholder="students list" type="file" accept=".csv" ref={fileInput}/>
                : <>
                    <label>Student</label>
                    <Select options={options} styles={customStyles} placeholder="Sélectionner l'étudiant à envoyer aux cachots" onChange={(e) => setStudent(e.value)}/>
                </>
            }
            <label>Points</label>
            <input type="number" value={points} onChange={(e) => setPoints(e.target.value)}></input>
            <label>Reason</label>
            <input type="text" value={reason} onChange={(e) => setReason(e.target.value)}></input>
            <button type="button" onClick={bulkMode ? submitBulk : submit}>Let's go</button>
        </div>
    )
}

export default Dumbledore