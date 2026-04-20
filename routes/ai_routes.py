from flask import Blueprint, request, jsonify
from ai.question_engine import generate_question
from ai.tts_engine import generate_voice
from ai.report_engine import generate_report
from models.interview import save_report
from utils.validation import QuestionRequest, ReportRequest
from pydantic import ValidationError

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/api/ai/question", methods=["POST"])
def question():
    try:
        data = QuestionRequest(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"error": "Invalid input", "details": str(e)}), 400

    role = data.role
    answer = data.answer
    question_history = data.question_history

    try:
        question_text = generate_question(role, answer, question_history)
        audio_url = generate_voice(question_text)

        return jsonify({
            "question": question_text,
            "audio": audio_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_bp.route("/api/ai/report", methods=["POST"])
def report():
    try:
        data = ReportRequest(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"error": "Invalid input", "details": str(e)}), 400

    role = data.role
    qa_history = data.qa_history
    room_id = data.room_id

    try:
        report_text = generate_report(role, qa_history)

        if room_id:
            import json
            save_report(room_id, report_text, json.dumps(qa_history))

        return jsonify({"report": report_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500