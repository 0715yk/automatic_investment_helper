from fastapi import APIRouter, HTTPException
from services.account_service import get_account_info

router = APIRouter()

# 특정 코인 잔고 가져오기
@router.get("/account-info")
async def account_info():
    try:
        account_data = get_account_info()
        return {"status": "success", "data": account_data}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
