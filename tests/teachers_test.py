from unittest.mock import patch
from core.apis.assignments.schema import AssignmentGradeSchema, AssignmentSchema
from core.models.assignments import Assignment
from core.libs.helpers import GeneralObject
from core.models.teachers import Teacher


def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED']


def test_grade_assignment_cross(client, h_teacher_2):
    """
    failure case: assignment 1 was submitted to teacher 1 and not teacher 2
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 1,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_bad_grade(client, h_teacher_1):
    """
    failure case: API should allow only grades available in enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": "A"
        }
    )

    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_draft_assignment(client, h_teacher_1):
    """
    failure case: only a submitted assignment can be graded
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1
        , json={
            "id": 2,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'

def test_grade_without_authentication(client):
    """
    failure case: API should reject requests without authentication
    """
    response = client.post(
        '/teacher/assignments/grade',
        json={
            "id": 3,
            "grade": "A"
        }
    )

    assert response.status_code == 401

def test_grade_assignment(client, h_teacher_1):
    payload = {
        'id': 1,
        'grade': 'A'
    }
    grade_assignment_payload = GeneralObject(id=1, grade='A')

    with patch.object(AssignmentGradeSchema, 'load', return_value=grade_assignment_payload):
        with patch.object(Assignment, 'mark_grade', return_value=Assignment(id=1, grade='A')):
            with patch.object(AssignmentSchema, 'dump', return_value=payload):
                response = client.post(
                    '/teacher/assignments/grade',
                    json=payload,
                    headers=h_teacher_1
                )

                assert response.status_code == 200
                data = response.get_json()
                assert data['data']['id'] == 1
                assert data['data']['grade'] == 'A'

def test_student_repr():
    teacher = Teacher()
    teacher.id = 123
    
    assert str(teacher) == '<Teacher 123>'
    assert repr(teacher) == '<Teacher 123>'