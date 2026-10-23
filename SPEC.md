# GradeLens — Rubric Based AI Powered Smart Evaluation System

## 1. Project Overview

GradeLens is an AI-powered assignment and exam evaluation platform designed for universities, teachers, and students. It uses large language models (LLMs) to evaluate students’ written answers against teacher-provided rubrics or sample answers, suggest marks, and generate personalized feedback explaining their strengths, mistakes, missing concepts, and areas for improvement.

The system combines rule-based grading for multiple-choice questions (MCQs), OCR to extract text from typed, scanned, or handwritten PDF submissions, and AI-powered evaluation for written answers. Teachers can review, edit, and approve AI-generated results before students receive their grades and detailed PDF feedback reports. By automating the initial evaluation process, GradeLens reduces teachers’ grading workload while helping students understand their mistakes and improve their learning extensively.

### 1.1 Main objectives

-   Reduce the time teachers spend preparing individualized feedback.
-   Give students actionable explanations of strengths, mistakes,
    missing concepts, and ways to improve.
-   Support typed PDFs and scanned handwritten PDFs.
-   Keep grading transparent and subject to teacher review.
-   Give teachers class-level analytics to identify common mistakes and
    topics that need further teaching.
-   Use the stated free/open-source stack where possible, with Groq's
    free tier for LLM inference.

------------------------------------------------------------------------

## 2. Problem Statement

Instructors often teach large classes and cannot provide detailed,
personalized feedback to every student. Students may receive a grade
without understanding which concepts they missed, what they did
correctly, or how to improve. Manual grading at scale can be slow and
inconsistent.

The platform automates the first draft of feedback while keeping the
teacher in control of the final result. It combines objective
auto-grading, OCR-based text extraction, LLM-assisted written-answer
evaluation, teacher approval, PDF feedback reports, and class-wide
analytics.

------------------------------------------------------------------------

## 3. Proposed Solution and Main Workflow

1.  A teacher registers or signs in and creates a class.
2.  The system generates a unique class join code and a shareable invite
    link.
3.  Students register or sign in and join the class using the code or
    link.
4.  The teacher creates an assignment or exam and adds MCQ and/or
    written questions.
5.  For each MCQ, the teacher configures options and the correct answer.
    For each written question, the teacher provides either a rubric or a
    sample answer.
6.  Students submit a single PDF before the deadline.
7.  The backend stores the submission and extracts text from the PDF
    using python libraries.
8.  MCQs are graded using direct answer comparison. Written answers are
    evaluated by a Groq LLM through LangChain ChatGroq.
9.  The system stores all AI scores and feedback as drafts.
10. The teacher reviews and can edit question scores, feedback, and
    overall comments.
11. The teacher explicitly approves the student's feedback.
12. Only after approval can the student see the final feedback and
    download a PDF report.
13. The teacher can view class-level analytics, including score
    statistics and charts.

------------------------------------------------------------------------


## 4. Target Users and Permissions

### 4.1 Teacher / Professor

Teachers can:

- Register and sign in as a teacher.
- Create and manage multiple classes and subjects
- Create assignments and exams with mixed question types
- Define correct answers for MCQs
- Define rubrics or sample answers for written questions
- View submissions for assignments belonging to their own classes.
- Review, edit, and approve AI-generated draft feedback
- View class-wide analytics with visual charts after grading


### 4.2 Student

Students can:

- Register and sign in as a student.
- Join classes via a unique code or shareable invite link
- View classes in which they are enrolled.
- View all assignments and deadlines for enrolled classes
- Upload and submit assignments as PDF files
- Download approved feedback report as a PDF

------------------------------------------------------------------------
## **CORE FEATURES**
## 5. Functional Requirements 

### 5.1 Authentication and Role Management

- Separate sign-up and login for Teachers and Students
- User selects role at sign-up (Teacher or Student)
- JWT token authentication with role embedded in token payload
- Role-based access control on both frontend and backend
- Teachers access: class creation, assignment creation,
  feedback approval, analytics dashboard
- Students access: class enrollment, submission, feedback download
- Passwords hashed securely using bcrypt
- Protected routes — unauthenticated users redirected to login

