from flask import abort
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from models.consumer_model import Consumer, ConsumerSchema

api = Namespace('consumer', description='API to register consumers')

consumer_schema = ConsumerSchema()
consumers_schema = ConsumerSchema(many=True)

consumer_model = api.model('Consumer', {
    'name': fields.String(required=True, description='Name')
})


@api.route('')
class ConsumerList(Resource):
    @jwt_required
    @api.doc('get_consumers')
    def get(self):
        '''Get All Consumers'''
        db_consumers = Consumer.fetch_all()
        if len(db_consumers) == 0:
            return {'message': 'There are no registered consumers.'}, 400
        consumers = consumers_schema.dump(db_consumers)
        return consumers, 200

    @jwt_required
    @api.doc('add_consumer')
    @api.expect(consumer_model)
    def post(self):
        '''Add Consumer'''
        data = api.payload
        if not data:
            abort(400, 'No input data detected')

        name = data['name']
        this_consumer = Consumer.fetch_by_name(name)
        if this_consumer:
            abort(400, 'A consumer with this name already exists')

        authorised_user = get_jwt_identity()
        user_id = authorised_user['id']

        new_consumer = Consumer(name=name, user_id=user_id)
        new_consumer.insert_record()

        consumer = consumer_schema.dump(data)
        return consumer, 201

@api.route('/<int:id>')
@api.param('id', 'The consumer identifier')
class ConsumerOperations(Resource):
    @jwt_required
    @api.doc('get_consumers')
    def get(self, id):
        '''Get All Consumers'''
        this_consumer = Consumer.fetch_by_id(id)
        if this_consumer:
            consumer = consumer_schema.dump(this_consumer)
            return consumer, 200
        return {'message':'There is no such user.'}, 400

    @jwt_required
    @api.doc('edit_consumer')
    @api.expect(consumer_model)
    def put(self, id):
        '''Edit Consumer Name'''
        my_consumer = Consumer.fetch_by_id(id)
        consumer = consumer_schema.dump(my_consumer)
        if len(consumer) == 0:
            abort(400, 'Consumer does not exist')
        
        authorised_user = get_jwt_identity()
        if my_consumer.user_id != authorised_user['id']:
            abort(400, 'You do not have the required permissions!')

        data = api.payload
        if not data:
            abort(400, 'No input data detected')

        name = data['name']

        db_consumer = Consumer.fetch_by_name(name)
        consumer_to_check = consumer_schema.dump(db_consumer)
        if len(consumer_to_check) > 0:
            if id != consumer_to_check['id']:
                abort(400, 'Falied... A Consumer with this name already exists')
        Consumer.update(id, name=name)
        this_consumer = Consumer.fetch_by_id(id)
        consumer = consumer_schema.dump(this_consumer)
        return consumer, 200

    @jwt_required
    @api.doc('delete_user')
    def delete(self, id):
        '''Delete User'''
        this_consumer = Consumer.fetch_by_id(id)
        consumer = consumer_schema.dump(this_consumer)
        if len(consumer) == 0:
            abort(400, 'Consumer does not exist')

        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        if this_consumer.user_id != authorised_user['id']:  # 403
            abort(400, 'You do not have the required permissions to delete this consumer!')

        Consumer.delete_by_id(id)
        msg = 'Consumer {} has been deleted'.format(this_consumer.name)

        return {'message': msg}, 200


@api.route('/suspend/<int:id>')
@api.param('id', 'The consumer identifier')
class SuspendConsumer(Resource):
    @jwt_required
    @api.doc('get_consumers')
    def put(self, id):
        '''Suspend Consumer'''
        this_consumer = Consumer.fetch_by_id(id)
        consumer = consumer_schema.dump(this_consumer)
        if len(consumer) == 0:
            abort(400, 'Consumer does not exist')

        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        if claims['is_admin'] or this_consumer.user_id == authorised_user['id']:
            is_suspended = 1
            try:
                Consumer.suspend(id, is_suspended=is_suspended)
                return {'message': 'Consumer suspended successfuly'}, 200
            except:
                return{'message': 'Unable to perform this action'}, 400

        abort(400, 'You do not have the required permissions!')


@api.route('/restore/<int:id>')
@api.param('id', 'The consumer identifier')
class RestoreConsumer(Resource):
    @jwt_required
    @api.doc('get_consumers')
    def put(self, id):
        '''Restore Consumer'''
        this_consumer = Consumer.fetch_by_id(id)
        consumer = consumer_schema.dump(this_consumer)
        if len(consumer) == 0:
            abort(400, 'Consumer does not exist')

        claims = get_jwt_claims()
        authorised_user = get_jwt_identity()
        if claims['is_admin'] or this_consumer.user_id == authorised_user['id']:
            is_suspended = 2
            try:
                Consumer.suspend(id, is_suspended=is_suspended)
                return {'message': 'Consumer restored successfuly'}, 200
            except:
                return{'message': 'Unable to perform this action'}, 400

        abort(400, 'You do not have the required permissions!')
