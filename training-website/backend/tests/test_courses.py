from sqlalchemy import select

from app.models.user import User
from tests.conftest import TestingSessionLocal


def make_platform_admin(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "course-admin@example.com",
            "full_name": "Course Admin",
            "password": "StrongPassword123!",
        },
    )
    assert response.status_code == 201
    with TestingSessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "course-admin@example.com"))
        user.is_platform_admin = True
        db.commit()
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "course-admin@example.com", "password": "StrongPassword123!"},
    )
    assert login.status_code == 200


def test_non_admin_cannot_manage_courses(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "student@example.com", "full_name": "Student", "password": "StrongPassword123!"},
    )
    response = client.get("/api/v1/admin/courses")
    assert response.status_code == 403


def test_course_lifecycle_and_public_catalogue(client):
    make_platform_admin(client)

    category = client.post(
        "/api/v1/admin/courses/categories",
        json={"name": "Networking", "slug": "networking", "description": "Enterprise networking"},
    )
    assert category.status_code == 201

    course = client.post(
        "/api/v1/admin/courses",
        json={
            "title": "Enterprise Network Architecture",
            "slug": "enterprise-network-architecture",
            "short_description": "Architecture fundamentals",
            "description": "A structured course.",
            "category_id": category.json()["id"],
            "estimated_hours": 12,
        },
    )
    assert course.status_code == 201
    course_id = course.json()["id"]
    assert course.json()["status"] == "draft"

    module = client.post(
        f"/api/v1/admin/courses/{course_id}/modules",
        json={"title": "Foundations", "description": "Core concepts", "order_index": 0},
    )
    assert module.status_code == 201

    lesson = client.post(
        f"/api/v1/admin/courses/{course_id}/modules/{module.json()['id']}/lessons",
        json={
            "title": "Network Architecture Principles",
            "slug": "network-architecture-principles",
            "content": "Course content",
            "order_index": 0,
            "estimated_minutes": 45,
        },
    )
    assert lesson.status_code == 201

    submit = client.post(f"/api/v1/admin/courses/{course_id}/submit-review")
    assert submit.status_code == 200
    assert submit.json()["status"] == "review"

    publish = client.post(f"/api/v1/admin/courses/{course_id}/publish")
    assert publish.status_code == 200
    assert publish.json()["status"] == "published"

    catalogue = client.get("/api/v1/courses")
    assert catalogue.status_code == 200
    assert [item["slug"] for item in catalogue.json()] == ["enterprise-network-architecture"]

    structure = client.get("/api/v1/courses/enterprise-network-architecture/structure")
    assert structure.status_code == 200
    assert structure.json()["modules"][0]["lessons"][0]["title"] == "Network Architecture Principles"


def test_course_prerequisite_validation(client):
    make_platform_admin(client)

    first = client.post(
        "/api/v1/admin/courses",
        json={"title": "Networking Basics", "slug": "networking-basics"},
    )
    assert first.status_code == 201

    second = client.post(
        "/api/v1/admin/courses",
        json={
            "title": "Advanced Networking",
            "slug": "advanced-networking",
            "prerequisite_course_ids": [first.json()["id"]],
        },
    )
    assert second.status_code == 201

    invalid = client.post(
        "/api/v1/admin/courses",
        json={
            "title": "Invalid Course",
            "slug": "invalid-course",
            "prerequisite_course_ids": [99999],
        },
    )
    assert invalid.status_code == 400
