from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific frontend URL if needed
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"message": "Server is running"}


# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client["survey_db"]
survey_collection = db["surveys"]

# Pydantic Models
class CreateSurveyRequest(BaseModel):
    survey_number: str

class AddQuestionRequest(BaseModel):
    question: str

class UpdateQuestionsRequest(BaseModel):
    questions: list[str]

class UpdateSurveyNameRequest(BaseModel):
    name: str

# Utility function to convert MongoDB document to JSON
def survey_helper(survey) -> dict:
    return {
        "id": str(survey["_id"]),
        "survey_number": survey["survey_number"],
        "name": survey.get("name", ""),
        "questions": survey.get("questions", [])
    }

# 1️⃣ Create a new survey (only using survey number)
@app.post("/surveys/")
async def create_survey(request: CreateSurveyRequest):
    survey_data = {"survey_number": request.survey_number, "questions": []}
    result = await survey_collection.insert_one(survey_data)
    return {"id": str(result.inserted_id), "survey_number": request.survey_number}

# 2️⃣ Add a question to an existing survey
@app.post("/surveys/{survey_id}/questions/")
async def add_question(survey_id: str, request: AddQuestionRequest):
    result = await survey_collection.update_one(
        {"_id": ObjectId(survey_id)},
        {"$push": {"questions": request.question}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": "Question added successfully"}

# 3️⃣ Update all questions in a survey
@app.put("/surveys/{survey_id}/questions/")
async def update_questions(survey_id: str, request: UpdateQuestionsRequest):
    result = await survey_collection.update_one(
        {"_id": ObjectId(survey_id)},
        {"$set": {"questions": request.questions}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": "Questions updated successfully"}

# 4️⃣ Update the survey name
@app.put("/surveys/{survey_id}/name/")
async def update_survey_name(survey_id: str, request: UpdateSurveyNameRequest):
    result = await survey_collection.update_one(
        {"_id": ObjectId(survey_id)},
        {"$set": {"name": request.name}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": "Survey name updated successfully"}

# 5️⃣ Delete a specific question from a survey
@app.delete("/surveys/{survey_id}/questions/")
async def delete_question(survey_id: str, request: AddQuestionRequest):
    result = await survey_collection.update_one(
        {"_id": ObjectId(survey_id)},
        {"$pull": {"questions": request.question}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Survey not found or question not found")
    return {"message": "Question deleted successfully"}

# 6️⃣ Delete an entire survey
@app.delete("/surveys/{survey_id}")
async def delete_survey(survey_id: str):
    result = await survey_collection.delete_one({"_id": ObjectId(survey_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Survey not found")
    return {"message": "Survey deleted successfully"}

# 7️⃣ Get all surveys (Optional)
@app.get("/surveys/")
async def get_surveys():
    surveys = await survey_collection.find().to_list(100)
    return [survey_helper(survey) for survey in surveys]



