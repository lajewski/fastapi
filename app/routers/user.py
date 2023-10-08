from fastapi import status, HTTPException, APIRouter
from .. import schemas, utils
from ..database import database_connection
#sqlalchemy imports

router = APIRouter(
    prefix = "/users",
    tags = ['Users']
)

conn = database_connection()
cursor = conn.cursor()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate):
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    cursor.execute("""INSERT INTO users(email, password) VALUES (%s, %s) RETURNING * """,(user.email, user.password))
    new_user = cursor.fetchone()
    conn.commit()
    return new_user

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int):
    cursor.execute("""SELECT * FROM users WHERE id = %s""", (str(id),))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user with id: {id} does not exist")
    return user