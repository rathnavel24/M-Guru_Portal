from pydantic import BaseModel

class SectionResponse(BaseModel):
    section_id : int
    section_name : str

    class config:
        from_attributes = True