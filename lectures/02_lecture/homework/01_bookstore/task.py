from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional

# ═══════════════════════════════════════════════════════════
# МОДЕЛИ
# ═══════════════════════════════════════════════════════════

class Category(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=50)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    model_config = {"extra": "forbid"}


class Book(BaseModel):
    id: int
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=0, le=2025)
    isbn: str
    price: float = Field(gt=0)
    category_id: Optional[int] = None


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=0, le=2025)
    isbn: str
    price: float = Field(gt=0)
    category_id: Optional[int] = None


# ═══════════════════════════════════════════════════════════
# ИСКЛЮЧЕНИЯ
# ═══════════════════════════════════════════════════════════

class BookNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=404,
            detail={"detail": "Book not found", "code": "NOT_FOUND"},
        )


class DuplicateIsbnException(HTTPException):
    def __init__(self, isbn: str):
        super().__init__(
            status_code=409,
            detail={"detail": f"Book with ISBN {isbn} already exists", "code": "DUPLICATE_ISBN"},
        )


# ═══════════════════════════════════════════════════════════
# ПРИЛОЖЕНИЕ
# ═══════════════════════════════════════════════════════════

app = FastAPI(title="Bookstore API")

BOOKS: list[dict] = []
CATEGORIES: list[dict] = []
_book_id_counter = 0
_category_id_counter = 0


# ═══════════════════════════════════════════════════════════
# ОБРАБОТЧИКИ ОШИБОК
# ═══════════════════════════════════════════════════════════

@app.exception_handler(BookNotFoundException)
async def book_not_found_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.exception_handler(DuplicateIsbnException)
async def duplicate_isbn_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


# ═══════════════════════════════════════════════════════════
# КАТЕГОРИИ
# ═══════════════════════════════════════════════════════════

@app.get("/categories")
def list_categories():
    return CATEGORIES


@app.post("/categories", status_code=201)
def create_category(category: CategoryCreate):
    global _category_id_counter
    _category_id_counter += 1
    new_cat = {"id": _category_id_counter, "name": category.name}
    CATEGORIES.append(new_cat)
    return new_cat


# ═══════════════════════════════════════════════════════════
# CRUD КНИГ
# ВАЖНО: /books/search ДОЛЖЕН быть до /books/{book_id}
# ═══════════════════════════════════════════════════════════

@app.get("/books/search")
def search_books(query: str):
    q = query.lower()
    return [
        b for b in BOOKS
        if q in b["title"].lower() or q in b["author"].lower()
    ]


@app.get("/books")
def list_books(category_id: Optional[int] = None, year: Optional[int] = None):
    result = BOOKS
    if category_id is not None:
        result = [b for b in result if b.get("category_id") == category_id]
    if year is not None:
        result = [b for b in result if b["year"] == year]
    return result


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for b in BOOKS:
        if b["id"] == book_id:
            return b
    raise BookNotFoundException()


@app.post("/books", status_code=201)
def create_book(book: BookCreate):
    global _book_id_counter
    for b in BOOKS:
        if b["isbn"] == book.isbn:
            raise DuplicateIsbnException(book.isbn)
    _book_id_counter += 1
    new_book = {"id": _book_id_counter, **book.model_dump()}
    BOOKS.append(new_book)
    return new_book


@app.put("/books/{book_id}")
def update_book(book_id: int, book: BookCreate):
    for i, b in enumerate(BOOKS):
        if b["id"] == book_id:
            updated = {"id": book_id, **book.model_dump()}
            BOOKS[i] = updated
            return updated
    raise BookNotFoundException()


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    for i, b in enumerate(BOOKS):
        if b["id"] == book_id:
            BOOKS.pop(i)
            return
    raise BookNotFoundException()