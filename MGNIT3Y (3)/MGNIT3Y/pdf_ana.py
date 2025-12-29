from flask import Flask, request, jsonify
import os
import re
import pdfplumber
import io
from datetime import datetime
import shap
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import warnings
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
import json
from threading import Thread
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Institution Configuration
INSTITUTION_CONFIG = {
    'name': 'Debaggurs City',
    'email': 'debaggursofficial@gmail.com',
    'phone': '+91-1234567890',
    'website': 'www.debaggurs.in',
    'address': 'Kolkata'
}

# Firebase configuration
firebase_config = {
    'api_key': os.environ.get("AIzaSyCRVtR5G9nhMYpYxWPPxsbJBxwe1ZkiLfs"),
    'auth_domain': os.environ.get("minorproject3y.firebaseapp.com"),
    'project_id': os.environ.get("minorproject3y"),
    'storage_bucket': os.environ.get("minorproject3y.firebasestorage.app"),
    'messaging_sender_id': os.environ.get("1011137898679"),
    'app_id': os.environ.get("1:1011137898679:web:dcb43af172a1bb6aa04532")
}

# Initialize Firebase
try:
    if not firebase_admin._apps:
        service_account_info = {
            "type": "service_account",
            "project_id": "minorproject3y",
            "private_key_id": "4a617da79ed07ee278dfd020162e0b7a7a90b2e5",
            "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDNBgb33nFVsx+g
d2cLiTU+C5b5yIW/dN01iGGEjnYXf5v1yE5lp9IujecQ8rTC2JFhOLXgOqU1gaiI
5vqcEO+8BuOUEonefm4R/6SHzU4HMvwA43wyePZ5F/pZahQNOmuR95JJdNQBUJty
hhloLYCL3dMNi/+AIUESYWUvXQwA7eGiYgzNgUvnCwyOBYEnA/ILJwERkIqT08nU
ZlUQXeQNl34RQ+bjFGj2XoFIU5IkgJs8OG0WLG6JTseorm3wDjpwFdg8Sp43+9+i
RmFlNpK0jvP/WVgSyJIduNCxZQFRwytJQWzDkigmFrwkqBfEoiCeYaD4nOPzKRoO
KmmXOZK3AgMBAAECggEAAiTEi3B4EqqJkAFk7TLzgMg8rxge2zV+mGHqU/6XGiqv
EKfO8EFhRqXHLQna0qVgzt0WJxCV6IKINOjmOo+6U7wtXvhpUUhU52YpMzq9E8gx
Pap4kL0y0E0W4R5zl+Ls0TmNU3ODXiwmzpfYHwzWTHVogoGjqemg3/2Ll2cSprkm
hWxTmefWhjAFG6ugIhIdPyWCh+aAJdvV4jeyoWcSHaSJDJ3r9aJj9FjkwBwYAk/c
uOzuzikhiS2o11KfOrg1bSRu5CnuVD3bLlabovYyXoYVUU834k+zcZ7oM/+7/T8M
rM6GC8mD2bG0RN8OBXj/WJNJQrnVIU+EpiWtOKWREQKBgQD8x9CVPi6WJ6Dev47Q
o/GXNhmDulpQEFo2XdotaGiO0nKjC5YfrfHsrfDXGSTvwqKexJ4oyHnZk2Cxavlv
uPonMAMxA3easx94c834PeGViJ/cwp+zZgNKn8f48Q0S5oyBRBpqA3bbLRkPGuFY
tJDpWvu2M0S5erDtad1vZTHeiQKBgQDPooB61eTrCePnb6B7UzMnl8o8wwveeS+y
/efzmt6On6YHdyPUE2vdbyx0oi9g7vh1IwHFniDy/h4mUAGqZpx33fOB2KrlUTwY
PMmdvj8Hx0QfpE2ZpH+2/t5FIIxn7fWlN45N5OzRpcLeQ1sl0EyFLGnsAv7N7hPl
8tfHI+mXPwKBgQDsWHcx034DbvH+0uRZN7A/TZn1jFu82E1A3+eK5UA9qY7922t2
G1FDli7FLwFWG4mpIPUv9KHZSO7zc63dQ/rAgSe6wB8oSap3GO/P1ywAgEnYQzDG
r+8L6vEyVU+ACIf+pQp9bNfIfhYcBWoFYm7LgQIwjScItSqQEJe1+8vw4QKBgFEY
ui+/7Soz8bTKL5cbduZm7dFvqOoa0RuK+hZ2jaiNCG7wBKlncIDLVES1t+WXUKmH
o8CIs3vU7vet1gi1DTXwFZTIiG8KnHsm+uRGkx25oYzuQnTZABz8TNoZDV3mXkRK
f6VC3ZBAuuzOyAHr6oc1QqWwwc6yx0jP4aFhEHJHAoGAKi7hNj3m7zbveiLUvegN
BLfUDb7p3KULr7Cmol7131//KqdakSTTx/415p4ATZ7jLsdvUoyvQIP2+6FduX9U
OJQaVV8tpD+T4pdAT5b000S0zTISWkrdAv+Z/2kSUn993xqU4I1Y27qO+AJfeKmD
DN0IPbEnknZy56HhDZmBMzM=
-----END PRIVATE KEY-----\n""",
            "client_email": "firebase-adminsdk-fbsvc@minorproject3y.iam.gserviceaccount.com",
            "client_id": "117739492234885769448",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40minorproject3y.iam.gserviceaccount.com"
        }

        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Firebase connected successfully to project: minorproject3y")

except Exception as e:
    print(f"⚠ Firebase connection failed: {e}")
    db = None

# In-memory storage for student profiles (fallback)
student_profiles = {}

# Email configuration only
email_config = {
    'provider': 'firebase'
}

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Resume Evaluator | AI-Powered Candidate Assessment</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { font-family: 'Inter', sans-serif; }
    .hidden { display: none; }
    .glass-effect {
      background: rgba(255, 255, 255, 0.25);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(255, 255, 255, 0.18);
    }
    .gradient-bg {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .gradient-card {
      background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    }
    .score-ring { transition: stroke-dashoffset 1s ease-in-out; }
    .feature-bar { transition: width 0.8s ease-in-out; }
    .pulse-glow { animation: pulse-glow 2s infinite; }
    @keyframes pulse-glow {
      0%, 100% { box-shadow: 0 0 5px rgba(59, 130, 246, 0.5); }
      50% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.8); }
    }
    .nav-active {
      background: linear-gradient(135deg, #4f46e5, #7c3aed);
      color: white;
      transform: translateY(-2px);
      box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4);
    }
    .page { display: none; animation: fadeIn 0.5s ease-in; }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .page-active { display: block; }
    .candidate-card {
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      border-left: 4px solid transparent;
    }
    .candidate-card:hover {
      transform: translateY(-5px);
      box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    .rank-1 { border-left-color: #f59e0b; background: linear-gradient(135deg, #fff7ed, #fed7aa); }
    .rank-2 { border-left-color: #6b7280; background: linear-gradient(135deg, #f9fafb, #e5e7eb); }
    .rank-3 { border-left-color: #92400e; background: linear-gradient(135deg, #fef3c7, #fde68a); }
    .status-badge {
      padding: 0.5rem 1rem;
      border-radius: 9999px;
      font-weight: 600;
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .shap-force-bar {
      height: 8px;
      border-radius: 4px;
      background: #e5e7eb;
      margin: 0.5rem 0;
      overflow: hidden;
    }
    .shap-positive { background: linear-gradient(90deg, #10b981, #059669); }
    .shap-negative { background: linear-gradient(90deg, #ef4444, #dc2626); }
    .skill-tag {
      display: inline-flex;
      align-items: center;
      padding: 0.5rem 1rem;
      border-radius: 25px;
      font-size: 0.875rem;
      font-weight: 500;
      margin: 0.25rem;
      transition: all 0.3s ease;
    }
    .skill-tag:hover { transform: scale(1.05); }
    .loading-dots { display: inline-block; }
    .loading-dots:after {
      content: '...';
      animation: dots 1.5s steps(4, end) infinite;
    }
    @keyframes dots {
      0%, 20% { color: rgba(0,0,0,0); text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }
      40% { color: white; text-shadow: .25em 0 0 rgba(0,0,0,0), .5em 0 0 rgba(0,0,0,0); }
      60% { text-shadow: .25em 0 0 white, .5em 0 0 rgba(0,0,0,0); }
      80%, 100% { text-shadow: .25em 0 0 white, .5em 0 0 white; }
    }
    .profile-section {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      border-radius: 1rem;
      padding: 2rem;
      color: white;
      margin-bottom: 2rem;
    }
    .notification-badge {
      position: absolute;
      top: -8px;
      right: -8px;
      background: #ef4444;
      color: white;
      border-radius: 50%;
      width: 20px;
      height: 20px;
      font-size: 0.75rem;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  </style>
</head>

<body class="bg-gray-50">
  <!-- Navigation -->
  <nav class="gradient-bg shadow-xl">
    <div class="container mx-auto px-4">
      <div class="flex justify-between items-center py-4">
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-white rounded-lg">
            <i class="fas fa-robot text-2xl text-purple-600"></i>
          </div>
          <div>
            <h1 class="text-xl font-bold text-white">Debaggurs Resume Evaluator</h1>
            <p class="text-sm text-purple-100">AI-Powered Candidate Assessment</p>
          </div>
        </div>
        <div class="flex space-x-1 bg-white/20 rounded-xl p-1 backdrop-blur-sm">
          <button id="nav-single" class="nav-btn px-6 py-3 rounded-lg font-semibold transition-all duration-300 nav-active" data-page="single">
            <i class="fas fa-user-check mr-2"></i>Single Analysis
          </button>
          <button id="nav-multiple" class="nav-btn px-6 py-3 rounded-lg font-semibold transition-all duration-300" data-page="multiple">
            <i class="fas fa-trophy mr-2"></i>Candidate Ranking
          </button>
          <button id="nav-profiles" class="nav-btn px-6 py-3 rounded-lg font-semibold transition-all duration-300" data-page="profiles">
            <i class="fas fa-users mr-2"></i>Student Profiles
          </button>
          <button id="nav-notifications" class="nav-btn px-6 py-3 rounded-lg font-semibold transition-all duration-300" data-page="notifications">
            <i class="fas fa-cog mr-2"></i>Settings
          </button>
        </div>
      </div>
    </div>
  </nav>

  <div class="container mx-auto px-4 py-8">
    <!-- Single Resume Analysis Page -->
    <div id="page-single" class="page page-active">
      <!-- Hero Section -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center px-4 py-2 rounded-full bg-blue-100 text-blue-800 text-sm font-semibold mb-4">
          <i class="fas fa-star mr-2"></i>
          Debaggurs AI-Powered Resume Screening
        </div>
        <h2 class="text-4xl font-bold text-gray-800 mb-4">
          Smart Resume Analysis with 
          <span class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Transparent AI</span>
        </h2>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <!-- Input Section -->
        <div class="gradient-card rounded-2xl shadow-xl p-8 border border-gray-100">
          <div class="flex items-center mb-6">
            <div class="p-3 bg-blue-100 rounded-xl mr-4">
              <i class="fas fa-upload text-2xl text-blue-600"></i>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-800">Upload & Analyze</h3>
              <p class="text-gray-600">Upload resume and job description for smart analysis</p>
            </div>
          </div>

          <form id="uploadFormSingle" enctype="multipart/form-data">
            <!-- Resume Upload -->
            <div class="mb-6">
              <label class="block text-gray-700 mb-3 font-semibold">
                <i class="fas fa-file-alt mr-2 text-blue-500"></i>
                Resume Document
              </label>
              <div class="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center transition-all duration-300 hover:border-blue-400 hover:bg-blue-50/50">
                <i class="fas fa-file-pdf text-4xl text-red-500 mb-3"></i>
                <i class="fas fa-file-text text-4xl text-green-500 mb-3"></i>
                <p class="text-gray-700 font-medium mb-2">Drag & drop your resume here</p>
                <p class="text-sm text-gray-500 mb-4">Supports PDF and TXT formats</p>
                <input type="file" id="resume" name="resume" accept=".pdf,.txt" class="block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-6 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-blue-500 file:to-purple-600 file:text-white hover:file:from-blue-600 hover:file:to-purple-700 transition-all" required>
                <div id="fileInfoSingle" class="file-info hidden mt-4 p-3 bg-blue-50 rounded-lg">
                  <i class="fas fa-check-circle text-green-500 mr-2"></i>
                  <span id="fileNameSingle" class="text-sm text-blue-700 font-medium"></span>
                </div>
              </div>
            </div>

            <!-- Job Description -->
            <div class="mb-6">
              <label class="block text-gray-700 mb-3 font-semibold">
                <i class="fas fa-briefcase mr-2 text-purple-500"></i>
                Job Description
              </label>
              <textarea id="job_description_single" name="job_description" rows="6" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all" placeholder="Paste the complete job description here...">We are looking for a Python developer with experience in web development. Required skills: Python, JavaScript, HTML, CSS, SQL. Nice to have: React, Docker, AWS. Minimum 2 years of experience required.</textarea>
            </div>

            <!-- Salary Configuration -->
            <div class="mb-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-200">
              <h4 class="font-bold text-green-800 mb-4 flex items-center">
                <i class="fas fa-money-bill-wave mr-2"></i>
                Salary Prediction Settings
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm text-green-700 mb-2 font-semibold">Base Salary (₹)</label>
                  <input type="number" id="base_salary_single" name="base_salary" value="600000" class="w-full px-4 py-3 border border-green-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 text-sm font-medium">
                </div>
                <div>
                  <label class="block text-sm text-green-700 mb-2 font-semibold">Location Factor</label>
                  <select id="location_factor_single" name="location_factor" class="w-full px-4 py-3 border border-green-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 text-sm font-medium">
                    <option value="1.0">Metro Cities (Delhi, Mumbai, Chennai)</option>
                    <option value="1.2">Tech Hubs (Bangalore, Hyderabad, Pune)</option>
                    <option value="0.8">Tier-2 Cities</option>
                  </select>
                </div>
              </div>
            </div>

            <button type="submit" class="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center group">
              <i class="fas fa-brain mr-3 group-hover:scale-110 transition-transform"></i>
              Analyze with Smart AI
              <i class="fas fa-arrow-right ml-2 group-hover:translate-x-1 transition-transform"></i>
            </button>
          </form>
        </div>

        <!-- Results Section -->
        <div class="gradient-card rounded-2xl shadow-xl p-8 border border-gray-100">
          <div class="flex items-center mb-6">
            <div class="p-3 bg-green-100 rounded-xl mr-4">
              <i class="fas fa-chart-bar text-2xl text-green-600"></i>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-800">Analysis Results</h3>
              <p class="text-gray-600">Comprehensive insights with clear explanations</p>
            </div>
          </div>

          <div id="results-single" class="hidden">
            <!-- Decision Card -->
            <div id="decision-container-single" class="mb-8 rounded-2xl p-8 text-center text-white shadow-lg">
              <div class="flex items-center justify-center mb-4">
                <i id="decision-icon-single" class="fas text-4xl mr-4"></i>
                <div>
                  <h4 id="decision-title-single" class="text-3xl font-bold mb-2"></h4>
                  <p id="decision-message-single" class="text-xl opacity-90"></p>
                </div>
              </div>
              <p id="decision-reason-single" class="text-lg opacity-80"></p>
            </div>

            <!-- Student Profile & Actions -->
            <div id="student-actions" class="mb-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl p-6 border border-indigo-200">
              <div class="flex justify-between items-center">
                <div>
                  <h4 class="font-bold text-indigo-800 mb-1" id="student-info">Student: -</h4>
                  <p class="text-sm text-indigo-600" id="student-email-display">Email: -</p>
                  <p class="text-sm text-indigo-600" id="student-phone-display">Phone: -</p>

                  <input type="text" id="student_name" class="hidden">
                  <input type="email" id="student_email" class="hidden">
                  <input type="text" id="student_phone" class="hidden">
                </div>
                <div class="flex space-x-3">
                  <button id="save-profile-btn" class="bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-lg font-semibold transition-all flex items-center">
                    <i class="fas fa-save mr-2"></i>Save Profile
                  </button>
                  <button id="send-email-btn" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-semibold transition-all flex items-center">
                    <i class="fas fa-paper-plane mr-2"></i>Send Email
                  </button>
                </div>
              </div>
            </div>

            <!-- Score & Key Metrics -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <!-- Match Score -->
              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 text-center">
                <div class="inline-block relative">
                  <svg class="w-24 h-24">
                    <circle class="text-gray-200" stroke-width="8" stroke="currentColor" fill="transparent" r="44" cx="48" cy="48"/>
                    <circle class="text-green-500 score-ring" stroke-width="8" stroke-linecap="round" stroke="currentColor" fill="transparent" r="44" cx="48" cy="48" id="score-circle-single" stroke-dasharray="276,276" stroke-dashoffset="276"/>
                  </svg>
                  <div class="absolute inset-0 flex items-center justify-center">
                    <span id="match-score-single" class="text-2xl font-bold">0%</span>
                  </div>
                </div>
                <p class="text-gray-600 font-semibold mt-3">Match Score</p>
              </div>

              <!-- Confidence Score -->
              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <div class="flex items-center mb-4">
                  <i class="fas fa-shield-alt text-blue-500 text-xl mr-3"></i>
                  <span class="font-bold text-gray-800">AI Confidence</span>
                </div>
                <div class="mb-2">
                  <div class="flex justify-between items-center mb-1">
                    <span class="text-sm font-medium text-gray-600">Confidence Level</span>
                    <span id="confidence-score-single" class="text-sm font-bold text-blue-600">0%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-3">
                    <div id="confidence-bar-single" class="bg-gradient-to-r from-blue-500 to-cyan-500 h-3 rounded-full feature-bar" style="width: 0%"></div>
                  </div>
                </div>
              </div>

              <!-- Salary Prediction -->
              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <div class="flex items-center mb-4">
                  <i class="fas fa-rupee-sign text-green-500 text-xl mr-3"></i>
                  <span class="font-bold text-gray-800">Salary Prediction</span>
                </div>
                <div class="text-center">
                  <div class="text-2xl font-bold text-green-600 mb-1" id="salary-median-single">₹0</div>
                  <div class="text-sm text-gray-600 mb-3" id="salary-range-single">Range: ₹0 - ₹0</div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-gradient-to-r from-green-400 to-green-600 h-2 rounded-full" id="salary-bar-single" style="width: 50%"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Feature Analysis Section -->
            <div class="mb-8 bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl p-6 border border-purple-200 shadow-lg">
              <h4 class="font-bold text-purple-800 mb-4 flex items-center">
                <i class="fas fa-chess-board mr-2"></i>
                Feature Impact Analysis
                <span class="ml-2 text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full font-semibold">
                  Clear & Understandable
                </span>
              </h4>
              
              <!-- Model Prediction -->
              <div class="mb-4 p-4 bg-white rounded-xl border border-purple-100">
                <div class="flex justify-between items-center mb-2">
                  <span class="font-semibold text-purple-700">AI Recommendation</span>
                  <span id="shap-prediction" class="px-4 py-2 rounded-full text-sm font-bold"></span>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span class="text-purple-600">Confidence Level</span>
                  <span id="shap-confidence" class="font-bold text-purple-700"></span>
                </div>
              </div>
              
              <!-- Feature Impact Visualization -->
              <div class="mb-4">
                <h5 class="font-semibold text-purple-700 mb-3">Key Factor Analysis</h5>
                <div id="shap-force-plot" class="space-y-3">
                  <!-- Feature visualization will be inserted here -->
                </div>
              </div>
              
              <!-- Top Influencers -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="bg-green-50 rounded-xl p-4 border border-green-200">
                  <h6 class="font-semibold text-green-700 mb-3 flex items-center">
                    <i class="fas fa-arrow-up mr-2"></i>
                    Positive Factors
                  </h6>
                  <ul id="shap-positive-features" class="space-y-2">
                    <!-- Positive features will be inserted here -->
                  </ul>
                </div>
                
                <div class="bg-red-50 rounded-xl p-4 border border-red-200">
                  <h6 class="font-semibold text-red-700 mb-3 flex items-center">
                    <i class="fas fa-arrow-down mr-2"></i>
                    Areas to Improve
                  </h6>
                  <ul id="shap-negative-features" class="space-y-2">
                    <!-- Negative features will be inserted here -->
                  </ul>
                </div>
              </div>
            </div>

            <!-- Skills & Experience -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <h4 class="font-bold text-gray-800 mb-4 flex items-center">
                  <i class="fas fa-cogs text-blue-500 mr-2"></i>
                  Skills Analysis
                </h4>
                <div id="skills-found-single" class="flex flex-wrap gap-2">
                  <!-- Skills will be inserted here -->
                </div>
              </div>

              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <h4 class="font-bold text-gray-800 mb-4 flex items-center">
                  <i class="fas fa-briefcase text-purple-500 mr-2"></i>
                  Experience
                </h4>
                <p id="experience-single" class="text-gray-700 text-lg font-semibold"></p>
              </div>
            </div>

            <!-- Strengths & Improvements -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 border border-green-200">
                <h4 class="font-bold text-green-800 mb-4 flex items-center">
                  <i class="fas fa-check-circle mr-2"></i>
                  Key Strengths
                </h4>
                <ul id="strengths-single" class="space-y-2 text-green-700">
                  <!-- Strengths will be inserted here -->
                </ul>
              </div>

              <div class="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl p-6 border border-orange-200">
                <h4 class="font-bold text-red-800 mb-4 flex items-center">
                  <i class="fas fa-lightbulb mr-2"></i>
                  Development Areas
                </h4>
                <ul id="gaps-single" class="space-y-2 text-red-700">
                  <!-- Gaps will be inserted here -->
                </ul>
              </div>
            </div>
          </div>

          <!-- Loading State -->
          <div id="loading-single" class="hidden text-center py-12">
            <div class="inline-flex items-center justify-center p-4 bg-blue-100 rounded-full mb-4">
              <i class="fas fa-spinner fa-spin text-3xl text-blue-600"></i>
            </div>
            <h4 class="text-xl font-bold text-gray-800 mb-2">Analyzing Resume with AI</h4>
            <p class="text-gray-600">Processing with smart analysis<span class="loading-dots"></span></p>
          </div>

          <!-- Empty State -->
          <div id="placeholder-single" class="text-center py-16">
            <div class="inline-flex items-center justify-center p-6 bg-gray-100 rounded-full mb-6">
              <i class="fas fa-file-alt text-4xl text-gray-400"></i>
            </div>
            <h4 class="text-2xl font-bold text-gray-400 mb-3">Ready for Analysis</h4>
            <p class="text-gray-500 max-w-md mx-auto">Upload a resume and job description to see smart insights and clear explanations</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Multiple Resume Ranking Page -->
    <div id="page-multiple" class="page">
      <!-- Hero Section -->
      <div class="text-center mb-12">
        <div class="inline-flex items-center px-4 py-2 rounded-full bg-purple-100 text-purple-800 text-sm font-semibold mb-4">
          <i class="fas fa-users mr-2"></i>
          Multi-Candidate Analysis
        </div>
        <h2 class="text-4xl font-bold text-gray-800 mb-4">
          Candidate Comparison & 
          <span class="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">Ranking System</span>
        </h2>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">Compare multiple candidates with AI-powered ranking and salary analysis</p>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <!-- Input Section -->
        <div class="gradient-card rounded-2xl shadow-xl p-8 border border-gray-100">
          <div class="flex items-center mb-6">
            <div class="p-3 bg-purple-100 rounded-xl mr-4">
              <i class="fas fa-users text-2xl text-purple-600"></i>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-800">Upload Candidates</h3>
              <p class="text-gray-600">Upload multiple resumes for comparison</p>
            </div>
          </div>

          <form id="uploadFormMultiple" enctype="multipart/form-data">
            <!-- Multiple Resume Upload -->
            <div class="mb-6">
              <label class="block text-gray-700 mb-3 font-semibold">
                <i class="fas fa-files mr-2 text-purple-500"></i>
                Multiple Resumes
              </label>
              <div class="border-2 border-dashed border-gray-300 rounded-2xl p-8 text-center transition-all duration-300 hover:border-purple-400 hover:bg-purple-50/50">
                <i class="fas fa-file-pdf text-4xl text-red-500 mb-3"></i>
                <i class="fas fa-file-text text-4xl text-green-500 mb-3"></i>
                <p class="text-gray-700 font-medium mb-2">Select multiple resume files</p>
                <p class="text-sm text-gray-500 mb-4">Drag & drop or click to select multiple PDF/TXT files</p>
                <input type="file" id="resumes" name="resumes" accept=".pdf,.txt" multiple class="block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-6 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gradient-to-r file:from-purple-500 file:to-pink-600 file:text-white hover:file:from-purple-600 hover:file:to-pink-700 transition-all" required>
                <div id="fileInfoMultiple" class="file-info hidden mt-4 p-3 bg-purple-50 rounded-lg">
                  <i class="fas fa-check-circle text-green-500 mr-2"></i>
                  <span id="fileNameMultiple" class="text-sm text-purple-700 font-medium"></span>
                </div>
              </div>
            </div>

            <!-- Job Description -->
            <div class="mb-6">
              <label class="block text-gray-700 mb-3 font-semibold">
                <i class="fas fa-briefcase mr-2 text-pink-500"></i>
                Job Description
              </label>
              <textarea id="job_description_multiple" name="job_description" rows="6" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all" placeholder="Paste the job description for comparison...">We are looking for a Python developer with experience in web development. Required skills: Python, JavaScript, HTML, CSS, SQL. Nice to have: React, Docker, AWS. Minimum 2 years of experience required.</textarea>
            </div>

            <!-- Salary Configuration -->
            <div class="mb-6 bg-gradient-to-r from-pink-50 to-rose-50 rounded-2xl p-6 border border-pink-200">
              <h4 class="font-bold text-pink-800 mb-4 flex items-center">
                <i class="fas fa-money-bill-wave mr-2"></i>
                Salary Configuration
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm text-pink-700 mb-2 font-semibold">Base Salary (₹)</label>
                  <input type="number" id="base_salary_multiple" name="base_salary" value="600000" class="w-full px-4 py-3 border border-pink-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 text-sm font-medium">
                </div>
                <div>
                  <label class="block text-sm text-pink-700 mb-2 font-semibold">Location Factor</label>
                  <select id="location_factor_multiple" name="location_factor" class="w-full px-4 py-3 border border-pink-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-pink-500 text-sm font-medium">
                    <option value="1.0">Metro Cities (Delhi, Mumbai, Chennai)</option>
                    <option value="1.2">Tech Hubs (Bangalore, Hyderabad, Pune)</option>
                    <option value="0.8">Tier-2 Cities</option>
                  </select>
                </div>
              </div>
            </div>

            <button type="submit" class="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center group">
              <i class="fas fa-trophy mr-3 group-hover:scale-110 transition-transform"></i>
              Compare Candidates & Rank
              <i class="fas fa-arrow-right ml-2 group-hover:translate-x-1 transition-transform"></i>
            </button>
          </form>
        </div>

        <!-- Results Section -->
        <div class="gradient-card rounded-2xl shadow-xl p-8 border border-gray-100">
          <div class="flex items-center mb-6">
            <div class="p-3 bg-yellow-100 rounded-xl mr-4">
              <i class="fas fa-ranking-star text-2xl text-yellow-600"></i>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-800">Ranking Results</h3>
              <p class="text-gray-600">Smart candidate comparison</p>
            </div>
          </div>

          <!-- Summary Stats -->
          <div id="summary-stats" class="hidden grid grid-cols-3 gap-4 mb-8">
            <div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-6 text-center border border-blue-200">
              <div class="text-3xl font-bold text-blue-600 mb-2" id="total-candidates">0</div>
              <div class="text-sm text-blue-800 font-semibold">Candidates</div>
            </div>
            <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-6 text-center border border-green-200">
              <div class="text-3xl font-bold text-green-600 mb-2" id="avg-salary">₹0</div>
              <div class="text-sm text-green-800 font-semibold">Avg Salary</div>
            </div>
            <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 text-center border border-purple-200">
              <div class="text-3xl font-bold text-purple-600 mb-2" id="avg-score">0%</div>
              <div class="text-sm text-purple-800 font-semibold">Avg Score</div>
            </div>
          </div>

          <!-- Candidates Ranking -->
          <div id="ranking-results" class="hidden">
            <div class="space-y-4">
              <!-- Candidate cards will be inserted here -->
            </div>
          </div>

          <!-- Loading State -->
          <div id="loading-multiple" class="hidden text-center py-12">
            <div class="inline-flex items-center justify-center p-4 bg-purple-100 rounded-full mb-4">
              <i class="fas fa-spinner fa-spin text-3xl text-purple-600"></i>
            </div>
            <h4 class="text-xl font-bold text-gray-800 mb-2">Analyzing Candidates</h4>
            <p class="text-gray-600">Processing multiple resumes with AI<span class="loading-dots"></span></p>
            <p class="text-sm text-gray-500 mt-2" id="progress-text">Processing 0/0 files</p>
          </div>

          <!-- Empty State -->
          <div id="placeholder-multiple" class="text-center py-16">
            <div class="inline-flex items-center justify-center p-6 bg-gray-100 rounded-full mb-6">
              <i class="fas fa-users text-4xl text-gray-400"></i>
            </div>
            <h4 class="text-2xl font-bold text-gray-400 mb-3">Compare Candidates</h4>
            <p class="text-gray-500 max-w-md mx-auto">Upload multiple resumes to see smart ranking and comparison</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Student Profiles Page -->
    <div id="page-profiles" class="page">
      <div class="text-center mb-12">
        <div class="inline-flex items-center px-4 py-2 rounded-full bg-green-100 text-green-800 text-sm font-semibold mb-4">
          <i class="fas fa-user-graduate mr-2"></i>
          Student Profile Management
        </div>
        <h2 class="text-4xl font-bold text-gray-800 mb-4">
          Student Profiles & 
          <span class="bg-gradient-to-r from-green-600 to-teal-600 bg-clip-text text-transparent">Communication Hub</span>
        </h2>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">Manage student profiles and send automated notifications</p>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <!-- Profile List -->
        <div class="gradient-card rounded-2xl shadow-xl p-6 border border-gray-100">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-bold text-gray-800">Student Profiles</h3>
            <span class="bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-semibold" id="profile-count">0 profiles</span>
          </div>
          <div class="space-y-4" id="profiles-list">
            <!-- Profiles will be loaded here -->
          </div>
        </div>

        <!-- Profile Details -->
        <div class="gradient-card rounded-2xl shadow-xl p-6 border border-gray-100 xl:col-span-2">
          <div class="flex items-center mb-6">
            <div class="p-3 bg-indigo-100 rounded-xl mr-4">
              <i class="fas fa-user-edit text-2xl text-indigo-600"></i>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-800">Profile Details</h3>
              <p class="text-gray-600">View and manage student information</p>
            </div>
          </div>

          <div id="profile-details" class="hidden">
            <div class="profile-section">
              <div class="flex justify-between items-start mb-4">
                <div>
                  <h4 class="text-2xl font-bold text-white mb-2" id="profile-name">Student Name</h4>
                  <p class="text-blue-100" id="profile-email">email@example.com</p>
                  <p class="text-blue-100" id="profile-phone">Phone: -</p>
                </div>
                <div class="flex space-x-2">
                  <button class="bg-white text-indigo-600 px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-all">
                    <i class="fas fa-edit mr-2"></i>Edit
                  </button>
                  <button class="bg-red-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-red-600 transition-all">
                    <i class="fas fa-trash mr-2"></i>Delete
                  </button>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <h4 class="font-bold text-gray-800 mb-4 flex items-center">
                  <i class="fas fa-chart-line text-green-500 mr-2"></i>
                  Performance Metrics
                </h4>
                <div class="space-y-3">
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm text-gray-600">Match Score</span>
                      <span class="text-sm font-bold text-green-600" id="profile-score">0%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div class="bg-green-500 h-2 rounded-full" id="profile-score-bar" style="width: 0%"></div>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm text-gray-600">Experience</span>
                      <span class="text-sm font-bold text-blue-600" id="profile-experience">0 years</span>
                    </div>
                  </div>
                  <div>
                    <div class="flex justify-between mb-1">
                      <span class="text-sm text-gray-600">Status</span>
                      <span class="text-sm font-bold" id="profile-status">-</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-2xl p-6 shadow-lg border border-gray-100">
                <h4 class="font-bold text-gray-800 mb-4 flex items-center">
                  <i class="fas fa-cogs text-blue-500 mr-2"></i>
                  Skills & Technologies
                </h4>
                <div id="profile-skills" class="flex flex-wrap gap-2">
                  <!-- Skills will be inserted here -->
                </div>
              </div>
            </div>

            <!-- Communication Actions -->
            <div class="bg-gradient-to-r from-orange-50 to-amber-50 rounded-2xl p-6 border border-orange-200">
              <h4 class="font-bold text-orange-800 mb-4 flex items-center">
                <i class="fas fa-paper-plane mr-2"></i>
                Send Notification
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <button class="bg-green-500 hover:bg-green-600 text-white py-3 rounded-lg font-semibold transition-all flex items-center justify-center" onclick="sendEmail('accepted')">
                  <i class="fas fa-check-circle mr-2"></i>Accept
                </button>
                <button class="bg-yellow-500 hover:bg-yellow-600 text-white py-3 rounded-lg font-semibold transition-all flex items-center justify-center" onclick="sendEmail('special_interview')">
                  <i class="fas fa-hourglass-half mr-2"></i>Special Interview
                </button>
                <button class="bg-red-500 hover:bg-red-600 text-white py-3 rounded-lg font-semibold transition-all flex items-center justify-center" onclick="sendEmail('rejected')">
                  <i class="fas fa-times-circle mr-2"></i>Reject
                </button>
              </div>
              <div class="mt-4">
                <textarea id="custom-message" class="w-full px-4 py-3 border border-orange-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 text-sm" rows="3" placeholder="Add a custom message (optional)"></textarea>
              </div>
            </div>
          </div>

          <div id="profile-placeholder" class="text-center py-16">
            <div class="inline-flex items-center justify-center p-6 bg-gray-100 rounded-full mb-6">
              <i class="fas fa-user-graduate text-4xl text-gray-400"></i>
            </div>
            <h4 class="text-2xl font-bold text-gray-400 mb-3">Select a Profile</h4>
            <p class="text-gray-500">Choose a student profile from the list to view details and send notifications</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Page -->
    <div id="page-notifications" class="page">
      <div class="text-center mb-12">
        <div class="inline-flex items-center px-4 py-2 rounded-full bg-red-100 text-red-800 text-sm font-semibold mb-4">
          <i class="fas fa-cog mr-2"></i>
          System Settings
        </div>
        <h2 class="text-4xl font-bold text-gray-800 mb-4">
          System 
          <span class="bg-gradient-to-r from-red-600 to-pink-600 bg-clip-text text-transparent">Configuration</span>
        </h2>
        <p class="text-xl text-gray-600 max-w-3xl mx-auto">Configure system settings and connections</p>
      </div>

      <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <!-- Firebase Configuration -->
        <div class="gradient-card rounded-2xl shadow-xl p-8 border border-gray-100">
          <div class="flex items-center mb-6">
            <div class="p-3 bg-red-100 rounded-xl mr-4">
              <i class="fas fa-database text-2xl text-red-600"></i>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-800">Firebase Configuration</h3>
              <p class="text-gray-600">Set up Firebase for email and data storage</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="bg-green-50 border border-green-200 rounded-xl p-4">
              <div class="flex items-center">
                <i class="fas fa-check-circle text-green-500 text-xl mr-3"></i>
                <div>
                  <h4 class="font-semibold text-green-800">Firebase Status</h4>
                  <p class="text-green-600 text-sm" id="firebase-status">Checking...</p>
                </div>
              </div>
            </div>
          </div>

          <button onclick="testFirebase()" class="w-full bg-gradient-to-r from-red-500 to-orange-600 hover:from-red-600 hover:to-orange-700 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center group mt-6">
            <i class="fas fa-bolt mr-3 group-hover:scale-110 transition-transform"></i>
            Test Firebase Connection
            <i class="fas fa-arrow-right ml-2 group-hover:translate-x-1 transition-transform"></i>
          </button>
        </div>

        <!-- Email Configuration -->
        <div class="gradient-card rounded-2xl shadow-xl p-8 border border-gray-100">
          <div class="flex items-center mb-6">
            <div class="p-3 bg-blue-100 rounded-xl mr-4">
              <i class="fas fa-envelope text-2xl text-blue-600"></i>
            </div>
            <div>
              <h3 class="text-2xl font-bold text-gray-800">Email Configuration</h3>
              <p class="text-gray-600">Email service for candidate notifications</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="bg-green-50 border border-green-200 rounded-xl p-4">
              <div class="flex items-center">
                <i class="fas fa-check-circle text-green-500 text-xl mr-3"></i>
                <div>
                  <h4 class="font-semibold text-green-800">Email Status</h4>
                  <p class="text-green-600 text-sm">Email service is active via Firebase</p>
                </div>
              </div>
            </div>
          </div>

          <button onclick="testEmailService()" class="w-full bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center group mt-6">
            <i class="fas fa-envelope mr-3 group-hover:scale-110 transition-transform"></i>
            Test Email Service
            <i class="fas fa-arrow-right ml-2 group-hover:translate-x-1 transition-transform"></i>
          </button>
        </div>
      </div>

      <!-- Institution Configuration -->
      <div class="gradient-card rounded-2xl shadow-xl p-8 border border-gray-100 mt-8">
        <div class="flex items-center mb-6">
          <div class="p-3 bg-blue-100 rounded-xl mr-4">
            <i class="fas fa-university text-2xl text-blue-600"></i>
          </div>
          <div>
            <h3 class="text-2xl font-bold text-gray-800">Institution Settings</h3>
            <p class="text-gray-600">Configure institution details for communications</p>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm text-gray-700 mb-2 font-semibold">Institution Name</label>
            <input type="text" id="institution-name" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" placeholder="Your institution name">
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-2 font-semibold">Contact Email</label>
            <input type="email" id="institution-email" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" placeholder="contact@institution.com">
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-2 font-semibold">Contact Phone</label>
            <input type="text" id="institution-phone" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" placeholder="+91-9876543210">
          </div>
          <div>
            <label class="block text-sm text-gray-700 mb-2 font-semibold">Website</label>
            <input type="text" id="institution-website" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" placeholder="www.institution.com">
          </div>
        </div>
        <div class="mt-4">
          <label class="block text-sm text-gray-700 mb-2 font-semibold">Address</label>
          <textarea id="institution-address" class="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm" rows="2" placeholder="Full institution address"></textarea>
        </div>

        <button onclick="saveInstitutionConfig()" class="w-full bg-gradient-to-r from-blue-500 to-cyan-600 hover:from-blue-600 hover:to-cyan-700 text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl flex items-center justify-center group mt-6">
          <i class="fas fa-save mr-3 group-hover:scale-110 transition-transform"></i>
          Save Institution Settings
          <i class="fas fa-check ml-2 group-hover:scale-110 transition-transform"></i>
        </button>
      </div>
    </div>
  </div>

  <script>
    // Navigation functionality
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const targetPage = this.getAttribute('data-page');
        
        // Update active nav button
        document.querySelectorAll('.nav-btn').forEach(b => {
          b.classList.remove('nav-active');
        });
        this.classList.add('nav-active');
        
        // Show target page, hide others
        document.querySelectorAll('.page').forEach(page => {
          page.classList.remove('page-active');
        });
        document.getElementById(`page-${targetPage}`).classList.add('page-active');
        
        // Load data for specific pages
        if (targetPage === 'profiles') {
          loadStudentProfiles();
        } else if (targetPage === 'notifications') {
          loadNotificationSettings();
        }
      });
    });

    // File input handlers
    document.getElementById('resume').addEventListener('change', function(e) {
      const file = e.target.files[0];
      const fileInfo = document.getElementById('fileInfoSingle');
      const fileName = document.getElementById('fileNameSingle');
      
      if (file) {
        const fileSize = (file.size / 1024 / 1024).toFixed(2);
        fileName.textContent = `${file.name} (${fileSize} MB)`;
        fileInfo.classList.remove('hidden');
      } else {
        fileInfo.classList.add('hidden');
      }
    });

    document.getElementById('resumes').addEventListener('change', function(e) {
      const files = e.target.files;
      const fileInfo = document.getElementById('fileInfoMultiple');
      const fileName = document.getElementById('fileNameMultiple');
      
      if (files.length > 0) {
        const totalSize = Array.from(files).reduce((acc, file) => acc + file.size, 0) / 1024 / 1024;
        fileName.textContent = `${files.length} files selected (${totalSize.toFixed(2)} MB total)`;
        fileInfo.classList.remove('hidden');
      } else {
        fileInfo.classList.add('hidden');
      }
    });

    // Single Analysis Form Submission
    document.getElementById('uploadFormSingle').addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const resultsDiv = document.getElementById('results-single');
      const loadingDiv = document.getElementById('loading-single');
      const placeholderDiv = document.getElementById('placeholder-single');
      
      // Show loading, hide others
      loadingDiv.classList.remove('hidden');
      resultsDiv.classList.add('hidden');
      placeholderDiv.classList.add('hidden');
      
      try {
        console.log("Sending single analysis request...");
        
        const response = await fetch('/analyze-single', {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP error! status: ${response.status}. ${errorText}`);
        }
        
        const data = await response.json();
        console.log("Single analysis successful:", data);
        
        // Update UI with results
        updateSingleResults(data);
        
      } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
        
        // Show placeholder again
        loadingDiv.classList.add('hidden');
        placeholderDiv.classList.remove('hidden');
      }
    });

    // Multiple Analysis Form Submission
    document.getElementById('uploadFormMultiple').addEventListener('submit', async function(e) {
      e.preventDefault();
      
      const formData = new FormData(this);
      const resultsDiv = document.getElementById('ranking-results');
      const summaryDiv = document.getElementById('summary-stats');
      const loadingDiv = document.getElementById('loading-multiple');
      const placeholderDiv = document.getElementById('placeholder-multiple');
      
      // Show loading, hide others
      loadingDiv.classList.remove('hidden');
      resultsDiv.classList.add('hidden');
      summaryDiv.classList.add('hidden');
      placeholderDiv.classList.add('hidden');
      
      try {
        console.log("Sending multiple analysis request...");
        
        const response = await fetch('/analyze-multiple', {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`HTTP error! status: ${response.status}. ${errorText}`);
        }
        
        const data = await response.json();
        console.log("Multiple analysis successful:", data);
        
        // Update UI with ranking results
        updateRankingResults(data);
        
      } catch (error) {
        console.error('Error:', error);
        alert('Error: ' + error.message);
        
        // Show placeholder again
        loadingDiv.classList.add('hidden');
        placeholderDiv.classList.remove('hidden');
      }
    });

    // Save Profile Button
    document.getElementById('save-profile-btn').addEventListener('click', function() {
      const studentName = document.getElementById('student_name').value;
      const studentEmail = document.getElementById('student_email').value;
      const studentPhone = document.getElementById('student_phone').value;
      
      if (!studentName || !studentEmail) {
        alert('Please fill in student name and email before saving profile');
        return;
      }
      
      // Get analysis data from the current results
      const analysisData = window.currentAnalysisData;
      if (!analysisData) {
        alert('No analysis data available to save');
        return;
      }
      
      saveStudentProfile(studentName, studentEmail, studentPhone, analysisData);
    });

    // Send Email Button
    document.getElementById('send-email-btn').addEventListener('click', function() {
      const studentEmail = document.getElementById('student_email').value;
      const studentName = document.getElementById('student_name').value;
      
      if (!studentEmail) {
        alert('Please enter student email before sending notification');
        return;
      }
      
      const analysisData = window.currentAnalysisData;
      if (!analysisData) {
        alert('No analysis data available');
        return;
      }
      
      sendResultEmail(studentEmail, studentName, analysisData);
    });

    // Firebase and Email Functions
    async function testFirebase() {
      try {
        const response = await fetch('/test-firebase');
        const data = await response.json();
        
        if (data.success) {
          document.getElementById('firebase-status').textContent = 'Connected successfully!';
          document.getElementById('firebase-status').parentElement.className = 'bg-green-50 border border-green-200 rounded-xl p-4';
        } else {
          throw new Error(data.error || 'Connection failed');
        }
      } catch (error) {
        document.getElementById('firebase-status').textContent = 'Connection failed: ' + error.message;
        document.getElementById('firebase-status').parentElement.className = 'bg-red-50 border border-red-200 rounded-xl p-4';
      }
    }

    async function testEmailService() {
      try {
        const response = await fetch('/test-email-service');
        const data = await response.json();
        
        if (data.success) {
          alert('Email service is working correctly!');
        } else {
          throw new Error(data.error || 'Email service test failed');
        }
      } catch (error) {
        alert('Email service test failed: ' + error.message);
      }
    }

    async function saveInstitutionConfig() {
      const config = {
        name: document.getElementById('institution-name').value,
        email: document.getElementById('institution-email').value,
        phone: document.getElementById('institution-phone').value,
        website: document.getElementById('institution-website').value,
        address: document.getElementById('institution-address').value
      };
      
      try {
        const response = await fetch('/save-institution-config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config)
        });
        
        if (response.ok) {
          alert('Institution configuration saved successfully!');
        } else {
          throw new Error('Failed to save institution configuration');
        }
      } catch (error) {
        alert('Error: ' + error.message);
      }
    }

    async function loadNotificationSettings() {
      try {
        // Load institution config
        const instResponse = await fetch('/get-institution-config');
        const instConfig = await instResponse.json();
        
        if (instConfig.name) {
          document.getElementById('institution-name').value = instConfig.name || '';
          document.getElementById('institution-email').value = instConfig.email || '';
          document.getElementById('institution-phone').value = instConfig.phone || '';
          document.getElementById('institution-website').value = instConfig.website || '';
          document.getElementById('institution-address').value = instConfig.address || '';
        }
        
        // Test Firebase status
        await testFirebase();
      } catch (error) {
        console.error('Error loading notification settings:', error);
      }
    }

    function updateSingleResults(data) {
      window.currentAnalysisData = data;
      
      const studentName = data.extracted_name || 'Not Found';
      const studentEmail = data.extracted_email || 'Not Found';
      const studentPhone = data.extracted_phone || 'Not Found';
      
      // Update student info display
      document.getElementById('student-actions').classList.remove('hidden');
      document.getElementById('student-info').textContent = `Student: ${studentName}`;
      document.getElementById('student-email-display').textContent = `Email: ${studentEmail}`;
      document.getElementById('student-phone-display').textContent = `Phone: ${studentPhone}`;

      document.getElementById('student_name').value = studentName;
      document.getElementById('student_email').value = studentEmail;
      document.getElementById('student_phone').value = studentPhone;
      
      updateSingleDecision(data.decision, data.match_score, data.decision_reason);
      
      const score = data.match_score || 0;
      document.getElementById('match-score-single').textContent = score + '%';
      
      const circle = document.getElementById('score-circle-single');
      const circumference = 276;
      const offset = circumference - (score / 100) * circumference;
      circle.style.strokeDashoffset = offset;
      
      const confidence = data.confidence_score || 75;
      document.getElementById('confidence-score-single').textContent = confidence + '%';
      document.getElementById('confidence-bar-single').style.width = confidence + '%';
      
      const salary = data.salary_range;
      document.getElementById('salary-median-single').textContent = `₹${formatIndianNumber(salary.median)}`;
      document.getElementById('salary-range-single').textContent = `Range: ₹${formatIndianNumber(salary.low)} - ₹${formatIndianNumber(salary.high)}`;
      
      const salaryWidth = ((salary.median - salary.low) / (salary.high - salary.low)) * 100;
      document.getElementById('salary-bar-single').style.width = salaryWidth + '%';
      
      const skillsContainer = document.getElementById('skills-found-single');
      skillsContainer.innerHTML = "";
      (data.skills_found || []).forEach(skill => {
        const skillElement = document.createElement('span');
        skillElement.className = 'skill-tag bg-blue-100 text-blue-800 hover:bg-blue-200';
        skillElement.textContent = skill;
        skillsContainer.appendChild(skillElement);
      });
      
      document.getElementById('experience-single').textContent = `${data.experience_years || 0} years of experience`;
      
      updateSingleList('strengths-single', data.strengths || []);
      updateSingleList('gaps-single', data.gaps || []);
      
      if (data.shap_analysis) {
        updateSHAPComponents(data.shap_analysis);
      }
      
      document.getElementById('results-single').classList.remove('hidden');
      document.getElementById('loading-single').classList.add('hidden');
    }

    function formatIndianNumber(num) {
      if (num >= 10000000) {
        return (num / 10000000).toFixed(1) + ' Cr';
      } else if (num >= 100000) {
        return (num / 100000).toFixed(1) + ' L';
      } else {
        return num.toLocaleString('en-IN');
      }
    }

    function updateSHAPComponents(shapData) {
      const predictionElement = document.getElementById('shap-prediction');
      const confidenceElement = document.getElementById('shap-confidence');
      
      if (shapData.prediction === 'accepted') {
        predictionElement.textContent = 'ACCEPTED';
        predictionElement.className = 'px-4 py-2 rounded-full text-sm font-bold bg-green-100 text-green-800';
      } else if (shapData.prediction === 'special_interview') {
        predictionElement.textContent = 'SPECIAL INTERVIEW';
        predictionElement.className = 'px-4 py-2 rounded-full text-sm font-bold bg-yellow-100 text-yellow-800';
      } else {
        predictionElement.textContent = 'REJECTED';
        predictionElement.className = 'px-4 py-2 rounded-full text-sm font-bold bg-red-100 text-red-800';
      }
      
      confidenceElement.textContent = shapData.confidence + '%';
      
      updateSHAPFeatureVisualization(shapData.feature_importance);
      updateSHAPFeatureLists(shapData.feature_importance);
    }

    function updateSHAPFeatureVisualization(featureImportance) {
      const container = document.getElementById('shap-force-plot');
      container.innerHTML = '';
      
      if (!featureImportance) return;
      
      const features = Object.entries(featureImportance)
        .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
        .slice(0, 8);
      
      features.forEach(([feature, value]) => {
        const isPositive = value > 0;
        const width = Math.min(Math.abs(value) * 3, 100);
        
        const featureDiv = document.createElement('div');
        featureDiv.className = 'bg-white rounded-lg p-4 border border-gray-200';
        
        featureDiv.innerHTML = `
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium text-gray-800 capitalize">${feature.replace(/_/g, ' ')}</span>
            <span class="font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}">
              ${isPositive ? '+' : ''}${value.toFixed(1)}%
            </span>
          </div>
          <div class="shap-force-bar">
            <div class="h-full rounded-full ${isPositive ? 'shap-positive' : 'shap-negative'}" style="width: ${width}%"></div>
          </div>
        `;
        
        container.appendChild(featureDiv);
      });
    }

    function updateSHAPFeatureLists(featureImportance) {
      const positiveList = document.getElementById('shap-positive-features');
      const negativeList = document.getElementById('shap-negative-features');
      
      positiveList.innerHTML = '';
      negativeList.innerHTML = '';
      
      if (!featureImportance) return;
      
      const features = Object.entries(featureImportance);
      const positiveFeatures = features.filter(([_, score]) => score > 0)
                                     .sort((a, b) => b[1] - a[1])
                                     .slice(0, 5);
      
      const negativeFeatures = features.filter(([_, score]) => score < 0)
                                     .sort((a, b) => a[1] - b[1])
                                     .slice(0, 5);
      
      positiveFeatures.forEach(([feature, score]) => {
        const li = document.createElement('li');
        li.className = 'flex justify-between items-center bg-green-100/50 p-2 rounded-lg';
        li.innerHTML = `
          <span class="text-sm font-medium text-green-800 capitalize">${feature.replace(/_/g, ' ')}</span>
          <span class="text-sm font-bold text-green-600">+${score.toFixed(1)}%</span>
        `;
        positiveList.appendChild(li);
      });
      
      negativeFeatures.forEach(([feature, score]) => {
        const li = document.createElement('li');
        li.className = 'flex justify-between items-center bg-red-100/50 p-2 rounded-lg';
        li.innerHTML = `
          <span class="text-sm font-medium text-red-800 capitalize">${feature.replace(/_/g, ' ')}</span>
          <span class="text-sm font-bold text-red-600">${score.toFixed(1)}%</span>
        `;
        negativeList.appendChild(li);
      });
    }

    function updateSingleDecision(decision, score, reason) {
      const container = document.getElementById('decision-container-single');
      const icon = document.getElementById('decision-icon-single');
      const title = document.getElementById('decision-title-single');
      const message = document.getElementById('decision-message-single');
      const reasonEl = document.getElementById('decision-reason-single');
      
      container.className = 'mb-8 rounded-2xl p-8 text-center text-white shadow-lg';
      icon.className = 'fas text-4xl mr-4';
      
      if (decision === 'accepted') {
        container.classList.add('bg-gradient-to-r', 'from-green-500', 'to-emerald-600');
        icon.classList.add('fa-check-circle');
        title.textContent = 'ACCEPTED';
        message.textContent = `Excellent match with ${score}% alignment`;
        reasonEl.textContent = reason || 'Candidate exceeds job requirements';
      } else if (decision === 'special_interview') {
        container.classList.add('bg-gradient-to-r', 'from-yellow-500', 'to-amber-600');
        icon.classList.add('fa-star');
        title.textContent = 'SPECIAL INTERVIEW REQUIRED';
        message.textContent = `Good match with ${score}% alignment`;
        reasonEl.textContent = reason || 'Candidate shows potential but needs further assessment';
      } else {
        container.classList.add('bg-gradient-to-r', 'from-red-500', 'to-rose-600');
        icon.classList.add('fa-times-circle');
        title.textContent = 'REJECTED';
        message.textContent = `Low match with ${score}% alignment`;
        reasonEl.textContent = reason || 'Candidate missing critical requirements';
      }
    }

    function updateSingleList(elementId, items) {
      const list = document.getElementById(elementId);
      list.innerHTML = "";
      if (items.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'No significant items identified';
        li.className = 'text-sm italic';
        list.appendChild(li);
      } else {
        items.forEach(item => {
          const li = document.createElement('li');
          li.textContent = item;
          li.className = 'text-sm';
          list.appendChild(li);
        });
      }
    }

    function updateRankingResults(data) {
      document.getElementById('total-candidates').textContent = data.candidates.length;
      document.getElementById('avg-salary').textContent = data.summary.average_salary;
      document.getElementById('avg-score').textContent = data.summary.average_score + '%';
      
      const container = document.getElementById('ranking-results');
      container.innerHTML = '';
      
      data.candidates.forEach((candidate, index) => {
        const card = document.createElement('div');
        card.className = `candidate-card bg-white rounded-2xl p-6 shadow-lg border border-gray-200 rank-${index < 3 ? index + 1 : 'other'}`;
        
        let rankBadge = '';
        if (index === 0) {
          rankBadge = '<div class="absolute top-4 right-4 bg-yellow-500 text-white px-3 py-1 rounded-full text-sm font-bold">TOP CANDIDATE</div>';
        } else if (index === 1) {
          rankBadge = '<div class="absolute top-4 right-4 bg-gray-500 text-white px-3 py-1 rounded-full text-sm font-bold">RUNNER UP</div>';
        } else if (index === 2) {
          rankBadge = '<div class="absolute top-4 right-4 bg-amber-800 text-white px-3 py-1 rounded-full text-sm font-bold">THIRD</div>';
        }
        
        let statusClass = '';
        let statusText = '';
        if (candidate.decision === 'accepted') {
          statusClass = 'bg-green-100 text-green-800';
          statusText = 'Accepted';
        } else if (candidate.decision === 'special_interview') {
          statusClass = 'bg-yellow-100 text-yellow-800';
          statusText = 'Special Interview';
        } else {
          statusClass = 'bg-red-100 text-red-800';
          statusText = 'Rejected';
        }
        
        card.innerHTML = `
          <div class="relative">
            ${rankBadge}
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center">
                <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-lg mr-4">
                  ${index + 1}
                </div>
                <div>
                  <h4 class="font-bold text-gray-800 text-lg">${candidate.filename}</h4>
                  <p class="text-gray-600 text-sm">${candidate.extracted_name || 'Name not found'}</p>
                  <p class="text-gray-500 text-xs">${candidate.extracted_email || 'Email not found'}</p>
                </div>
              </div>
              <span class="status-badge ${statusClass}">${statusText}</span>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div class="text-center">
                <div class="text-2xl font-bold ${getScoreColor(candidate.match_score)}">${candidate.match_score}%</div>
                <div class="text-xs text-gray-600">Match Score</div>
              </div>
              <div class="text-center">
                <div class="text-xl font-bold text-green-600">₹${formatIndianNumber(candidate.salary_range.median)}</div>
                <div class="text-xs text-gray-600">Expected Salary</div>
              </div>
              <div class="text-center">
                <div class="text-lg font-bold text-blue-600">${candidate.experience_years} yrs</div>
                <div class="text-xs text-gray-600">Experience</div>
              </div>
            </div>
            
            <div class="flex flex-wrap gap-1 mb-4">
              ${candidate.skills_found.slice(0, 5).map(skill => 
                `<span class="skill-tag bg-blue-100 text-blue-800 text-xs">${skill}</span>`
              ).join('')}
              ${candidate.skills_found.length > 5 ? 
                `<span class="skill-tag bg-gray-100 text-gray-600 text-xs">+${candidate.skills_found.length - 5} more</span>` : ''
              }
            </div>

            <!-- Hidden fields (Safe) -->
            <input type="hidden" class="cand-name" value="${candidate.extracted_name || ''}">
            <input type="hidden" class="cand-email" value="${candidate.extracted_email || ''}">
            <input type="hidden" class="cand-phone" value="${candidate.extracted_phone || ''}">
            <input type="hidden" class="cand-data" value='${JSON.stringify(candidate)}'>

            <div class="flex space-x-2">
            <button class="save-btn flex-1 bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-2 rounded-lg text-sm font-semibold transition-all flex items-center justify-center">
                <i class="fas fa-save mr-2"></i>Save
            </button>
            <button class="email-btn flex-1 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded-lg text-sm font-semibold transition-all flex items-center justify-center">
                <i class="fas fa-paper-plane mr-2"></i>Email
            </button>
            </div>
          </div>
        `;
        
        container.appendChild(card);
      });

      document.querySelectorAll('.candidate-card').forEach(card => {

        card.querySelector('.save-btn').onclick = () => {
        saveCandidateProfile(
            card.querySelector('.cand-email').value,
            JSON.parse(card.querySelector('.cand-data').value)
        );
        };

        card.querySelector('.email-btn').onclick = () => {
        sendCandidateEmail(
            card.querySelector('.cand-email').value,
            card.querySelector('.cand-name').value,
            JSON.parse(card.querySelector('.cand-data').value)
        );
        };

    });
      
      document.getElementById('ranking-results').classList.remove("hidden");
      document.getElementById('summary-stats').classList.remove("hidden");
      document.getElementById('loading-multiple').classList.add("hidden");
    }

    function getScoreColor(score) {
      if (score >= 90) return 'text-green-600';
      if (score >= 70) return 'text-yellow-600';
      return 'text-red-600';
    }

    // Candidate ranking functions
    window.saveCandidateProfile = async function(email, candidateData) {
      if (!email || email === 'Not Found') {
        alert('Cannot save profile: Email not found in resume');
        return;
      }
      
      try {
        const profileData = {
          name: candidateData.extracted_name,
          phone: candidateData.extracted_phone,
          match_score: candidateData.match_score,
          experience_years: candidateData.experience_years,
          skills_found: candidateData.skills_found,
          decision: candidateData.decision,
          analysis_date: new Date().toISOString()
        };
        
        const response = await fetch('/save-student-profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: email,
            profile: profileData
          })
        });
        
        if (response.ok) {
          alert('Candidate profile saved successfully!');
        } else {
          throw new Error('Failed to save candidate profile');
        }
      } catch (error) {
        alert('Error: ' + error.message);
      }
    };

    window.sendCandidateEmail = async function(email, name, candidateData) {
      if (!email || email === 'Not Found') {
        alert('Cannot send email: Email not found in resume');
        return;
      }
      
      try {
        const response = await fetch('/send-result-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: email,
            name: name,
            analysis_data: candidateData
          })
        });
        
        if (response.ok) {
          alert('Result email sent successfully!');
        } else {
          throw new Error('Failed to send result email');
        }
      } catch (error) {
        alert('Error: ' + error.message);
      }
    };

    async function loadStudentProfiles() {
      try {
        const response = await fetch('/get-student-profiles');
        const profiles = await response.json();
        
        const profilesList = document.getElementById('profiles-list');
        const profileCount = document.getElementById('profile-count');
        
        profilesList.innerHTML = '';
        profileCount.textContent = `${Object.keys(profiles).length} profiles`;
        
        Object.entries(profiles).forEach(([email, profile]) => {
          const profileElement = document.createElement('div');
          profileElement.className = 'bg-white rounded-xl p-4 border border-gray-200 cursor-pointer hover:border-blue-300 transition-all';
          profileElement.innerHTML = `
            <div class="flex justify-between items-start">
              <div>
                <h4 class="font-bold text-gray-800">${profile.name}</h4>
                <p class="text-sm text-gray-600">${email}</p>
                <p class="text-sm text-gray-500">${profile.phone || 'No phone'}</p>
                <div class="flex items-center mt-2">
                  <span class="text-xs font-semibold ${getScoreColor(profile.match_score)}">${profile.match_score}%</span>
                  <span class="mx-2 text-gray-300">•</span>
                  <span class="text-xs text-gray-600">${profile.experience_years} yrs exp</span>
                </div>
              </div>
              <span class="status-badge ${profile.decision === 'accepted' ? 'bg-green-100 text-green-800' : profile.decision === 'special_interview' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}">
                ${profile.decision}
              </span>
            </div>
          `;
          
          profileElement.addEventListener('click', () => showProfileDetails(profile, email));
          profilesList.appendChild(profileElement);
        });
      } catch (error) {
        console.error('Error loading profiles:', error);
      }
    }

    function showProfileDetails(profile, email) {
      document.getElementById('profile-details').classList.remove('hidden');
      document.getElementById('profile-placeholder').classList.add('hidden');
      
      document.getElementById('profile-name').textContent = profile.name;
      document.getElementById('profile-email').textContent = email;
      document.getElementById('profile-phone').textContent = `Phone: ${profile.phone || 'Not provided'}`;
      document.getElementById('profile-score').textContent = profile.match_score + '%';
      document.getElementById('profile-score-bar').style.width = profile.match_score + '%';
      document.getElementById('profile-experience').textContent = profile.experience_years + ' years';
      document.getElementById('profile-status').textContent = profile.decision;
      document.getElementById('profile-status').className = `text-sm font-bold ${
        profile.decision === 'accepted' ? 'text-green-600' : 
        profile.decision === 'special_interview' ? 'text-yellow-600' : 'text-red-600'
      }`;
      
      const skillsContainer = document.getElementById('profile-skills');
      skillsContainer.innerHTML = '';
      profile.skills_found.slice(0, 8).forEach(skill => {
        const skillElement = document.createElement('span');
        skillElement.className = 'skill-tag bg-blue-100 text-blue-800 text-xs';
        skillElement.textContent = skill;
        skillsContainer.appendChild(skillElement);
      });
      
      window.currentProfile = { ...profile, email };
    }

    async function saveStudentProfile(name, email, phone, analysisData) {
      try {
        const profileData = {
          name: name,
          phone: phone,
          match_score: analysisData.match_score,
          experience_years: analysisData.experience_years,
          skills_found: analysisData.skills_found,
          decision: analysisData.decision,
          analysis_date: new Date().toISOString()
        };
        
        const response = await fetch('/save-student-profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: email,
            profile: profileData
          })
        });
        
        if (response.ok) {
          alert('Student profile saved successfully!');
          if (document.getElementById('page-profiles').classList.contains('page-active')) {
            loadStudentProfiles();
          }
        } else {
          throw new Error('Failed to save student profile');
        }
      } catch (error) {
        alert('Error: ' + error.message);
      }
    }

    async function sendResultEmail(email, name, analysisData) {
      try {
        const response = await fetch('/send-result-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: email,
            name: name,
            analysis_data: analysisData
          })
        });
        
        if (response.ok) {
          alert('Result email sent successfully!');
        } else {
          throw new Error('Failed to send result email');
        }
      } catch (error) {
        alert('Error: ' + error.message);
      }
    }

    // Global functions for profile page
    window.sendEmail = async function(decision) {
      if (!window.currentProfile) {
        alert('No profile selected');
        return;
      }
      
      const customMessage = document.getElementById('custom-message').value;
      
      try {
        const response = await fetch('/send-profile-email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: window.currentProfile.email,
            name: window.currentProfile.name,
            decision: decision,
            custom_message: customMessage,
            profile_data: window.currentProfile
          })
        });
        
        if (response.ok) {
          alert(`${decision.charAt(0).toUpperCase() + decision.slice(1)} email sent successfully!`);
        } else {
          throw new Error('Failed to send email');
        }
      } catch (error) {
        alert('Error: ' + error.message);
      }
    };

    // Initialize
    document.getElementById('placeholder-single').classList.remove('hidden');
    document.getElementById('placeholder-multiple').classList.remove('hidden');
  </script>
</body>
</html>
"""

class SmartResumeEvaluator:
    def __init__(self):
        self.common_skills = [
            'python', 'java', 'javascript', 'html', 'css', 'react', 'angular',
            'vue', 'sql', 'mongodb', 'aws', 'docker', 'git', 'machine learning',
            'data analysis', 'project management', 'agile', 'scrum', 'excel',
            'communication', 'leadership', 'teamwork', 'problem solving',
            'c++', 'c#', 'php', 'ruby', 'swift', 'kotlin', 'typescript',
            'node.js', 'express', 'django', 'flask', 'spring', 'laravel',
            'mysql', 'postgresql', 'oracle', 'redis', 'firebase',
            'azure', 'google cloud', 'jenkins', 'kubernetes', 'linux',
            'rest api', 'graphql', 'microservices', 'ci/cd', 'devops'
        ]

        # Updated Decision thresholds
        self.ACCEPT_THRESHOLD = 90
        self.SPECIAL_INTERVIEW_THRESHOLD = 70

        # Salary configuration for Indian market
        self.BASE_SALARY = 600000  # 6 LPA base
        self.PREMIUM_SKILLS = ['machine learning', 'aws', 'kubernetes', 'docker', 'python', 'react', 'node.js']
        self.PREMIUM_SKILL_BONUS = 50000  # 50k per premium skill

        # Updated Email templates with institution info
        self.email_templates = {
            'accepted': """Dear {{student_name}},

We are pleased to inform you that your application has been ACCEPTED!

Your resume showed excellent alignment with our requirements:
- Match Score: {{match_score}}%
- Key Skills: {{skills}}
- Experience: {{experience_years}} years

We were particularly impressed with your strengths in:
{{strengths}}

Next Steps:
1. We will contact you within 3 business days to schedule an interview
2. Please keep your documents ready for verification
3. Be prepared to discuss your technical skills in detail

For any queries, please contact:
{{institution_name}}
Email: {{institution_email}}
Phone: {{institution_phone}}

We look forward to welcoming you to our team!

Best regards,
Recruitment Team
{{institution_name}}""",

            'special_interview': """Dear {{student_name}},

Thank you for your application. 

Your profile shows promise with a {{match_score}}% match to our requirements. 
We would like to invite you for a SPECIAL INTERVIEW/ASSESSMENT.

Your key qualifications:
- Skills: {{skills}}
- Experience: {{experience_years}} years

Areas for development:
{{gaps}}

Next Steps:
1. Special technical assessment scheduled
2. Further interview rounds if assessment is cleared
3. We will contact you with assessment details

For any queries, please contact:
{{institution_name}}
Email: {{institution_email}}
Phone: {{institution_phone}}

We appreciate your interest and look forward to your assessment.

Best regards,
Recruitment Team
{{institution_name}}""",

            'rejected': """Dear {{student_name}},

Thank you for your interest in the position and for taking the time to apply.

After careful consideration, we have decided to move forward with other candidates whose qualifications more closely match our current requirements.

Your application showed:
- Match Score: {{match_score}}%
- Key Skills: {{skills}}

We encourage you to apply for future positions as they become available and continue developing your skills in the areas mentioned.

For career guidance, please contact:
{{institution_name}}
Email: {{institution_email}}
Phone: {{institution_phone}}

We wish you the best in your job search.

Best regards,
Recruitment Team
{{institution_name}}"""
        }

        # Initialize model
        self.model = None
        self.explainer = None
        self.feature_names = []
        self.setup_model()

    def setup_model(self):
        """Initialize or load model"""
        try:
            self.model = joblib.load('smart_resume_model.pkl')
            self.explainer = joblib.load('smart_explainer.pkl')
            self.feature_names = joblib.load('feature_names.pkl')
            print("✓ Pre-trained model loaded")
        except:
            print("⚠ No pre-trained model found. Training new model...")
            self.train_model()

    def extract_contact_info(self, text):
        """Extract name, email, and phone from resume text"""
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        email = emails[0] if emails else "Not Found"
        
        # Extract phone numbers (international format)
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
            r'\b\d{10}\b',  # Indian 10-digit
            r'\+91[-.\s]?\d{5}[-.\s]?\d{5}',  # Indian with +91
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'  # US format
        ]
        
        phone = "Not Found"
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                phone = phones[0]
                break
        
        # Extract name (simple heuristic - first line that looks like a name)
        lines = text.split('\n')
        name = "Not Found"
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if (len(line) > 2 and len(line) < 50 and 
                not re.search(r'@|\d{10}|\+', line) and
                not any(word in line.lower() for word in ['resume', 'cv', 'curriculum', 'vitae', 'page', 'linkedin'])):
                name = line
                break
        
        return {
            'name': name,
            'email': email,
            'phone': phone
        }

    def create_synthetic_dataset(self, n_samples=1000):
        """Create training data for demonstration"""
        np.random.seed(42)
        
        features = []
        labels = []

        self.feature_names = [
            'python_experience', 'javascript_experience', 'java_experience', 
            'sql_experience', 'aws_experience', 'docker_experience', 
            'react_experience', 'machine_learning', 'years_experience', 
            'degree_level', 'project_count', 'certification_count', 
            'leadership_experience', 'communication_skills', 'portfolio_activity'
        ]
        
        for i in range(n_samples):
            candidate_features = [
                np.random.randint(0, 3), 
                np.random.randint(0, 3),  
                np.random.randint(0, 3), 
                np.random.randint(0, 3),  
                np.random.randint(0, 3),  
                np.random.randint(0, 3),  
                np.random.randint(0, 3), 
                np.random.randint(0, 2), 
                np.random.uniform(0, 15), 
                np.random.randint(0, 4),  
                np.random.randint(0, 25), 
                np.random.randint(0, 12), 
                np.random.randint(0, 2),  
                np.random.randint(0, 3), 
                np.random.randint(0, 2),  
            ]

            score = (
                candidate_features[0] * 0.12 +  
                candidate_features[1] * 0.08 +  
                candidate_features[4] * 0.15 +  
                candidate_features[7] * 0.20 +  
                min(candidate_features[8] * 0.06, 0.9) +  
                candidate_features[9] * 0.04 +  
                candidate_features[12] * 0.08 + 
                candidate_features[13] * 0.10 + 
                candidate_features[10] * 0.03 + 
                candidate_features[11] * 0.04 
            )
            
            label = 1 if score > 0.45 else 0
            labels.append(label)
            features.append(candidate_features)
        
        return np.array(features), np.array(labels)

    def train_model(self):
        """Train a model and explainer"""
        print("Training model...")

        X, y = self.create_synthetic_dataset(1500)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model = RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            min_samples_split=5,
            random_state=42
        )
        self.model.fit(X_train, y_train)

        self.explainer = shap.TreeExplainer(self.model)

        joblib.dump(self.model, 'smart_resume_model.pkl')
        joblib.dump(self.explainer, 'smart_explainer.pkl')
        joblib.dump(self.feature_names, 'feature_names.pkl')
        
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        print(f"✓ Model trained (Train: {train_score:.3f}, Test: {test_score:.3f})")

    def extract_text_from_pdf(self, file_stream):
        """Extract text from PDF file"""
        try:
            text = ""
            with pdfplumber.open(file_stream) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""

    def extract_skills(self, text):
        """Extract skills from text"""
        found_skills = []
        text_lower = text.lower()

        for skill in self.common_skills:
            if skill in text_lower:
                found_skills.append(skill)

        return found_skills

    def extract_experience(self, text):
        """Extract years of experience"""
        experience_patterns = [
            r'(\d+)\s*years?',
            r'(\d+)\s*yrs?',
            r'(\d+)\s*yr?',
            r'experience.*?(\d+)\s*years?',
            r'(\d+)\+?\s*years?\s*experience'
        ]

        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                years = max([int(match) for match in matches])
                return min(years, 20)
        return 0

    def extract_features_for_analysis(self, resume_text, job_description):
        """Extract features for analysis"""
        features = np.zeros(len(self.feature_names))
        
        text_lower = resume_text.lower()
        jd_lower = job_description.lower()

        features[0] = 2 if any(word in text_lower for word in ['python', 'django', 'flask']) else 1 if 'python' in text_lower else 0
        features[1] = 2 if any(word in text_lower for word in ['javascript', 'typescript', 'node.js']) else 1 if 'javascript' in text_lower else 0
        features[2] = 2 if any(word in text_lower for word in ['java', 'spring', 'j2ee']) else 1 if 'java' in text_lower else 0
        features[3] = 2 if any(word in text_lower for word in ['sql', 'mysql', 'postgresql']) else 1 if 'sql' in text_lower else 0
        features[4] = 2 if any(word in text_lower for word in ['aws', 'amazon web services', 'ec2']) else 1 if 'aws' in text_lower else 0
        features[5] = 2 if any(word in text_lower for word in ['docker', 'container', 'kubernetes']) else 1 if 'docker' in text_lower else 0
        features[6] = 2 if any(word in text_lower for word in ['react', 'react.js', 'redux']) else 1 if 'react' in text_lower else 0

        features[7] = 1 if any(word in text_lower for word in ['machine learning', 'ml', 'ai', 'tensorflow', 'pytorch']) else 0

        features[8] = self.extract_experience(resume_text)

        if 'phd' in text_lower or 'doctorate' in text_lower:
            features[9] = 3
        elif 'master' in text_lower or 'ms' in text_lower:
            features[9] = 2
        elif 'bachelor' in text_lower or 'undergraduate' in text_lower or 'bs' in text_lower or 'ba' in text_lower:
            features[9] = 1
        else:
            features[9] = 0

        features[10] = len(re.findall(r'project|developed|built|created|implemented', text_lower))
        features[10] = min(features[10], 24)

        features[11] = len(re.findall(r'certification|certified|certificate|license', text_lower))
        features[11] = min(features[11], 11)

        features[12] = 1 if any(word in text_lower for word in 
                               ['lead', 'managed', 'supervised', 'team lead', 'directed', 'oversaw']) else 0

        features[13] = 2 if any(word in text_lower for word in 
                               ['presentation', 'public speaking', 'client facing']) else 1 if any(word in text_lower for word in 
                               ['communication', 'collaborat', 'teamwork']) else 0

        features[14] = 1 if any(word in text_lower for word in 
                               ['github', 'gitlab', 'bitbucket', 'open source', 'portfolio']) else 0
        
        return features

    def generate_smart_explanations(self, resume_text, job_description):
        """Generate explanations for resume decision"""
        try:
            features = self.extract_features_for_analysis(resume_text, job_description)
            features_2d = features.reshape(1, -1)

            shap_values = self.explainer.shap_values(features_2d)

            prediction_proba = self.model.predict_proba(features_2d)[0]
            prediction = np.argmax(prediction_proba)
            confidence = prediction_proba[prediction]

            if len(shap_values) == 2:
                shap_values_single = shap_values[1][0]
            else:
                shap_values_single = shap_values[0]

            feature_importance = {}
            shap_sum = np.sum(np.abs(shap_values_single))
            
            for i, feature_name in enumerate(self.feature_names):
                if shap_sum > 0:
                    importance_score = (shap_values_single[i] / shap_sum) * 100
                else:
                    importance_score = 0
                feature_importance[feature_name] = round(importance_score, 1)

            top_positive = [f for f, score in feature_importance.items() if score > 0]
            top_positive = sorted(top_positive, key=lambda x: feature_importance[x], reverse=True)[:3]
            
            top_negative = [f for f, score in feature_importance.items() if score < 0]
            top_negative = sorted(top_negative, key=lambda x: feature_importance[x])[:3]
            
            explanation = f"AI recommends {'ACCEPTED' if prediction == 1 else 'SPECIAL INTERVIEW' if prediction == 0.5 else 'REJECTED'} "
            explanation += f"with {confidence:.1%} confidence. "
            
            if top_positive:
                pos_features = [f.replace('_', ' ') for f in top_positive]
                explanation += f"Key strengths: {', '.join(pos_features)}. "
            if top_negative:
                neg_features = [f.replace('_', ' ') for f in top_negative]
                explanation += f"Areas to improve: {', '.join(neg_features)}."
            
            return {
                'feature_importance': feature_importance,
                'prediction': 'accepted' if prediction == 1 else 'special_interview' if confidence > 0.6 else 'rejected',
                'confidence': round(confidence * 100, 1),
                'explanation': explanation,
                'base_value': float(self.explainer.expected_value[1] if len(self.explainer.expected_value) == 2 
                                  else self.explainer.expected_value),
                'features': dict(zip(self.feature_names, features.tolist()))
            }
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return self.generate_fallback_explanation(resume_text, job_description)

    def generate_fallback_explanation(self, resume_text, job_description):
        """Fallback explanation if analysis fails"""
        skills = self.extract_skills(resume_text)
        jd_skills = self.extract_skills(job_description)
        experience = self.extract_experience(resume_text)
        
        matched = len([s for s in jd_skills if s in skills])
        total_jd = len(jd_skills) if len(jd_skills) > 0 else 1
        
        score = (matched / total_jd) * 100
        
        return {
            'feature_importance': {
                'skill_match': min(score, 100),
                'experience': min(experience * 8, 100),
                'premium_skills': len([s for s in skills if s in self.PREMIUM_SKILLS]) * 15
            },
            'prediction': 'accepted' if score >= 90 else 'special_interview' if score >= 70 else 'rejected',
            'confidence': 70.0,
            'explanation': 'Analysis based on skill matching and experience evaluation',
            'base_value': 50.0,
            'features': {}
        }

    def predict_salary_range(self, skills, experience_years, base_salary=600000, location_factor=1.0):
        """Predict salary range based on skills and experience for Indian market"""
        experience_bonus = experience_years * 50000

        premium_bonus = 0
        for skill in skills:
            if skill in self.PREMIUM_SKILLS:
                premium_bonus += self.PREMIUM_SKILL_BONUS

        median_salary = (base_salary + experience_bonus + premium_bonus) * location_factor

        low_range = median_salary * 0.75
        high_range = median_salary * 1.25

        return {
            'low': round(low_range),
            'median': round(median_salary),
            'high': round(high_range),
            'currency': '₹'
        }

    def format_indian_currency(self, amount):
        """Format amount in Indian currency format"""
        if amount >= 10000000:
            return f"₹{amount/10000000:.1f} Cr"
        elif amount >= 100000:
            return f"₹{amount/100000:.1f} L"
        else:
            return f"₹{amount:,}"

    def make_decision(self, match_score, matched_skills, missing_skills, experience_years, job_description):
        """Make acceptance/rejection decision with new thresholds"""
        if match_score >= self.ACCEPT_THRESHOLD:
            decision = "accepted"
            reason = "Excellent match! Candidate exceeds most requirements with strong skill alignment."

        elif match_score >= self.SPECIAL_INTERVIEW_THRESHOLD:
            decision = "special_interview"
            if len(missing_skills) > 0:
                reason = f"Good match. Requires special interview/assessment to evaluate: {', '.join(missing_skills[:3])}"
            else:
                reason = "Good match. Candidate shows potential but needs further assessment through special interview."

        else:
            decision = "rejected"
            if len(missing_skills) > 0:
                reason = f"Low match. Missing critical skills: {', '.join(missing_skills[:3])}"
            else:
                reason = "Low overall alignment with job requirements and expectations."

        required_experience = self.extract_experience(job_description)
        if required_experience > 0 and experience_years < required_experience:
            if decision == "accepted":
                decision = "special_interview"
                reason += f" Note: Has {experience_years} years vs required {required_experience} years."
            elif decision == "rejected":
                reason += f" Also below required experience: {experience_years} years vs {required_experience} years required."

        return decision, reason

    def calculate_comprehensive_score(self, match_score, experience_years, skills_count, required_experience=0):
        """Calculate comprehensive score considering multiple factors"""
        base_score = match_score * 0.6

        exp_bonus = min(experience_years * 3, 30)
        base_score += exp_bonus * 0.3

        skills_bonus = min(skills_count * 1, 10)
        base_score += skills_bonus * 0.1

        return min(round(base_score), 100)

    def analyze_single_resume(self, resume_text, job_description, filename, base_salary=600000, location_factor=1.0):
        """Enhanced analysis with contact extraction"""
        # Extract contact information
        contact_info = self.extract_contact_info(resume_text)
        
        resume_skills = self.extract_skills(resume_text)
        jd_skills = self.extract_skills(job_description)
        experience = self.extract_experience(resume_text)

        if jd_skills:
            matched_skills = [skill for skill in jd_skills if skill in resume_skills]
            match_score = round((len(matched_skills) / len(jd_skills)) * 100, 2)
        else:
            matched_skills = []
            match_score = 0

        missing_skills = [skill for skill in jd_skills if skill not in resume_skills]

        salary_range = self.predict_salary_range(resume_skills, experience, base_salary, location_factor)

        decision, decision_reason = self.make_decision(
            match_score, matched_skills, missing_skills, experience, job_description
        )

        analysis_results = self.generate_smart_explanations(resume_text, job_description)

        confidence_factors = {
            'skill_coverage': min(len(matched_skills) / 8, 1.0),
            'experience_clarity': 1.0 if experience > 0 else 0.4,
            'text_quality': min(len(resume_text) / 1500, 1.0)
        }
        confidence_score = round(sum(confidence_factors.values()) / len(confidence_factors) * 100, 1)

        if analysis_results and analysis_results.get('confidence', 0) > 70:
            decision = analysis_results['prediction']
            confidence_score = max(confidence_score, analysis_results['confidence'])

        return {
            'filename': filename,
            'extracted_name': contact_info['name'],
            'extracted_email': contact_info['email'],
            'extracted_phone': contact_info['phone'],
            'match_score': match_score,
            'skills_found': resume_skills,
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'experience_years': experience,
            'strengths': matched_skills[:5],
            'gaps': missing_skills[:5],
            'decision': decision,
            'decision_reason': decision_reason,
            'salary_range': salary_range,
            'confidence_score': confidence_score,
            'shap_analysis': analysis_results,
            'analysis_timestamp': datetime.now().isoformat()
        }

    def analyze_multiple_resumes(self, resume_files, job_description, base_salary=600000, location_factor=1.0):
        """Analyze multiple resumes for ranking with contact extraction"""
        candidates_data = []

        for resume_file in resume_files:
            if resume_file.filename == "":
                continue

            filename = resume_file.filename
            print(f"Processing file: {filename}")

            resume_text = ""
            try:
                if filename.lower().endswith('.pdf'):
                    file_bytes = io.BytesIO(resume_file.read())
                    resume_text = self.extract_text_from_pdf(file_bytes)

                    if not resume_text:
                        print(f"Could not extract text from PDF: {filename}")
                        continue

                elif filename.lower().endswith('.txt'):
                    resume_text = resume_file.read().decode('utf-8')
                else:
                    print(f"Unsupported file format: {filename}")
                    continue

                if not resume_text.strip():
                    print(f"Empty resume file: {filename}")
                    continue

                # Extract contact information
                contact_info = self.extract_contact_info(resume_text)
                
                resume_skills = self.extract_skills(resume_text)
                jd_skills = self.extract_skills(job_description)
                experience = self.extract_experience(resume_text)

                if jd_skills:
                    matched_skills = [skill for skill in jd_skills if skill in resume_skills]
                    basic_match_score = round((len(matched_skills) / len(jd_skills)) * 100, 2)
                else:
                    matched_skills = []
                    basic_match_score = 0

                required_experience = self.extract_experience(job_description)
                comprehensive_score = self.calculate_comprehensive_score(
                    basic_match_score, experience, len(resume_skills), required_experience
                )

                missing_skills = [skill for skill in jd_skills if skill not in resume_skills]

                salary_range = self.predict_salary_range(resume_skills, experience, base_salary, location_factor)

                decision, decision_reason = self.make_decision(
                    comprehensive_score, matched_skills, missing_skills, experience, job_description
                )

                candidate_analysis = {
                    'filename': filename,
                    'extracted_name': contact_info['name'],
                    'extracted_email': contact_info['email'],
                    'extracted_phone': contact_info['phone'],
                    'match_score': comprehensive_score,
                    'skills_found': resume_skills,
                    'matched_skills': matched_skills,
                    'missing_skills': missing_skills,
                    'experience_years': experience,
                    'strengths': matched_skills[:5],
                    'gaps': missing_skills[:5],
                    'decision': decision,
                    'decision_reason': decision_reason,
                    'salary_range': salary_range,
                    'analysis_timestamp': datetime.now().isoformat()
                }

                candidates_data.append(candidate_analysis)
                print(f"✓ Analyzed {filename}, score: {comprehensive_score}%")

            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
                continue

        return candidates_data

    def rank_candidates(self, candidates_data):
        """Rank candidates based on comprehensive scoring"""
        ranked_candidates = sorted(
            candidates_data,
            key=lambda x: (x['match_score'], x['experience_years'], len(x['skills_found'])),
            reverse=True
        )
        
        total_candidates = len(ranked_candidates)
        if total_candidates > 0:
            average_score = round(sum(c['match_score'] for c in ranked_candidates) / total_candidates, 1)
            average_salary_num = sum(c['salary_range']['median'] for c in ranked_candidates) / total_candidates
            average_salary = self.format_indian_currency(round(average_salary_num))
        else:
            average_score = 0
            average_salary = "₹0"

        summary = {
            'total_candidates': total_candidates,
            'average_score': average_score,
            'average_salary': average_salary,
            'top_candidate': ranked_candidates[0]['filename'] if ranked_candidates else None
        }

        return ranked_candidates, summary

    def format_email_template(self, template, data):
        """Format email template with student and institution data"""
        formatted = template
        
        formatted = formatted.replace('{{student_name}}', data.get('name', 'Candidate'))
        formatted = formatted.replace('{{match_score}}', str(data.get('match_score', 0)))
        formatted = formatted.replace('{{experience_years}}', str(data.get('experience_years', 0)))
        
        skills = ', '.join(data.get('skills_found', [])[:5])
        formatted = formatted.replace('{{skills}}', skills)
        
        strengths = '\n- '.join(data.get('strengths', ['Good technical foundation']))
        formatted = formatted.replace('{{strengths}}', '- ' + strengths)
        
        gaps = '\n- '.join(data.get('gaps', ['Continue skill development']))
        formatted = formatted.replace('{{gaps}}', '- ' + gaps)
        
        # Add institution info
        formatted = formatted.replace('{{institution_name}}', INSTITUTION_CONFIG['name'])
        formatted = formatted.replace('{{institution_email}}', INSTITUTION_CONFIG['email'])
        formatted = formatted.replace('{{institution_phone}}', INSTITUTION_CONFIG['phone'])
        
        return formatted

    def send_email_via_firebase(self, to_email, subject, message):
      """Store email in Firebase and actually send it via Gmail"""
      try:
          if not db:
              return False, "Firebase not initialized"

          # Store in Firebase first
          email_data = {
              'to': to_email,
              'subject': subject,
              'message': message,
              'status': 'pending',
              'created_at': firestore.SERVER_TIMESTAMP
          }
          db.collection('emails').add(email_data)
          print(f"✓ Email stored in Firebase for {to_email}")

          # --- Actual Email Sending Section ---
          import smtplib
          from email.mime.text import MIMEText
          from email.mime.multipart import MIMEMultipart

          sender_email = "jrjohiralom14@gmail.com"
          app_password = "nzidxcfekzuyliqh"

          msg = MIMEMultipart()
          msg["From"] = sender_email
          msg["To"] = to_email
          msg["Subject"] = subject
          msg.attach(MIMEText(message, "plain"))

          # Send through Gmail's secure SMTP server
          with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
              server.login(sender_email, app_password)
              server.sendmail(sender_email, to_email, msg.as_string())

          print(f"✅ Email sent successfully to {to_email}")

          # Update Firestore record status
          db.collection('emails').where('to', '==', to_email).where('subject', '==', subject).limit(1).get()
          for doc in db.collection('emails').where('to', '==', to_email).where('subject', '==', subject).limit(1).get():
              db.collection('emails').document(doc.id).update({'status': 'sent'})

          return True, "Email sent and stored in Firebase"

      except Exception as e:
          print(f"⚠️ Error sending email via Firebase: {e}")
          return False, f"Failed to send email: {str(e)}"

