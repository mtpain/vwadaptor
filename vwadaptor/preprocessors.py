from flask_jwt import jwt_required, current_identity
from flask.ext.restless import ProcessingException

from .extensions import storage
from vwadaptor.modelrun.models import ModelRun, ModelResource

#
# @jwt_required()
# def authorize(**kwargs):
#     pass
#

@jwt_required()
def modelresource_before_delete(instance_id=None,**kwargs):
    resource = ModelResource.query.get(instance_id)
    if not resource:
        return
    modelrun = ModelRun.query.get(resource.modelrun_id)
    if modelrun.user_id != current_identity.id:
        raise ProcessingException(description='You are not authorized to access this ModelResource', code=401)
    obj = storage.get(resource.resource_name)
    if obj:
        obj.delete()



@jwt_required()
def modelrun_before_post(data=None,**kwargs):
    user_id = current_identity.id
    data['user_id'] = user_id
    return data


@jwt_required()
def modelrun_before_get(instance_id=None,**kwargs):
    modelrun = ModelRun.query.get(instance_id)
    if modelrun and modelrun.user_id != current_identity.id:
        raise ProcessingException(description='You are not authorized to access this ModelRun', code=401)
    return None


@jwt_required()
def modelrun_before_get_many(search_params=None, **kwargs):
    if search_params is None:
        return
    filt = dict(name='user_id', op='eq', val=current_identity.id)
    search_params['filters'] = [filt]



@jwt_required()
def modelrun_before_delete(instance_id=None,**kwargs):
    modelrun = ModelRun.query.get(instance_id)
    if modelrun:
        if modelrun.resources:
          for resource in modelrun.resources:
            modelresource_before_delete(instance_id=resource.id)
            resource.delete()
        if modelrun.progress_events:
          for event in modelrun.progress_events:
            event.delete()


modelrun_preprocessors = {
    'GET_SINGLE':[
        modelrun_before_get
    ],
    'GET_MANY':[
        modelrun_before_get_many
    ],
    'POST': [
        modelrun_before_post
    ],
    'DELETE_SINGLE':[
        modelrun_before_delete
    ]
}
