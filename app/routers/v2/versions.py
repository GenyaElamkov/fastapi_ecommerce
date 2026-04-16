from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException, status

app = FastAPI()

router = APIRouter(prefix="/notes")

def http_exception_400(detail: str):
    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )

def validate_note_id(note_id: int):
    if note_id <= 0:
        http_exception_400("Invalid note ID")
    return note_id


@router.get("/")
async def get_all_notes(api_version: str = Header(default=None, alias="X-API-Version")):
    if api_version == "v1":
        return "Notes in v1: Note 1, Note 2"
    if api_version == "v2":
        return "Notes in v2: Note 1 (draft), Note 2 (published)" 
    http_exception_400("Invalid or missing API version")


@router.get("/count")
async def count_notes(api_version: str = Header(default=None, alias="X-API-Version")):
    if api_version == "v1":
        http_exception_400("Invalid or missing API version")
    if api_version == "v2":
        return "Total notes in v2: 2"
    http_exception_400("Invalid or missing API version")
    

@router.get("/{note_id}")
async def get_note(
    note_id: int = Depends(validate_note_id), 
    api_version: str = Header(default=None, alias="X-API-Version")
):
    if api_version == "v1":
        return f"Note {note_id} in v1"
    if api_version == "v2":
        return f"Note {note_id} in v2 with status: draft"
    http_exception_400("Invalid or missing API version")
    


app.include_router(router, prefix="/api")