# Initialize evaluator
evaluator = SmartResumeEvaluator()

# Routes
@app.route('/')
def home():
    return HTML_CONTENT

@app.route('/analyze-single', methods=['POST'])
def analyze_single():
    """Analyze a single resume with enhanced explanations"""
    try:
        print("Single analysis request received")

        job_description = request.form.get('job_description', '')
        resume_file = request.files.get('resume')
        base_salary = float(request.form.get('base_salary', 600000))
        location_factor = float(request.form.get('location_factor', 1.0))

        if not resume_file:
            return jsonify({'error': 'No resume file uploaded'}), 400

        if not job_description.strip():
            return jsonify({'error': 'Job description is required'}), 400

        resume_text = ""
        filename = resume_file.filename

        if filename.lower().endswith('.pdf'):
            file_bytes = io.BytesIO(resume_file.read())
            resume_text = evaluator.extract_text_from_pdf(file_bytes)
            if not resume_text:
                return jsonify({'error': 'Could not extract text from PDF. The file might be scanned or corrupted.'}), 400
        elif filename.lower().endswith('.txt'):
            resume_text = resume_file.read().decode('utf-8')
        else:
            return jsonify({'error': 'Unsupported file format. Please upload PDF or TXT.'}), 400

        if not resume_text.strip():
            return jsonify({'error': 'Resume file is empty or could not be read'}), 400

        results = evaluator.analyze_single_resume(
            resume_text, job_description, filename, base_salary, location_factor
        )
        
        print(f"Analysis complete. Score: {results['match_score']}% - Decision: {results['decision'].upper()}")

        return jsonify(results)

    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/analyze-multiple', methods=['POST'])
