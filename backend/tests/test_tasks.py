from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.services import create_task
from app.models import Task


# Create an isolated in-memory database for tests
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# Override the database dependency during tests
def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Reset the test database before each test
def setup_function():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


# Test retrieving all tasks
def test_get_tasks():
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


# Test creating a task
def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "id": 1,
            "title": "Learn Docker",
            "completed": False,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Learn Docker",
        "completed": False,
    }


# Test invalid task data
def test_create_task_invalid_data():
    response = client.post(
        "/tasks",
        json={
            "id": "hello",
            "title": 123,
            "completed": "not-a-boolean",
        },
    )

    assert response.status_code == 422


# Test the default completed value
def test_create_task_default_completed():
    response = client.post(
        "/tasks",
        json={
            "id": 2,
            "title": "Learn Kubernetes",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 2,
        "title": "Learn Kubernetes",
        "completed": False,
    }


# Test the create_task service directly
def test_create_task_service():
    db = TestingSessionLocal()

    try:
        task = Task(
            id=10,
            title="Learn Jenkins",
            completed=False,
        )

        result = create_task(db, task)

        assert result.id == 10
        assert result.title == "Learn Jenkins"
        assert result.completed is False

    finally:
        db.close()


# Test updating an existing task
def test_update_task():
    # Create a task first
    client.post(
        "/tasks",
        json={
            "id": 1,
            "title": "Learn Docker",
            "completed": False,
        },
    )

    # Update the task
    response = client.put(
        "/tasks/1",
        json={
            "id": 1,
            "title": "Docker completed",
            "completed": True,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Docker completed",
        "completed": True,
    }


# Test updating a nonexistent task
def test_update_task_not_found():
    response = client.put(
        "/tasks/999",
        json={
            "id": 999,
            "title": "Task does not exist",
            "completed": False,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found"
    }


# Test updating a task when URL and body IDs differ
def test_update_task_id_mismatch():
    response = client.put(
        "/tasks/1",
        json={
            "id": 2,
            "title": "Learn Kubernetes",
            "completed": False,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Task ID in URL must match task ID in request body"
    }


# Test deleting an existing task
def test_delete_task():
    # Create a task first
    client.post(
        "/tasks",
        json={
            "id": 1,
            "title": "Learn Docker",
            "completed": False,
        },
    )

    # Delete the task
    response = client.delete("/tasks/1")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Task deleted successfully"
    }

    # Confirm that the task was deleted
    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == []


# Test deleting a nonexistent task
def test_delete_task_not_found():
    response = client.delete("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found"
    }
    
    
# Test retrieving a single existing task
def test_get_task():
    # Create a task first
    client.post(
        "/tasks",
        json={
            "id": 1,
            "title": "Learn Docker",
            "completed": False,
        },
    )

    # Retrieve the task by ID
    response = client.get("/tasks/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "title": "Learn Docker",
        "completed": False,
    }


# Test retrieving a nonexistent task
def test_get_task_not_found():
    response = client.get("/tasks/999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found"
    }