### 5.2 Class Management

- Teacher creates a class with a name and subject
- System auto-generates a unique 6-character alphanumeric join code
- System generates a shareable invite link containing the join code
- Students join by entering the code or clicking the link
- Teacher does not manually add students — enrollment is self-service
- Teacher can view all enrolled students per class
- Teacher manages multiple classes from a single dashboard

### 5.3 Assignment and Exam Creation

- Teacher creates an assignment under a specific class
- Sets title, description, total marks, and submission deadline
- An assignment can contain a mixture of MCQ and written-answer questions.
- Supports two question types in the same assignment:

#### 5.3.1 MCQ questions

- Teacher writes the question text
- Teacher defines 4 answer options (A, B, C, D)
- Teacher selects the correct answer
- System auto-grades student responses — no LLM involved
- Full marks or zero per MCQ question


#### 5.3.2 Written-answer questions

-   Teacher enters the question text and marks available.
-   Teacher supplies **one** evaluation reference:
    -   **Rubric:** marking criteria and, where appropriate, marks
        assigned to each criterion.
    -   **Sample answer:** a model answer used as a reference for
        evaluating the student's answer.
-   The application validates that a written question has the required
    evaluation reference before it can be used for AI grading.
-   The system sends the question, available marks, reference material,
    and extracted student answer to the LLM.
-   The AI returns a proposed score, justification, strengths, missing
    or incorrect concepts, and actionable improvement suggestions.

### 5.4 Student Assignment View and Submission

- Student views all active assignments across enrolled classes
- Student uploads a single PDF per assignment:
  - Typed and exported as PDF
  - Word document converted to PDF before uploading
  - Handwritten paper scanned via CamScanner and saved as PDF
- System stores the PDF and records submission timestamp
- Upload button disabled after deadline — Submission Closed message shown
- Student can view submission status:
  - Submitted — awaiting grading
  - Feedback Pending — graded but not yet approved by teacher
  - Feedback Ready — approved and available to download

### 5.5 AI Evaluation Pipeline

#### 5.5.1 Step 1 — PDF Text Extraction (PyMuPDF + OCR Fallback)
- PyMuPDF first attempts native text extraction on each page of the uploaded PDF
- If a page contains little or no extractable text (scanned or handwritten pages), PyMuPDF renders that page as an image and EasyOCR extracts the text from it
- Extracted text from all pages is combined, cleaned, and mapped to the corresponding questions by question number

#### 5.5.2 Step 2 — MCQ Auto-Grading
- Student answer compared directly to teacher-defined correct answer
- Marks assigned as full marks or zero
- No LLM call made for MCQ questions — instant and 100% accurate

#### 5.5.3 Step 3 — Written Answer LLM Evaluation
- Structured prompt sent to Groq LLM via LangChain ChatGroq
- Prompt includes: question text, total marks, rubric or sample
  answer, and student extracted answer
- LLM returns for each question:
  - Score out of total marks with justification
  - Strengths: what the student did well
  - Lackings: what was missed or incorrect
  - Improvement suggestions: specific actionable advice
- LLM uses both teacher-provided content and its own world knowledge
- All LLM output stored as draft — never shown to students directly

#### 5.5.4 Evaluation Prompt Template
You are a university examiner. Evaluate the student answer fairly.

Question: {question_text} Total Marks: {marks}

[If rubric provided] Marking Rubric: {rubric_text}

[If sample answer provided] Sample Answer (use as benchmark): {sample_answer_text}

Student Answer: {extracted_student_answer}

Provide:

Score out of {marks} with justification
Strengths — what the student did well
Lackings — what was missed or wrong
Improvement suggestions — specific and actionable

**Required output format (structured JSON)**

The LLM must respond with valid JSON only — no extra text, explanations, or Markdown code fences outside the JSON.

The prompt ends with the following instruction:

Respond ONLY with a valid JSON object in exactly this format:

```json
{
  "score": 0,
  "justification": "",
  "strengths": ["", ""],
  "lackings": ["", ""],
  "suggestions": ["", ""]
}
```

