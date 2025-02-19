# from fastapi import APIRouter, HTTPException,Depends
# from models import Survey
# from database import db 
# from bson import ObjectId
# from typing import List
# from datetime import datetime 

# router = APIRouter()

# @router.post("/surveys/", response_model=Survey)
# async def create_survey(survey: Survey):
#     survey_dict = dict(survey)
#     survey_dict["created_at"] = str(datetime.now())
#     new_survey = await db.surveys.insert_one(survey_dict)
#     return {**survey_dict, "id": str(new_survey.inserted_id)}   
    

# @router.get("/surveys/",response_model=List[Survey])
# async def get_surveys():
#     surveys = await db.surveys.find().to_list(100)
#     for survey in surveys:
#         survey["id"] = str(survey["_id"])
#         del survey["_id"]  
#     return surveys


# @router.get("/surveys/{survey_id}",response_model=Survey)    
# async def get_survey(survey_id:str):
#     survey = await db.surveys.find_one({"_id":ObjectId(survey_id)})
#     if not survey:
#         raise HTTPException(status_code=404, detail="Survey not found")
#     survey["id"] = str(survey["_id"])
#     del survey["_id"]
#     return survey


# @router.put("/surveys/{survey_id}",response_model=Survey)
# async def update_survey(survey_id:str,survey:Survey):
#     updated_survey = await db.surveys.find_one_and_update(
#         {"_id":ObjectId(survey_id)},
#         {"$set":survey.dict()},
#         return_document=True 
#     )
#     if not updated_survey:
#         raise HTTPException(status_code=404, detail="Survey not found")
#     updated_survey["id"] = str(updated_survey["_id"])
#     del updated_survey["_id"]
#     return updated_survey

# @router.delete("/surveys/{survey_id}")
# async def delete_survey(survey_id:str):
#     result = await db.surveys.delete_one({"_id":ObjectId(survey_id)})
#     if result.deleted_count==0:
#         raise HTTPException(status_code=404, detail="Survey not found")
#     return {"message":"Survey deleted successfully"}

# routes.py
from fastapi import APIRouter, HTTPException
from models import Survey
from database import db 
from bson import ObjectId
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/surveys/", response_model=Survey)
async def create_survey(survey: Survey):
    survey_dict = survey.dict()
    
    # If custom ID is provided, use it
    if survey.id:
        # Check if ID already exists
        existing_survey = await db.surveys.find_one({"_id": survey.id})
        if existing_survey:
            raise HTTPException(status_code=400, detail="Survey ID already exists")
        survey_dict["_id"] = survey.id
    
    survey_dict["created_at"] = str(datetime.utcnow())
    
    # Remove the 'id' field before insertion if it exists
    if "id" in survey_dict:
        del survey_dict["id"]
        
    new_survey = await db.surveys.insert_one(survey_dict)
    
    # Return the created survey
    created_survey = await db.surveys.find_one({"_id": new_survey.inserted_id})
    created_survey["id"] = str(created_survey["_id"])
    del created_survey["_id"]
    return created_survey

@router.get("/surveys/", response_model=List[Survey])
async def get_surveys():
    surveys = await db.surveys.find().to_list(100)
    for survey in surveys:
        survey["id"] = str(survey["_id"])
        del survey["_id"]
    return surveys

@router.get("/surveys/{survey_id}", response_model=Survey)
async def get_survey(survey_id: str):
    survey = await db.surveys.find_one({"_id": survey_id})
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    survey["id"] = str(survey["_id"])
    del survey["_id"]
    return survey

@router.post("/surveys/{survey_id}", response_model=Survey)
async def update_survey(survey_id: str, survey: Survey):
    updated_survey = await db.surveys.find_one_and_update(
        {"_id": survey_id},
        {"$set": {
            "title": survey.title,
            "description": survey.description,
            "questions": survey.questions
        }},
        return_document=True
    )
    if not updated_survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    updated_survey["id"] = str(updated_survey["_id"])
    del updated_survey["_id"]
    return updated_survey

@router.delete("/surveys/{survey_id}")
async def delete_survey(survey_id: str):
    result = await db.surveys.delete_one({"_id": survey_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": "Survey deleted successfully"}