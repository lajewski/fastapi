from fastapi import Response, status, HTTPException, APIRouter, Depends
from ..database import database_connection
from .. import schemas, oauth2
#sqlalchemy imports

router = APIRouter(
    prefix = "/vote",
    tags = ['Vote']
)

conn = database_connection()
cursor = conn.cursor()

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, current_user: int = Depends(oauth2.get_current_user)):
    
    cursor.execute("""SELECT * FROM posts WHERE post_id = %s""", (vote.post_id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {vote.post_id} does not exist") #raises exception if user tries to vote on a post that does not exist

    cursor.execute("""SELECT * FROM votes WHERE posts_post_id = %s AND users_id = %s""", (vote.post_id, current_user['id']))
    found_vote = cursor.fetchone() #checks if there is already a vote
    if(vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user['id']} has already voted on post {vote.post_id}")
        cursor.execute("""INSERT INTO votes(posts_post_id, users_id) VALUES (%s, %s) RETURNING * """, (vote.post_id, current_user['id']))
        new_vote = cursor.fetchone()
        conn.commit()
        return {"message": "successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist")
        cursor.execute("""DELETE FROM votes WHERE posts_post_id = %s AND users_id = %s""", (vote.post_id, current_user['id']))
        conn.commit()
        return {"message": "successfully deleted vote"}