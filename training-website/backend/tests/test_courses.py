def test_non_admin_cannot_manage_courses(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "student@example.com", "full_name": "Student", "password": "StrongPassword123!"},
    )
    response = client.get("/api/v1/admin/courses")
    assert response.status_code == 403


def test_course_lifecycle_and_public_catalogue(platform_admin):
    client = platform_admin

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


def test_course_prerequisite_validation(platform_admin):
    client = platform_admin

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


def test_course_editor_authoring_endpoints(platform_admin):
    client = platform_admin

    prerequisite = client.post(
        "/api/v1/admin/courses",
        json={"title": "Prerequisite Course", "slug": "prerequisite-course"},
    )
    assert prerequisite.status_code == 201

    course = client.post(
        "/api/v1/admin/courses",
        json={
            "title": "Authoring Course",
            "slug": "authoring-course",
            "prerequisite_course_ids": [prerequisite.json()["id"]],
        },
    )
    assert course.status_code == 201
    course_id = course.json()["id"]

    prerequisites = client.get(f"/api/v1/admin/courses/{course_id}/prerequisites")
    assert prerequisites.status_code == 200
    assert [item["id"] for item in prerequisites.json()] == [prerequisite.json()["id"]]

    module = client.post(
        f"/api/v1/admin/courses/{course_id}/modules",
        json={"title": "Module One", "description": "Initial", "order_index": 0},
    )
    assert module.status_code == 201
    module_id = module.json()["id"]

    updated_module = client.patch(
        f"/api/v1/admin/courses/{course_id}/modules/{module_id}",
        json={"title": "Updated Module", "description": "Updated", "order_index": 0},
    )
    assert updated_module.status_code == 200
    assert updated_module.json()["title"] == "Updated Module"

    lesson = client.post(
        f"/api/v1/admin/courses/{course_id}/modules/{module_id}/lessons",
        json={
            "title": "Lesson One",
            "slug": "lesson-one",
            "content_type": "text",
            "content": "Initial lesson",
            "order_index": 0,
            "estimated_minutes": 30,
        },
    )
    assert lesson.status_code == 201
    lesson_id = lesson.json()["id"]

    updated_lesson = client.patch(
        f"/api/v1/admin/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}",
        json={
            "title": "Updated Lesson",
            "content_type": "video",
            "content": "Updated lesson",
            "order_index": 0,
        },
    )
    assert updated_lesson.status_code == 200
    assert updated_lesson.json()["content_type"] == "video"

    topic = client.post(
        f"/api/v1/admin/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/topics",
        json={"title": "Topic One", "content": "Topic content", "order_index": 0},
    )
    assert topic.status_code == 201
    topics = client.get(
        f"/api/v1/admin/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/topics"
    )
    assert topics.status_code == 200
    assert topics.json()[0]["title"] == "Topic One"

    resource = client.post(
        f"/api/v1/admin/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/resources",
        json={
            "name": "Reference",
            "resource_type": "link",
            "url": "https://example.com/reference",
            "description": "Reference material",
        },
    )
    assert resource.status_code == 201
    resources = client.get(
        f"/api/v1/admin/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/resources"
    )
    assert resources.status_code == 200
    assert resources.json()[0]["name"] == "Reference"

    lab = client.post(
        f"/api/v1/admin/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/lab-references",
        json={
            "reference_key": "networking-lab-01",
            "display_name": "Networking Lab 01",
            "metadata_json": "{\"topology\": \"basic\"}",
        },
    )
    assert lab.status_code == 201
    labs = client.get(
        f"/api/v1/admin/courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/lab-references"
    )
    assert labs.status_code == 200
    assert labs.json()[0]["reference_key"] == "networking-lab-01"
