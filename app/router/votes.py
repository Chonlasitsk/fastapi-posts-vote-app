import oauth2
from database import get_db
import models, schemas
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(tags=['Votes'])
@router.post('/vote', status_code=status.HTTP_201_CREATED)
async def vote(vote: schemas.Vote,
               db: Session = Depends(get_db),
               get_current_user: int = Depends(oauth2.get_current_user)):
    
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with ids: {vote.post_id} does not exist !')
    

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == get_current_user.id)
    found_vote = vote_query.first()
    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f'user {get_current_user.id} has already voted on post {vote.post_id}')
        new_vote = models.Vote(post_id=vote.post_id, user_id=get_current_user.id)
        db.add(new_vote)
        db.commit()
        return {'message':'Vote complete !'}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail='Vote does not exits')
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {'message': 'successful delete vote'}

@router.get('/votes', status_code=status.HTTP_200_OK)
def get_all_vote(db: Session = Depends(get_db),
                 get_current_user: int = Depends(oauth2.get_current_user)):
    votes = db.query(models.Vote).all()
    if not votes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Vote not found')
    return votes