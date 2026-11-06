
import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator

from app.operations import add, subtract, multiply, divide

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Module 10 Secure User Application",
    version="1.0.0"
)

templates = Jinja2Templates(directory="templates")


class OperationRequest(BaseModel):
    a: float = Field(..., description="First number")
    b: float = Field(..., description="Second number")

    @field_validator("a", "b")
    @classmethod
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Both values must be numbers.")
        return value


class OperationResponse(BaseModel):
    result: float


class ErrorResponse(BaseModel):
    error: str


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    logger.error(
        "HTTP error on %s: %s",
        request.url.path,
        exc.detail
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    messages = "; ".join(
        f"{error['loc'][-1]}: {error['msg']}"
        for error in exc.errors()
    )

    logger.error(
        "Validation error on %s: %s",
        request.url.path,
        messages
    )

    return JSONResponse(
        status_code=400,
        content={"error": messages}
    )


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/add", response_model=OperationResponse)
async def add_route(operation: OperationRequest):
    try:
        return OperationResponse(
            result=add(operation.a, operation.b)
        )
    except Exception as error:
        logger.exception("Addition failed")
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


@app.post("/subtract", response_model=OperationResponse)
async def subtract_route(operation: OperationRequest):
    try:
        return OperationResponse(
            result=subtract(operation.a, operation.b)
        )
    except Exception as error:
        logger.exception("Subtraction failed")
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


@app.post("/multiply", response_model=OperationResponse)
async def multiply_route(operation: OperationRequest):
    try:
        return OperationResponse(
            result=multiply(operation.a, operation.b)
        )
    except Exception as error:
        logger.exception("Multiplication failed")
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error


@app.post("/divide", response_model=OperationResponse)
async def divide_route(operation: OperationRequest):
    try:
        return OperationResponse(
            result=divide(operation.a, operation.b)
        )
    except ValueError as error:
        logger.error("Division error: %s", error)
        raise HTTPException(
            status_code=400,
            detail=str(error)
        ) from error
    except Exception as error:
        logger.exception("Unexpected division error")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        ) from error


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )
