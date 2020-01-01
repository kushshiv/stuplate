from app import app, db
from app.models import User, CoachingClass, CoachingTeachers, StudentDetails, CoachingBatches, StudentCoachingRelation

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'CoachingClass': CoachingClass, 'CoachingTeachers': CoachingTeachers, 'StudentDetails': StudentDetails, 'CoachingBatches':CoachingBatches, 'StudentCoachingRelation':StudentCoachingRelation}
