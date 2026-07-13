from fastapi import APIRouter

from .routes import person_routes

person_router = APIRouter(tags=['People'])
person_router.include_router(person_routes.router, prefix='/people')
