from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.api import deps
from backend.app.core.database import get_db
from backend.app.models.dashboard import Dashboard
from backend.app.models.project import Project
from backend.app.models.user import User
from backend.app.schemas.dashboard import DashboardCreate, DashboardResponse, DashboardUpdate

router = APIRouter()


@router.post("/", response_model=DashboardResponse, status_code=status.HTTP_201_CREATED)
def create_dashboard(
    dash_in: DashboardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Create a new visualization dashboard within a project."""
    project = db.query(Project).filter(Project.id == dash_in.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    dashboard = Dashboard(
        project_id=dash_in.project_id,
        name=dash_in.name,
        layout_json=dash_in.layout_json or {}
    )
    db.add(dashboard)
    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.get("/", response_model=List[DashboardResponse])
def list_dashboards(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """List all dashboards in a project."""
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(Dashboard).filter(Dashboard.project_id == project_id).all()


@router.get("/{dashboard_id}", response_model=DashboardResponse)
def get_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Retrieve details of a dashboard layout."""
    dashboard = db.query(Dashboard).join(Project).filter(
        Dashboard.id == dashboard_id,
        Project.user_id == current_user.id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return dashboard


@router.put("/{dashboard_id}", response_model=DashboardResponse)
def update_dashboard(
    dashboard_id: str,
    dash_in: DashboardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Update dashboard configuration or widget grid layouts."""
    dashboard = db.query(Dashboard).join(Project).filter(
        Dashboard.id == dashboard_id,
        Project.user_id == current_user.id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    if dash_in.name is not None:
        dashboard.name = dash_in.name
    if dash_in.layout_json is not None:
        dashboard.layout_json = dash_in.layout_json

    db.commit()
    db.refresh(dashboard)
    return dashboard


@router.delete("/{dashboard_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """Delete a dashboard layout."""
    dashboard = db.query(Dashboard).join(Project).filter(
        Dashboard.id == dashboard_id,
        Project.user_id == current_user.id
    ).first()
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    db.delete(dashboard)
    db.commit()
    return None
export_models = [DashboardResponse]
