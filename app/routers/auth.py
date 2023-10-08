from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from pydantic import EmailStr
from .. import schemas, utils, oauth2
from ..database import database_connection
#sqlalchemy imports


router = APIRouter(
    tags=['Authentication']
    )

conn = database_connection()
cursor = conn.cursor()      


@router.post('/login', response_model=schemas.Token)
#def login(user_credentials: schemas.UserLogin):  #this was used before we had OAuth2PasswordRequestForm
def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    #OAuth2PasswordRequestForm only stores two values u and p
    #e.g. {
        # "username": "plajewski"
        # "password": "lkfjsafjla;"
    # }
    #user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    #cursor.execute("""SELECT id,email,password FROM users WHERE email = %s""", (user_credentials.username,)) #this was used before we had OAuth2PasswordRequestForm 7:12:00 in video
    cursor.execute("""SELECT id,email,password FROM users WHERE email = %s""", (user_credentials.username,)) #user_credentials.email is the user-entered email. Returns a dictionary with the email and hashed password from the db. Note that we can't use WHERE 'password' because we would be looking for the unhashed password that the user entered, which doesn't exist in the db
    user_email = cursor.fetchone()
    user_password = user_email.get('password', None) #puts the hashed password into a string (instead of a dictionary), which we need when comparing the user-entered password with the hashed password
    user_id = user_email.get('id',None)

    if not user_email:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials - email")

    if not utils.verify(user_credentials.password, user_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid Credentials - password')
    
    #create a token
    #return a token

    access_token = oauth2.create_access_token(data = {"user_id": user_id}) #you can put a bunch of things in here (e.g. different user roles). Here we're just doing user_id.
    
    return {"access_token": access_token, "token_type": "bearer"} #when getting the access_token response in postman, you can then enter that 32 char access token into jwt.io (website) and it'll show the info that we embedded above i.e. the user id 





