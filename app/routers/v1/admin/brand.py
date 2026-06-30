from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.repositories.brand_repository import BrandRepository
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse
from app.models.user import User
from app.schemas.base import BaseResponse

router = APIRouter(prefix="/brands", tags=["Admin - Brands"])


def generate_code(brand_name):
    return brand_name.upper().replace(" ", "-")


@router.post("/", response_model=BaseResponse[BrandResponse])
async def create_brand(
    brand_in: BrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = BrandRepository(db)
    brand_code = generate_code(brand_in.brand_name)

    existing = await repo.get_by_code(brand_code)
    if existing:
        raise HTTPException(status_code=400, detail="Brand code already exists")
    setattr(brand_in, "brand_code", brand_code)
    brand = await repo.create_with_file(brand_in.model_dump(), file=brand_in.file)
    return BaseResponse(data=brand)


@router.put("/{brand_id}", response_model=BaseResponse[BrandResponse])
async def update_brand(
    brand_id: int,
    brand_in: BrandUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = BrandRepository(db)
    brand = await repo.get_by_id(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    await repo.update(brand, brand_in.model_dump(exclude_unset=True))
    await db.commit()
    await db.refresh(brand)
    return BaseResponse(data=brand)


@router.patch("/{brand_id}/status", response_model=BaseResponse)
async def update_brand_status(
    brand_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    repo = BrandRepository(db)
    brand = await repo.get_by_id(brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    await repo.update(brand, {"status": status})
    await db.commit()
    return BaseResponse(data=None)
