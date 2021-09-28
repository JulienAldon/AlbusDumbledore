# Harry Potter Point Counter

By user, by houses :
- Import users from intra
- add points
- remove points

4 houses :
- Gryffindor
- Hufflepuff
- Slytherin
- Ravenclaw

# API
|    Rule    |  Route        |  Description        |
|------------|---------------|---------------------|
| GET        | /student/`<id>` |  Student Points     |
| GET        | /house/`<id>`   |  House Points       |
| PUT        | /student/`<id>`/`<points>` |  Student Add Points |
| PUT        | /house/`<id>`/`<points>`   |  House Add Points   |
| POST       | /students/import |  Import Students    |