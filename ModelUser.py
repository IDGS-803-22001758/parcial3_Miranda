from User import User

class ModelUser:

    @classmethod
    def login(cls, db, user):
        try:
            user_record = db.session.query(User).filter_by(username=user.username).first()

            if user_record and User.check_password(user_record.password, user.password):
                return user_record
            return None
        except Exception as ex:
            raise Exception(f"Error en el login: {ex}")

    @classmethod
    def get_by_id(cls, db, id):
        try:
            user_record = db.session.query(User).filter_by(id=id).first()
            if user_record:
                return user_record  
            return None 
        except Exception as ex:
            raise Exception(f"Error al obtener el usuario por ID: {ex}")
