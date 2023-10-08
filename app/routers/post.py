from fastapi import Response, status, HTTPException, APIRouter, Depends
from typing import Optional, List
from .. import schemas, oauth2
from ..config import settings
from ..database import database_connection
#sqlalchemy imports

router = APIRouter(
    prefix="/posts",
    tags=['Posts'] #adds a tag to the documentation so that Posts and Users have their own sections (http://127.0.0.1:8000/docs)
)

conn = database_connection()
cursor = conn.cursor()


@router.get("/", response_model=List[schemas.Post]) #if we exclude List here, we'd get an error bc we'd be trying to force a list of posts into the shape of one post
def get_posts(current_user: int = Depends(oauth2.get_current_user),limit: int = 10, skip: int = 0, search: Optional[str] = ""): #"limit" is just a query parameter. If "?limit=someinteger&skip=someinteger" (e.g. posts?limit=4) is not called, then the default of 10 results will be returned.
    cursor.execute("""SELECT posts.*, users.*, count(users_id) AS votes 
                   FROM posts 
                   LEFT JOIN users on posts.user_id = users.id
                   LEFT JOIN votes on posts.post_id = votes.posts_post_id
                   WHERE title LIKE %s
                   GROUP BY post_id, users.id
                   ORDER BY post_id 
                    LIMIT %s OFFSET %s""",(('%'+search+'%'),limit,skip,)) #the %'s around the 'search' term are needed bc the % is a wildcard character in sql but %s is the variable in python so the code gets confused
    posts = cursor.fetchall()
    return posts

# default status codes get entered in the decorator
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.MainPost)
# Post is a class defined above to make sure user-entered data types are correct
def create_posts(post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""INSERT INTO posts(title, content, published, user_id) VALUES (%s, %s, %s, %s) RETURNING * """,(post.title, post.content, post.published, current_user['id'])) #the %s's are just variables that 'sanitize' the inputs from having any sql code in them. Otherwise, hackers can perform 'sql injection', which is importing malicious code into your db
    print(current_user["id"])
    new_post = cursor.fetchone()
    conn.commit() #actually saves the changes in the db
    return new_post


@router.get("/{post_id}", response_model=schemas.Post)  # path parameters (e.g. {post_id}) will always return a string so you have to manually convert it to another type if needed. Also, might be a good idea if path parameters are near the bottom of the request list bc for e.g. /posts/latest might get caught as {id} = 'latest' instead of it being a totally different request (1:50:00)
# 'int' here 1)automatically converts parameter to an integer and 2)returns an educated error message when it's not an integer
def get_post(post_id: int, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""SELECT posts.*, users.*, count(users_id) AS votes 
                   FROM posts 
                   LEFT JOIN users on posts.user_id = users.id
                   LEFT JOIN votes on posts.post_id = votes.posts_post_id
                    WHERE post_id = %s
                   GROUP BY post_id, users.id""", (str(post_id),)) #id needs to be converted to a string, otherwise the sql statement won't work. At 4:24:00, for some reason adding the extra comma at the end fixes some errors
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with post_id: {post_id} was not found")
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""DELETE FROM posts WHERE post_id = %s RETURNING *""", (str(post_id),))
    deleted_post = cursor.fetchone()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with post_id: {post_id} does not exist")
    if deleted_post["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    


@router.put("/{post_id}", response_model=schemas.MainPost)
# Post is a class defined above to make sure user-entered data types are correct
def update_post(post_id: int, post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user)):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE post_id = %s RETURNING *""", (post.title,post.content, post.published,str(post_id),))
    updated_post = cursor.fetchone()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"post with post_id: {post_id} does not exist")
    if updated_post["user_id"] != current_user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    conn.commit()
    return updated_post