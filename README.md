# Hermes Quant Intelligence Dashboard

Hermes is a premium, real-time market intelligence dashboard—a Bloomberg Terminal for a solo gold quant. It monitors intermarket networks, executes quantitative engines, and provides insights on short-term Gold price pressures.

No orders. No execution. No position management. Just intelligence.

---

## Workspace Structure

* **`app.py`**: Premium standalone Streamlit web application.
* **`hermes_dashboard.ipynb`**: Self-contained Jupyter Notebook featuring the live-updating grid dashboard.
* **`requirements.txt`**: Package dependencies list for local run and cloud deployment.
* **`Dockerfile`**: Containerization settings for cloud VPS, Render, or Railway.

---

## Setup & Running Locally

### 1. Standalone Web Application (Streamlit)
Activate the virtual environment and start the Streamlit server:
```powershell
# Windows
.\.venv\Scripts\Activate.ps1
streamlit run app.py

# macOS/Linux
source .venv/bin/activate
streamlit run app.py
```
This boots the local web server and opens the dashboard at `http://localhost:8501`.

### 2. Jupyter Notebook
1. Open the workspace folder in VS Code.
2. Select [hermes_dashboard.ipynb](file:///c:/Gold%20Hunt/hermes_dashboard.ipynb).
3. Select the Python `.venv` kernel.
4. Click **Run All** cells. Cell 4 runs the live-updating loop.

---

## Deployment (Access Anywhere)

### Option A: Streamlit Community Cloud (Recommended & 100% Free)
Streamlit hosts public Python apps for free directly from GitHub.
1. Push this directory to your public/private GitHub repository.
2. Log in to [Streamlit Community Cloud](https://share.streamlit.io/) with your GitHub account.
3. Click **New App**, select your repository, branch, and specify `app.py` as the main file.
4. Click **Deploy**. Your app will be live and accessible from any desktop or mobile device.

### Option B: Docker Container Deployment
If deploying on a custom VPS, AWS, GCP, fly.io, or Railway:
1. Build the Docker image:
   ```bash
   docker build -t hermes-terminal .
   ```
2. Run the container:
   ```bash
   docker run -d -p 8501:8501 --name hermes-app hermes-terminal
   ```
3. Access the dashboard by browsing to `http://your-server-ip:8501`.
