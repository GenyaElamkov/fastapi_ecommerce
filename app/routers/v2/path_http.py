from fastapi import APIRouter, FastAPI

app = FastAPI()

root_company = APIRouter(prefix="/company", tags=["company"])

@root_company.get("/")
async def root():
    return "This is the company level"

root_department = APIRouter(prefix="/departments/{dept_id}", tags=["departments"])

@root_department.get("/")
async def get_departmen(dept_id: int):
    return f"This is department {dept_id}"

root_teams = APIRouter(prefix="/teams/{team_id}", tags=["teams"])

@root_teams.get("/")
async def get_team(dept_id: int, team_id: int):
    return f"This is team {team_id} in department {dept_id}"

root_employees = APIRouter(prefix="/employees/{emp_id}", tags=["employees"])

@root_employees.get("/")
async def get_employee(dept_id: int, team_id: int, emp_id: int):
    return f"This is employee {emp_id} in team {team_id}, department {dept_id}"

root_teams.include_router(root_employees)
root_department.include_router(root_teams)
root_company.include_router(root_department)
app.include_router(root_company, prefix='/api')

