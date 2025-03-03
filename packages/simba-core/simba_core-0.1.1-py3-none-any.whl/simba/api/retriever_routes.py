from fastapi import APIRouter

from simba.retrieval import Retriever

retriever_route = APIRouter(prefix="/retriever", tags=["Retriever"])
retriever = Retriever()


@retriever_route.get("/as_retriever")
async def get_retriever():
    return retriever.as_retriever()  # TODO: Add config in /dto/retriever_dto.py
