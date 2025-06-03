from fastapi import Request, Depends, HTTPException, status
from repositories.team_repository import get_team_owner_id
from repositories.league_repository import get_league_owner_id


def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user_id

def check_user_ownership(request: Request, team_id: int):
    user_id = get_current_user(request)
    team_owner_id = get_team_owner_id(team_id)
    if user_id == team_owner_id:
        return True
    else:
        return False        
        
def require_team_owner(request: Request, team_id: int, user_id: int = Depends(get_current_user)):
    team_owner_id = get_team_owner_id(team_id)
    if user_id != team_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return True

def require_league_owner(request: Request, league_id: int, user_id: int = Depends(get_current_user)):
    league_owner_id = get_league_owner_id(league_id)
    if user_id != league_owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return True

def require_admin(request: Request):
    role = request.session.get("role")
    if role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return True