The `score` must be a number between 0 and the question's maximum marks.

**Handling the response**

- The backend parses the JSON and validates it.
- All required keys must be present.
- The score must be a number between 0 and the question's maximum marks.
- `strengths`, `lackings`, and `suggestions` must be lists of strings.
- If the response is invalid or cannot be parsed, the backend retries the LLM call once.
- If it still fails, the answer is flagged for manual grading by the teacher instead of being given a score.

**Mapping the parsed fields to the Answers table**

| LLM JSON field | Answers table column |
|---|---|
| `score` | `ai_score` |
| `justification` | `ai_feedback` |
| `strengths` | `ai_strengths` |
| `lackings` | `ai_lackings` |
| `suggestions` | `ai_suggestions` |

### 5.6 Teacher Review and Approval
- Teacher dashboard shows all student submissions per assignment
- For each student submission, teacher sees:
  - AI-generated score per question with justification
  - AI-generated draft feedback per question
  - Strengths, lackings, and improvement suggestions per question
  - Total AI-calculated score and percentage
- Teacher can edit score and feedback text for any question
- Teacher clicks Approve to finalize a student's feedback
- Student sees Feedback Pending until teacher approves
- Human-in-the-loop guaranteed — AI assists, teacher decides

### 5.7 Student PDF Feedback Report
- After approval, Download Feedback button appears for the student
- PDF generated on demand using FPDF (Python library)
- Report contains:
  - Platform header
  - Student name, class name, assignment title
  - Submission date and feedback approval date
  - Total score, percentage, and pass or fail indicator (pass mark is set per assignment, default 50%)
  - Per-question breakdown:
    - Question number and text
    - Student submitted answer
    - Score awarded out of total marks
    - Teacher-approved feedback
    - Strengths identified
    - Lackings identified
    - Improvement suggestions
  - Overall summary section
  - Professional formatting with clear sections and borders

### 5.8 Class-Wide Analytics Dashboard (Teacher)
- Teacher accesses analytics view after grading an assignment
- Visual charts rendered using Recharts on the frontend:
  - Bar chart: score distribution across the class
  - Bar chart: marks per question (class average vs full marks)
- Summary statistics displayed alongside charts:
  - Class average score and percentage
  - Highest score and lowest score in the class
  - Number of students who passed vs failed
  - Most commonly missed questions (ranked list)
  - Weak topics and concepts flagged most frequently by AI
- Helps teacher identify what to re-teach or address next class

------------------------------------------------------------------------


## 6. Technology Stack

| Layer            | Technology                          |
|------------------|-------------------------------------|
| Frontend         | Next.js + React + Tailwind CSS      |
| Backend          | Python + FastAPI                    |
| Database         | PostgreSQL                          |
| ORM              | SQLAlchemy                          |
| Authentication   | JWT (role-based: Teacher / Student) |
| OCR              | EasyOCR + PyMuPDF                   |
| AI Evaluation    | Groq API via LangChain ChatGroq     |
| PDF Generation   | FPDF (Python)                       |
| File Storage     | Local filesystem / server storage   |


------------------------------------------------------------------------

## 7. Responsibilities

-   **Frontend:** role-specific screens, forms, uploads, status
    displays, teacher review UI, analytics charts, and PDF download
    actions.
-   **FastAPI:** authentication, authorization, input validation,
    business rules, deadlines, submission processing, grading
    orchestration, approval gating, analytics aggregation, and report
    access.
-   **PostgreSQL:** users, classes, enrollments, assignments, questions,
    submissions, answers, and report metadata.
-   **Text extraction pipeline:** native PDF text extraction with PyMuPDF, with EasyOCR as a fallback for scanned or handwritten pages.
-   **LLM service:** proposed evaluation of written answers.
-   **FPDF:** generation of the final student-facing report after
    approval.
-   **Recharts:** visualizations rendered in the frontend using
    analytics returned by the API.

------------------------------------------------------------------------

## 8. Database Schema

### Users
- id, name, email, password_hash, role, created_at

### Classes
- id, teacher_id, name, subject, join_code, created_at

