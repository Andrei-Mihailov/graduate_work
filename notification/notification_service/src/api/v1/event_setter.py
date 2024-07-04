from http import HTTPStatus

from fastapi import APIRouter, Depends

from models.models import RequestEventModel
from services.broker_service import BrokerService, get_broker_service
from services.user_service import UserService, get_user_service


router = APIRouter()


@router.post(
        "/send-notification/email",
        status_code=HTTPStatus.ACCEPTED,
        summary="Отправка уведомления",
        description="Отправка уведомлений одному или группе пользователей",
        tags=["Уведомление"]
)
async def send_data_to_queue(
    event: RequestEventModel,
    broker_service: BrokerService = Depends(get_broker_service),
    user_service: UserService = Depends(get_user_service)
):
    print(event)
    if event.type_event == 'personal':
        user = await user_service.get_user_by_id(id=event.recipient)
        if not user:
            return HTTPStatus.NOT_FOUND
        await broker_service.put_one_message_to_queue(event, user)
    else:
        user_list = await user_service.get_users(user_list=event.recipient)
        if not user_list:
            return HTTPStatus.NOT_FOUND
        await broker_service.put_many_message_to_queue(event, user_list)

    return HTTPStatus.ACCEPTED
