from flask_restful import Resource
from flask_jwt_extended import jwt_required


class VistaSignup(Resource):
    def post(self):
        pass


class VistaLogin(Resource):
    def post(self):
        pass


class VistaTask(Resource):
    @jwt_required()
    def get(self, id_task):
        pass

    @jwt_required()
    def delete(self, id_task):
        pass


class VistaTasks(Resource):
    @jwt_required()
    def get(self):
        pass

    @jwt_required()
    def post(self):
        pass


class VistaFiles(Resource):
    @jwt_required()
    def get(self, filename):
        pass
