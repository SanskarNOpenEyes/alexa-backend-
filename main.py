# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from motor.motor_asyncio import AsyncIOMotorClient
# from bson import ObjectId
# import os
# from fastapi.middleware.cors import CORSMiddleware
# from typing import List, Optional

# app = FastAPI()

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/")
# def read_root():
#     return {"message": "Server is running"}

# # MongoDB Connection
# MONGO_URI = "mongodb+srv://GenerateQuestions:GenerateQuestions%40123@cluster0.b3ymk.mongodb.net/test?tls=true"
# client = AsyncIOMotorClient(MONGO_URI)
# db = client["survey_db"]
# survey_collection = db["surveys"]
# survey_response_collection = db["survey_responses"]

# # ---------------------- Pydantic Models ----------------------

# class CreateSurveyRequest(BaseModel):
#     survey_number: str
#     name: str

# class AddQuestionRequest(BaseModel):
#     question_text: str
#     question_type: str  # "qa", "mcq", "rating"
#     mcq_options: Optional[List[str]] = None  # Only required if question_type is "mcq"

# class UpdateQuestionsRequest(BaseModel):
#     questions: List[dict]  # Each question is a dict with question_text, question_type, etc.

# class UpdateSurveyNameRequest(BaseModel):
#     name: str

# class SurveyAccessRequest(BaseModel):
#     survey_number: str
#     username: str

# class SubmitSurveyRequest(BaseModel):
#     survey_number: str
#     username: str
#     answers: List[dict]

# # Utility function to format MongoDB document
# def survey_helper(survey) -> dict:
#     return {
#         "id": str(survey["_id"]),
#         "survey_number": survey["survey_number"],
#         "name": survey.get("name", ""),
#         "questions": survey.get("questions", [])
#     }

# # ---------------------- API Endpoints ----------------------

# # 1️⃣ Create a new survey
# @app.post("/surveys/")
# async def create_survey(request: CreateSurveyRequest):
#     survey_data = {
#         "survey_number": request.survey_number,
#         "name": request.name,
#         "questions": []
#     }
#     result = await survey_collection.insert_one(survey_data)
#     return {"id": str(result.inserted_id), "survey_number": request.survey_number}

# # 2️⃣ Add a question with a type
# @app.post("/surveys/{survey_id}/questions/")
# async def add_question(survey_id: str, request: AddQuestionRequest):
#     question_data = {

#         "question_text": request.question_text,
#         "question_type": request.question_type
#     }

#     # If MCQ, include options
#     if request.question_type == "mcq" and request.mcq_options:
#         question_data["mcq_options"] = request.mcq_options

#     result = await survey_collection.update_one(
#         {"_id": ObjectId(survey_id)},
#         {"$push": {"questions": question_data}}
#     )

#     if result.modified_count == 0:
#         raise HTTPException(status_code=404, detail="Survey not found")

#     return {"message": "Question added successfully 1"}

# # 3️⃣ Update all questions in a survey (supporting question types)
# @app.put("/surveys/{survey_id}/questions/")
# async def update_questions(survey_id: str, request: UpdateQuestionsRequest):
#     result = await survey_collection.update_one(
#         {"_id": ObjectId(survey_id)},
#         {"$set": {"questions": request.questions}}
#     )

#     if result.modified_count == 0:
#         raise HTTPException(status_code=404, detail="Survey not found")

#     return {"message": "Questions updated successfully1"}

# # 4️⃣ Update survey name
# @app.put("/surveys/{survey_id}/name/")
# async def update_survey_name(survey_id: str, request: UpdateSurveyNameRequest):
#     result = await survey_collection.update_one(
#         {"_id": ObjectId(survey_id)},
#         {"$set": {"name": request.name}}
#     )

#     if result.modified_count == 0:
#         raise HTTPException(status_code=404, detail="Survey not found")

#     return {"message": "Survey name updated successfully"}

# # 5️⃣ Delete a specific question from a survey
# @app.delete("/surveys/{survey_id}/questions/")
# async def delete_question(survey_id: str, request: AddQuestionRequest):
#     result = await survey_collection.update_one(
#         {"_id": ObjectId(survey_id)},
#         {"$pull": {"questions": {"question_text": request.question_text}}}
#     )

#     if result.modified_count == 0:
#         raise HTTPException(status_code=404, detail="Survey or question not found")

#     return {"message": "Question deleted successfully"}

