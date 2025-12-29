# 🤖 An Explainable AI for Resume Acceptance

## Brief One Line Summary
An Explainable AI–based resume screening system that predicts resume acceptance or rejection and provides transparent, human-readable explanations using SHAP and interpretable machine learning models.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Dataset Description](#dataset-description)
- [Tools & Technologies](#tools--technologies)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Methodology](#methodology)
- [Explainable AI Techniques](#explainable-ai-techniques)
- [Model Training & Evaluation](#model-training--evaluation)
- [Results & Explanation](#results--explanation)
- [How to Run This Project](#how-to-run-this-project)
- [Future Work](#future-work)
- [Team Members](#team-members)

---

## Overview

Recruitment processes often rely on automated systems to screen resumes, but traditional machine learning models act as **black boxes**, offering no explanation for their decisions.  
This project addresses that challenge by developing an **Explainable AI (XAI)** system that not only predicts resume acceptance but also clearly explains *why* a resume was accepted or rejected.

The system improves transparency, trust, and fairness in automated hiring.

---

## Problem Statement

Most AI-based resume screening systems:
- Lack transparency
- Provide no reasoning for decisions
- Create trust issues for recruiters and applicants

**Objective:**  
To build a machine learning system that:
- Predicts resume acceptance or rejection
- Explains decisions using interpretable AI techniques
- Helps recruiters understand feature influence clearly

---
## Dataset Description

The project uses a **synthetic dataset of 2,000 generated resume samples** created to simulate real-world hiring scenarios.  
The dataset includes features such as skills, experience, education, and certifications, with the target variable indicating **resume acceptance or rejection**.  
Using synthetic data ensures privacy, balanced representation, and suitability for demonstrating **Explainable AI (XAI)** techniques.

---

## Tools & Technologies

- **Programming Language:** Python  
- **Libraries:**  
  - Pandas  
  - NumPy  
  - Scikit-learn  
  - SHAP  
  - Matplotlib  
  - Seaborn  
- **Machine Learning Models:**  
  - Random Forest  
  - Ensemble Learning  
- **Explainable AI:** SHAP, Custom Interpreters  
- **File Handling:** Pickle (.pkl)  
- **Resume Parsing:** PDF text extraction  

---

## Project Structure
```
explainable-ai-resume-acceptance/
│
├── demo_resume_model.pkl        # Base machine learning model for resume acceptance prediction
├── demo_resume_explainer.pkl    # Basic explainability object for model decisions
│
├── smart_resume_model.pkl       # Optimized and fine-tuned resume classification model
├── smart_explainer.pkl          # Advanced explainability logic for improved transparency
│
├── shap_resume_model.pkl        # Model specifically prepared for SHAP-based analysis
├── shap_explainer.pkl           # SHAP explainer object for feature contribution visualization
│
├── feature_names.pkl            # List of input feature names used during training and inference
│
├── pdf_ana.py                   # Python script for resume PDF analysis and prediction
│                              # - Extracts resume data
│                              # - Runs prediction
│                              # - Generates explainability output
│
├── email_log.txt                # System log file for resume processing and prediction events
│
└── README.md                    # Project documentation and usage instructions
```

---

## System Architecture

The system follows a modular pipeline:

1. **Resume Input**
   - Resume uploaded in PDF format
2. **Feature Extraction**
   - Text extraction and preprocessing
3. **Prediction Module**
   - Machine learning model predicts acceptance or rejection
4. **Explainability Layer**
   - SHAP and interpretable models explain predictions
5. **Output Layer**
   - Final decision with explanation

---

## Methodology

1. Generate and preprocess synthetic resume data  
2. Perform feature engineering and encoding  
3. Train supervised machine learning models  
4. Save trained models using Pickle  
5. Apply SHAP for feature importance analysis  
6. Generate human-readable explanations for predictions  

---

## Explainable AI Techniques

- **SHAP (SHapley Additive Explanations)**
  - Explains individual predictions
  - Shows contribution of each feature

- **Custom Interpretable Explainers**
  - Converts numerical influence into readable insights  
  - Example:
    - “Strong technical skills increased acceptance probability”
    - “Low experience reduced selection chances”

---

## Model Training & Evaluation

- Models trained using supervised learning techniques  
- Evaluation metrics include:
  - Accuracy
  - Confusion Matrix
  - Classification Report
- Separate components used for prediction and explanation to maintain clarity

---

## Results & Explanation

- The system accurately predicts resume acceptance or rejection  
- Provides clear explanations for every decision  
- Enhances trust and transparency in automated hiring  
- Helps identify strengths and weaknesses in resumes  

---

## How to Run This Project

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/explainable-ai-resume-acceptance.git

2.Install Required Libraries :
pip install pandas numpy scikit-learn shap matplotlib seaborn

3. Run the resume analysis script: python pdf_ana.py

4.Upload a resume PDF to obtain:

-Prediction result (Accepted / Rejected)

-Explainable AI output



