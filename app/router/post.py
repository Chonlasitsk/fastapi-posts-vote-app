from ..database import get_db
from .. import models, schemas, oauth2
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing  import Optional
from sqlalchemy import func

router = APIRouter(tags=['Posts'])
@router.get('/posts', response_model = list[tuple[schemas.Post, int]])
def get_posts(db: Session = Depends(get_db), 
              get_current_user: int = Depends(oauth2.get_current_user),
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ''):
    
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    results = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(models.Vote, 
                                                                                         models.Vote.post_id == models.Post.id, 
                                                                                         isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return results

@router.post('/posts', status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, 
                 db: Session = Depends(get_db), 
                 get_current_user: int = Depends(oauth2.get_current_user)):
    try:
        # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""", 
        #                (post.title, post.content, post.published))
        # new_post = cursor.fetchone()
        # conn.commit()
        new_post = models.Post(**post.model_dump(), owner_id = get_current_user.id)
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
    except Exception as error:
        print('Error :', error)
        return {'message': 'Error creating post'}
    return new_post

@router.get('/posts/{id}', response_model=schemas.Post)
def get_post(id: int, 
             db: Session = Depends(get_db),
             get_current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
    if post.owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='No authorized to perform requested action') 
    return post

@router.delete('/posts/{id}')
def delete_post(id: int, 
                db: Session = Depends(get_db),
                get_current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s """, (str(id)))
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    if post.first().owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='No authorized to perform requested action') 
    post.delete(synchronize_session=False)
    db.commit()
    return {'message': 'post has been deleted'}
@router.put('/posts/{id}')
def update_post(id: int, 
                payload: schemas.PostUpdate, 
                db: Session = Depends(get_db),
                get_current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s """, (payload.title, payload.content, payload.published, str(id)))
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=404, detail=f"post with id: {id} was not found")
    
    if post.first().owner_id != get_current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='No authorized to perform requested action') 
    post.update(payload.model_dump(), synchronize_session=False)
    db.commit()
    return {'message': 'post has been updated'}