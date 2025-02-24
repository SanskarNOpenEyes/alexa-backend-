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
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["survey_db"]
survey_collection = db["surveys"]
survey_response_collection = db["survey_responses"]

# Pydantic Models
class CreateSurveyRequest(BaseModel):
    survey_number: str

class AddQuestionRequest(BaseModel):
    question: str

class UpdateQuestionsRequest(BaseModel):
    questions: list[str]

class UpdateSurveyNameRequest(BaseModel):
    name: str

class SurveyAccessRequest(BaseModel):
    survey_number: str
    username: str

class SubmitSurveyRequest(BaseModel):
    survey_number: str
    username: str
    answers: list[dict[str, str]]
    question: list[str] 

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


# 9️⃣ Get all responses for a specific survey
@app.get("/surveys/{survey_id}/responses/")
async def get_survey_responses(survey_id: str):
    responses = await survey_response_collection.find({"survey_id": ObjectId(survey_id)}).to_list(100)
    return responses




@app.post("/surveys/access/")
async def access_survey(request: SurveyAccessRequest):
    # Try to find the survey by name instead of just ID
    survey = await survey_collection.find_one({"name": request.survey_number})
    
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    survey["_id"] = str(survey["_id"])
    return survey
   

@app.post("/surveys/submit/")
async def submit_survey(request: SubmitSurveyRequest): 
    survey = await survey_collection.find_one({"_id": ObjectId(request.survey_number)})
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    response_data = {
        "survey_number": survey["survey_number"],
        "username": request.username,
        "answers": request.answers,
    }

    result = await survey_response_collection.insert_one(response_data)
    return {"submission_id": str(result.inserted_id), "message": "Survey responses submitted successfully"}

class AlexaRequest(BaseModel):
    request: dict

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
@app.post("/alexa/survey/")
async def alexa_survey_handler(request: AlexaRequest):
    logger.info(f"Received Alexa request: {request.json()}")  # Log request for debugging

    try:
        intent_name = request.request["intent"]["name"]
        logger.info(f"Processing intent: {intent_name}")

        if intent_name == "FetchSurveyIntent":
            survey_name = request.request["intent"]["slots"].get("surveyName", {}).get("value", None)
            logger.info(f"Fetching survey: {survey_name}")

            if not survey_name:
                return {"response": "Please provide a survey name."}
            
            survey = await survey_collection.find_one({"name": survey_name})
            if not survey or "questions" not in survey or len(survey["questions"]) == 0:
                return {"response": f"Sorry, the {survey_name} survey is not available."}

            first_question = survey["questions"][0]
            return {"response": f"Starting the {survey_name} survey. First question: {first_question}"}

        elif intent_name == "AnswerSurveyIntent":
            answer = request.request["intent"]["slots"].get("answer", {}).get("value", None)
            survey_name = request.session.get("survey_name", None)
            logger.info(f"Saving response: {answer} for survey: {survey_name}")

            if not survey_name or not answer:
                return {"response": "Please start a survey before answering."}

            await survey_response_collection.insert_one({
                "survey_name": survey_name,
                "answer": answer,
                "username": request.session.get("username", "Unknown")
            })

            return {"response": f"Thank you! Your answer '{answer}' has been recorded."}

    except Exception as e:
        logger.error(f"Error processing Alexa request: {str(e)}")
        return {"response": "An error occurred. Please try again."}

    return {"response": "I didn't understand that request."}
