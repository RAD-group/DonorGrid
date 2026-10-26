# DonorGrid: Smart Blood Donation Camp Management and Donor Prediction System

A web system for running blood donation camps. It keeps donors, camps, donations and blood stock in one place, and uses machine learning to predict which donors are likely to return, when a blood group's stock may run short, and where the next camp should be held.

Group mini project, B.Tech Computer Science and Engineering, Sri Manakula Vinayagar Engineering College (academic year 2025–2026), under the guidance of Dr. N. Danapaquiame.

| Team member | Register No. |
| --- | --- |
| Revanthkumar S | 23UCS130 |
| Amish S R | 23UCS011 |
| Dayaanidhi S V | 23UCS031 |

## Architecture
| Part | Folder | Technology |
| --- | --- | --- |
| Web interface with four role-based dashboards | `frontend/` | React 18, Axios |
| REST API, authentication and business logic | `backend/` | Java 17, Spring Boot 3.2, Spring Security, JWT, JPA |
| Database | `database/` | PostgreSQL (`schema.sql`, `seed.sql`) |
| Prediction service and chat assistant | `ml-service/` | Python 3.12, FastAPI, scikit-learn |

The React app calls the Spring Boot API at port 8080. The API stores data in PostgreSQL and asks the FastAPI service at port 8000 for predictions.

## Roles
| Role | What it can do |
| --- | --- |
| Super Admin | sees all data and manages users |
| Camp Coordinator | manages camps and gets location recommendations |
| Hospital Admin | manages blood stock and sees shortage alerts |
| Donor | checks eligibility, registers and sees predictions |

## The four CPPE modules
- **Data Engineering:** a normalised PostgreSQL schema for users, donors, camps, donations and blood stock (`database/schema.sql`), with seed data (`database/seed.sql`) and JPA repositories in the backend.
- **AI Engineering:** three scikit-learn models served by FastAPI (`ml-service/`):
  - a Random Forest that predicts whether a donor will return;
  - a regression model that forecasts the next 7 days of blood stock use and raises shortage alerts;
  - K-Means clustering that recommends camp locations.

  A chat assistant answers blood donation questions through a Hugging Face model when a key is set, and through built-in answers otherwise. The models are trained by `ml-service/train_models.py` on generated (synthetic) data with a fixed seed, not on real donor records.
- **Security Engineering:**
  - passwords are hashed with BCrypt;
  - logins issue signed JWTs, and every API route is restricted by role;
  - secrets come from environment variables (`.env.example`), never from the code;
  - only the frontend's origin is allowed by CORS;
  - nobody can give themselves the Super Admin role at signup;
  - login errors don't reveal which usernames exist.
- **Cloud Engineering:** the group report describes the deployment on AWS during the semester: EC2 for the backend and ML service, S3 for the frontend and RDS for PostgreSQL. This repository contains no deployment scripts.

## How to run
See [HOW_TO_RUN.md](HOW_TO_RUN.md) for the full steps on Windows, macOS and Linux. In short:
1. Create the database and load `database/schema.sql` and `database/seed.sql`.
2. Set `DB_PASSWORD` and `JWT_SECRET`, then start the backend with `mvn spring-boot:run` in `backend/`.
3. In `ml-service/`, install the requirements and start the service with `python -m uvicorn main:app --port 8000`.
4. In `frontend/`, run `npm install`, then `npm start`.

The seed data's demo accounts are listed in HOW_TO_RUN.md. Use them on your own machine only.

## Tests
```
cd ml-service
pip install -r requirements.txt pytest httpx
python -m pytest tests
```
There are 8 tests. They check each prediction endpoint, the rejection of bad input, the chat fallback without a key, that no key is in the code, and that CORS refuses other websites.
