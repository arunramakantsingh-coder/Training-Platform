def test_training_session_enrollment_and_progress(client, platform_admin):
    client.post(
        "/api/v1/auth/register",
        json={"email": "learner@example.com", "full_name": "Learner", "password": "StrongPassword123!"},
    )
    course = platform_admin.post(
        "/api/v1/admin/courses",
        json={"title": "SD-WAN Fundamentals", "slug": "sdwan-fundamentals"},
    )
    course_id = course.json()["id"]
    module = platform_admin.post(
        f"/api/v1/admin/courses/{course_id}/modules",
        json={"title": "Module 1", "order_index": 0},
    )
    lesson = platform_admin.post(
        f"/api/v1/admin/courses/{course_id}/modules/{module.json()['id']}/lessons",
        json={"title": "Lesson 1", "slug": "lesson-1", "content": "Learn SD-WAN", "order_index": 0},
    )
    assert lesson.status_code == 201
    assert platform_admin.post(f"/api/v1/admin/courses/{course_id}/submit-review").status_code == 200
    assert platform_admin.post(f"/api/v1/admin/courses/{course_id}/publish").status_code == 200

    session = platform_admin.post(
        f"/api/v1/admin/training/courses/{course_id}/sessions",
        json={"name": "October Cohort", "slug": "october-cohort", "enrollment_limit": 25},
    )
    assert session.status_code == 201
    session_id = session.json()["id"]
    opened = platform_admin.patch(
        f"/api/v1/admin/training/sessions/{session_id}", json={"status": "open"}
    )
    assert opened.status_code == 200

    learner = client.post(
        "/api/v1/auth/login",
        json={"email": "learner@example.com", "password": "StrongPassword123!"},
    )
    assert learner.status_code == 200

    public_detail = client.get("/api/v1/training/catalogue/sdwan-fundamentals")
    assert public_detail.status_code == 200
    assert public_detail.json()["modules"][0]["lessons"][0]["title"] == "Lesson 1"

    enrollment = client.post(
        f"/api/v1/training/courses/{course_id}/enroll",
        json={"training_session_id": session_id},
    )
    assert enrollment.status_code == 201

    progress = client.post(
        f"/api/v1/training/enrollments/{enrollment.json()['id']}/progress/{lesson.json()['id']}",
        json={"status": "completed"},
    )
    assert progress.status_code == 200
    assert progress.json()["status"] == "completed"

    learner_course = client.get("/api/v1/training/courses/sdwan-fundamentals")
    assert learner_course.status_code == 200
    assert learner_course.json()["progress_percent"] == 100
    assert learner_course.json()["enrollment"]["status"] == "completed"