# # 6️⃣ Delete an entire survey
# @app.delete("/surveys/{survey_id}")
# async def delete_survey(survey_id: str):
#     result = await survey_collection.delete_one({"_id": ObjectId(survey_id)})
    
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Survey not found")

#     return {"message": "Survey deleted successfully"}

# # 7️⃣ Get all surveys
# @app.get("/surveys/")
# async def get_surveys():
#     surveys = await survey_collection.find().to_list(100)
#     return [survey_helper(survey) for survey in surveys]

# # 8️⃣ Get all responses for a specific survey
# @app.get("/surveys/{survey_id}/responses/")
# async def get_survey_responses(survey_id: str):
#     responses = await survey_response_collection.find({"survey_number": survey_id}).to_list(100)
#     return responses

# # 9️⃣ Allow user to access a survey
# @app.post("/surveys/access/")
# async def access_survey(request: SurveyAccessRequest):
#     survey = await survey_collection.find_one({"survey_number": request.survey_number})
    
#     if not survey:
#         raise HTTPException(status_code=404, detail="Survey not found")
    
#     survey["_id"] = str(survey["_id"])
#     return survey    

# # 🔟 Submit a survey response
# @app.post("/surveys/submit/")  
# async def submit_survey(request: SubmitSurveyRequest): 
#     survey = await survey_collection.find_one({"survey_number": request.survey_number})
#     print(request.survey_number)
    
#     if not survey:
#         raise HTTPException(status_code=409, detail="Survey not found")
    
#     response_data = {
#         "survey_number": request.survey_number,
#         "username": request.username,
#         "answers": request.answers
#     }

#     result = await survey_response_collection.insert_one(response_data)
#     return {"submission_id": str(result.inserted_id), "message": "Survey responses submitted successfully"}
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import motor.motor_asyncio
from bson import ObjectId

app = FastAPI(title="Alexa Survey FastAPI with MongoDB")

# MongoDB Setup
MONGO_DETAILS = "mongodb+srv://GenerateQuestions:GenerateQuestions%40123@cluster0.b3ymk.mongodb.net/test?tls=true"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
db = client.alexa_survey

# Collections
sessions_collection = db.get_collection("sessions")
answers_collection = db.get_collection("answers")
reports_collection = db.get_collection("reports")

# Models
class StartSurveyRequest(BaseModel):
    device_id: str
    survey_code: str

class AnswerRequest(BaseModel):
    session_id: str
    answer: str

class ReportRequest(BaseModel):
    session_id: str
    comment: str

# Endpoints

@app.post("/start_survey/")
async def start_survey(payload: StartSurveyRequest):
    session = await sessions_collection.insert_one({
        "device_id": payload.device_id,
        "survey_code": payload.survey_code,
        "current_question": 0,
        "completed": False
    })
    return {"session_id": str(session.inserted_id), "message": "Survey started."}

@app.post("/submit_answer/")
async def submit_answer(payload: AnswerRequest):
    session = await sessions_collection.find_one({"_id": ObjectId(payload.session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    await answers_collection.insert_one({
        "session_id": payload.session_id,
        "device_id": session['device_id'],
        "answer": payload.answer,
        "question_index": session['current_question']
    })

    await sessions_collection.update_one(
        {"_id": ObjectId(payload.session_id)},
        {"$inc": {"current_question": 1}}
    )

    return {"message": "Answer recorded."}

@app.get("/get_next_question/{session_id}")
async def get_next_question(session_id: str):
    session = await sessions_collection.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if session['completed']:
        return {"message": "Survey already completed."}

    # Placeholder - you can fetch real question logic here
    question_text = f"Question {session['current_question'] + 1}: Sample question text."
    return {"question": question_text}

@app.post("/finish_survey/{session_id}")
async def finish_survey(session_id: str):
    session = await sessions_collection.find_one({"_id": ObjectId(session_id)})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    await sessions_collection.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"completed": True}}
    )

    return {"message": "Survey finished successfully."}

@app.post("/report_question/")
async def report_question(payload: ReportRequest):
    await reports_collection.insert_one({
        "session_id": payload.session_id,
        "comment": payload.comment,
        "type": "question"
    })
    return {"message": "Question reported successfully."}

@app.post("/report_survey/")
async def report_survey(payload: ReportRequest):
    await reports_collection.insert_one({
        "session_id": payload.session_id,
        "comment": payload.comment,
        "type": "survey"
    })
    return {"message": "Survey reported successfully."}
