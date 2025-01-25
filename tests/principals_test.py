from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum
from core import db

def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    assignment = Assignment.get_by_id(4)
    assignment.state = AssignmentStateEnum.GRADED
    db.session.commit()

    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B

def test_grade_assignment_invalid_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 999,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 404
    assert response.json['error'] == 'FyleError'
    assert response.json['message'] == 'No assignment with this id was found'

def test_list_teachers(client, h_principal):
    response = client.get(
        '/principal/teacher',
        headers=h_principal
    )

    assert response.status_code == 200
    
    data = response.json['data']
    assert isinstance(data, list)
    for teacher in data:
        assert 'id' in teacher
        assert 'user_id' in teacher
        assert 'created_at' in teacher
        assert 'updated_at' in teacher