def analyze_multiple():
    """Analyze multiple resumes and rank them"""
    try:
        print("Multiple analysis request received")

        job_description = request.form.get('job_description', '')
        resume_files = request.files.getlist('resumes')
        base_salary = float(request.form.get('base_salary', 600000))
        location_factor = float(request.form.get('location_factor', 1.0))

        if not resume_files:
            return jsonify({'error': 'No resume files uploaded'}), 400

        if not job_description.strip():
            return jsonify({'error': 'Job description is required'}), 400

        valid_files = [file for file in resume_files if file.filename]
        if not valid_files:
            return jsonify({'error': 'No valid files found'}), 400

        print(f"Processing {len(valid_files)} files...")

        candidates_data = evaluator.analyze_multiple_resumes(
            valid_files, job_description, base_salary, location_factor
        )

        if not candidates_data:
            return jsonify({'error': 'No valid resume data could be extracted'}), 400

        ranked_candidates, summary = evaluator.rank_candidates(candidates_data)

        print(f"Ranking complete. Top candidate: {summary['top_candidate']}")

        return jsonify({
            'candidates': ranked_candidates,
            'summary': summary
        })

    except Exception as e:
        print(f"Error in multiple analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/save-student-profile', methods=['POST'])
def save_student_profile():
    """Save student profile to Firebase"""
    try:
        data = request.json
        email = data.get('email')
        profile = data.get('profile')

        if not email or not profile:
            return jsonify({'error': 'Email and profile data required'}), 400

        if db:
            # Store in Firebase
            db.collection('student_profiles').document(email).set(profile)
            print(f"✓ Profile saved to Firebase for {email}")
        else:
            # Fallback to in-memory storage
            student_profiles[email] = profile
            print(f"✓ Profile saved locally for {email}")

        return jsonify({'success': True})

    except Exception as e:
        print(f"Error saving profile: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-student-profiles', methods=['GET'])
def get_student_profiles():
    """Get all student profiles"""
    try:
        if db:
            # Get from Firebase
            profiles = {}
            docs = db.collection('student_profiles').stream()
            for doc in docs:
                profiles[doc.id] = doc.to_dict()
            return jsonify(profiles)
        else:
            # Get from in-memory storage
            return jsonify(student_profiles)

    except Exception as e:
        print(f"Error getting profiles: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/send-result-email', methods=['POST'])
def send_result_email():
    """Send result email to candidate"""
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')
        analysis_data = data.get('analysis_data')

        if not email or not analysis_data:
            return jsonify({'error': 'Email and analysis data required'}), 400

        decision = analysis_data.get('decision', 'rejected')
        template = evaluator.email_templates.get(decision, evaluator.email_templates['rejected'])
        
        formatted_email = evaluator.format_email_template(template, {
            'name': name,
            'match_score': analysis_data.get('match_score', 0),
            'experience_years': analysis_data.get('experience_years', 0),
            'skills_found': analysis_data.get('skills_found', []),
            'strengths': analysis_data.get('strengths', []),
            'gaps': analysis_data.get('gaps', [])
        })

        subject = f"Application Update - {INSTITUTION_CONFIG['name']}"
        
        success, message = evaluator.send_email_via_firebase(email, subject, formatted_email)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 500

    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/send-profile-email', methods=['POST'])
def send_profile_email():
    """Send email from profile page"""
    try:
        data = request.json
        email = data.get('email')
        name = data.get('name')
        decision = data.get('decision', 'rejected')
        custom_message = data.get('custom_message', '')
        profile_data = data.get('profile_data', {})

        template = evaluator.email_templates.get(decision, evaluator.email_templates['rejected'])
        
        formatted_email = evaluator.format_email_template(template, {
            'name': name,
            'match_score': profile_data.get('match_score', 0),
            'experience_years': profile_data.get('experience_years', 0),
            'skills_found': profile_data.get('skills_found', []),
            'strengths': profile_data.get('strengths', []),
            'gaps': profile_data.get('gaps', [])
        })

        if custom_message:
            formatted_email += f"\n\nAdditional Note:\n{custom_message}"

        subject = f"Application Update - {INSTITUTION_CONFIG['name']}"
        
        success, message = evaluator.send_email_via_firebase(email, subject, formatted_email)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'error': message}), 500

    except Exception as e:
        print(f"Error sending profile email: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test-firebase', methods=['GET'])
def test_firebase():
    """Test Firebase connection"""
    try:
        if db:
            # Test by writing and reading a test document
            test_ref = db.collection('connection_tests').document('test')
            test_ref.set({'timestamp': firestore.SERVER_TIMESTAMP})
            test_ref.delete()
            return jsonify({'success': True, 'message': 'Firebase connected successfully'})
        else:
            return jsonify({'success': False, 'error': 'Firebase not initialized'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test-email-service', methods=['GET'])
def test_email_service():
    """Test email service"""
    try:
        # Test by sending a test email
        test_email = "test@example.com"
        subject = "Test Email - Resume Evaluator"
        message = "This is a test email from the Resume Evaluator system."
        
        success, result = evaluator.send_email_via_firebase(test_email, subject, message)
        
        if success:
            return jsonify({'success': True, 'message': 'Email service is working correctly'})
        else:
            return jsonify({'success': False, 'error': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/save-institution-config', methods=['POST'])
def save_institution_config():
    """Save institution configuration"""
    try:
        data = request.json
        INSTITUTION_CONFIG.update(data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-institution-config', methods=['GET'])
def get_institution_config():
    """Get institution configuration"""
    return jsonify(INSTITUTION_CONFIG)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)