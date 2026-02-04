from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from pathlib import Path
from typing import List


app = FastAPI(
    title="ApexAsset AI Backend",
    version="0.1.0",
    description="Backend API for ApexAsset AI.",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/srs", response_class=PlainTextResponse)
def get_srs() -> str:
    repo_root = Path(__file__).resolve().parents[2]
    srs_path = repo_root / "README.md"
    if not srs_path.exists():
        return "SRS not found."
    return srs_path.read_text(encoding="utf-8")


class KPI(BaseModel):
    label: str
    value: str
    change: str
    tone: str


class ModuleCard(BaseModel):
    title: str
    summary: str
    bullets: List[str]
    status: str


class Alert(BaseModel):
    title: str
    severity: str
    time: str
    action: str


class DashboardResponse(BaseModel):
    kpis: List[KPI]
    modules: List[ModuleCard]
    alerts: List[Alert]


@app.get("/dashboard", response_model=DashboardResponse)
def get_dashboard() -> DashboardResponse:
    return DashboardResponse(
        kpis=[
            KPI(label="Assets Monitored", value="128", change="+4% WoW", tone="positive"),
            KPI(label="Active Alerts", value="7", change="-2 since 24h", tone="positive"),
            KPI(label="Production Efficiency", value="92.4%", change="+1.3% WoW", tone="positive"),
            KPI(label="Maintenance Backlog", value="18", change="+3 new", tone="warning"),
        ],
        modules=[
            ModuleCard(
                title="Exploration",
                summary="Seismic interpretation and prospect evaluation.",
                bullets=["3D seismic viewer", "Well log correlation", "Risked resources"],
                status="Ready",
            ),
            ModuleCard(
                title="Development",
                summary="Reservoir planning and economics.",
                bullets=["Reservoir model maps", "Well planning canvas", "NPV scenarios"],
                status="Planned",
            ),
            ModuleCard(
                title="Production",
                summary="Real-time monitoring and optimization.",
                bullets=["1Hz dashboards", "Alarm management", "Energy efficiency"],
                status="Live",
            ),
            ModuleCard(
                title="Maintenance",
                summary="Condition monitoring and RUL forecasting.",
                bullets=["Vibration analytics", "Failure probability", "Work orders"],
                status="Live",
            ),
            ModuleCard(
                title="Decommissioning",
                summary="End-of-life planning and compliance.",
                bullets=["Cost estimation", "Regulatory tracking", "Rehab planning"],
                status="Planned",
            ),
        ],
        alerts=[
            Alert(
                title="Compressor A2 vibration",
                severity="High",
                time="5m ago",
                action="Inspect within 2h",
            ),
            Alert(
                title="Separator pressure spike",
                severity="Medium",
                time="22m ago",
                action="Validate control loop",
            ),
            Alert(
                title="Water breakthrough risk",
                severity="Low",
                time="1h ago",
                action="Review water cut trend",
            ),
        ],
    )
