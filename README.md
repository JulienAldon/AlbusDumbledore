# Harry Potter Point Counter

By user, by houses :
- Import users from intra
- Add points
- Remove points

Poudlard houses :
- Gryffindor
- Hufflepuff
- Slytherin
- Ravenclaw

# API
|    Rule    |  Route        |  Description        |
|------------|---------------|---------------------|
| POST       | /api/students/import |  Import Students    |
| PUT        | /api/student/`<id>`/`<points>`?reason=`<reason>` |  Student Add Points |
| PUT        | /api/house/`<id>`/`<points>`   |  House Add Points   |
| GET        | /api/house/`<id>`   |  House Points       |
| GET        | /api/student/`<id>` |  Student Points     |
| GET | /api/houses | House points |
| GET | /api/students/logs | Logs of added points |
| GET | /api/students | All students |
| GET | /api/hidden/secret/route | The chamber of secret |

# Setup api
Create a `secret.py` file with:
- `SQLALCHEMY_DATABASE_URL`: Connection string for SQLALCHEMY
- `SECRET_KEY`: Secret string for token authentication
- `ALGORITHM`: Encryption Algorithm for token authentication
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Time it takes for the token to expire
- `hiddenFlag`: Hidden flag of the chamber of secret

Create a `populate_db.py` with: 
This script must initialize:
- Houses(id, name, points)
- UselessModel(id, hasBeenPingued)
- UserAdmin definition


Made by :
- Arthur Lemaire
- Julien Aldon
- Neil Cecchini