### Enrollments
- id, student_id, class_id, joined_at

### Assignments
- id, class_id, title, description, total_marks, deadline, created_at

### Questions
- id, assignment_id, type (mcq or written), text, marks,
  options (MCQ), correct_answer (MCQ), rubric (written),
  sample_answer (written)

### Submissions
- id, assignment_id, student_id, pdf_path, submitted_at, status

### Answers
- id, submission_id, question_id, extracted_text, ai_score,
  ai_feedback, ai_strengths, ai_lackings, ai_suggestions,
  teacher_score, teacher_feedback, is_approved

### FeedbackReports
- id (integer, primary key, auto-increment)
- submission_id (foreign key → Submissions.id, unique)
- pdf_path (string — file path to generated PDF on server)
- generated_at (timestamp — when PDF was generated)
- is_downloaded (boolean — whether student has downloaded it)

------------------------------------------------------------------------

## 9. API Endpoints

### Auth
- POST /auth/register — register as teacher or student
- POST /auth/login — login and receive JWT token

### Classes
- POST /classes — teacher creates a class
- GET /classes — teacher gets all their classes
- POST /classes/join — student joins via code
- GET /classes/{id}/students — teacher views enrolled students

### Assignments
- POST /classes/{id}/assignments — teacher creates assignment
- GET /classes/{id}/assignments — list assignments for a class
- GET /assignments/{id} — get assignment details and questions

### Submissions
- POST /assignments/{id}/submit — student uploads PDF
- GET /assignments/{id}/submissions — teacher views all submissions

### Grading
- GET /submissions/{id}/review — teacher views AI feedback draft
- PATCH /submissions/{id}/approve — teacher edits and approves
- GET /submissions/{id}/feedback-pdf — student downloads feedback PDF

### Analytics
- GET /assignments/{id}/analytics — teacher views class analytics

------------------------------------------------------------------------

## 10. AI Evaluation Flow

1. Student uploads PDF
2. PyMuPDF extracts text from each page
3. For pages with no readable text, PyMuPDF renders the page as an image and EasyOCR extracts the text
4. Text mapped to questions by number
5. MCQ answers auto-graded by direct comparison
6. Written answers sent to the Groq LLM using the prompt template in Section 5.5.4
7. LLM output stored as draft
8. Teacher reviews, edits, and approves
9. FPDF generates student feedback PDF on approval

------------------------------------------------------------------------

## 11. Analytics Dashboard (Teacher)
- Class average score and percentage
- Highest and lowest score in the class
- Number of students passed vs failed
- Score distribution bar chart (Recharts)
- Marks per question bar chart (class average vs full marks)
- Most commonly missed questions ranked list
- Weak topics flagged most frequently by AI

------------------------------------------------------------------------

## 12. Constraints
- All submissions must be PDF format only
- AI feedback never visible to students without teacher approval
- Free or open-source tools are used throughout. Groq’s free tier is the only external API.
- System supports a teacher managing multiple classes simultaneously
- Submissions locked automatically after assignment deadline

------------------------------------------------------------------------

## 13. Future Scope
- Math equation and diagram recognition
- Coding assignment execution and testing
- Email notifications for deadlines and feedback
- Plagiarism detection across submissions
- Mobile app for students
- Integration with Moodle or Canvas LMS
- Peer review between students

------------------------------------------------------------------------

## 14. Team and Project Links

-   **Team members:** Arsalna Shaikh, Ayesha Amir, Afeerah Shafqat
-   **GitHub repository:** https://github.com/Arsalna-Shaikh/GradeLens-Rubric-Based-AI-Powered-Smart-Evaluation-System


**End of specification.**


## Phase 11 hardening notes

Production readiness requires running `npm run test:backend` against the configured PostgreSQL database and exercising the teacher/student journey. Access tokens are accepted through Authorization, X-Auth-Token, X-Access-Token, and query fallback transport for constrained preview proxies. Students receive only released submissions and reports; AI draft fields remain teacher-only. Submission deadlines and teacher-score approval are enforced server-side. Groq is optional and must be supplied through Secrets, never committed.
