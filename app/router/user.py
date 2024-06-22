from database import get_db
import models, schemas, utils
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import oauth2
router = APIRouter(prefix='/users', tags=['Users'])

@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.User, 
                db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)
    try:
        new_user = models.User(**user.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError :
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Error: Create user failed")
    return new_user

@router.get('/{id}', status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def get_user(id: int, 
             db: Session = Depends(get_db),
             get_current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")
    return user

@router.get('/', status_code=status.HTTP_200_OK, response_model=list[schemas.UserOut])
def get_all_user(db: Session = Depends(get_db),
                 get_current_user: int = Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Not found users')
    return users

@router.get('/me/', status_code=status.HTTP_200_OK, response_model=schemas.UserOut)
def user(db: Session = Depends(get_db),
         get_current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == get_current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found')
    return user