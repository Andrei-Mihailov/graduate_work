## Сервис лояльности
# Описание основных компонентов

auth - отвечает за аутентификацию пользователей. Стек: FastApi, Redis, Postgres
admin - отвечает за наполнение данными базы по работе с промокодами. Стек: Django, Redis, Postgres
loyalty - отвечает за применение промокодов пользователями. Стек: FastApi, Redis, Postgres

Промокоды назначаются конкретному пользователю или группе (только для зарегистрированных). Информация о зарегистрованных пользователях и их статусе (активный\удален\заблокирован) синхронизируется между сервисами лояльности и аутентификации посредстовм брокера сообщений RabbitMQ. 

Тесты - pytest
Логирование - sentry

# Функциональные требования
Купить платную версию за N рублей.
Купить платную версию за 0 рублей (по сути триал).
Сделать скидку M% на покупку платной версии.
Сделать промокод на определенный срок.
Сделать одноразовый промокод.
Сделать многоразовый промокод.
Сделать "применение" промокода со стороны администратора.
Уметь отслеживать, почему именно не прошел промокод.
* Сделать генератор промокодов.
* Сделать отмену применения промокода, если оплата не прошла

# Не функционаные требования
Производительность - 
Безопасность - 
Надежность - 
Масштабируемость - 

Время отклика - 200 мск
Количество пользователей - 

Комментарии: Персональные данные в auth-сервисе, что позволяет следить только за одним местом хранения. Два контейнера с бд - отдельно для аутентификации, отдельно для лояльности, позволяет распределить нагрузку и повысить отказоустойчивость системы. Работа компоненов организуется через docker-compose.

# Работа с сервисом
loyalty-api:

```
/apply_promocode?promocode_id=5&tariff=1 - применить промокод
/get_active_promocodes - получить список активных промокодов
/use_promocode?promocode_id=200&tariff=1 - покупка тарифа по промокоду
/cancel_apply_promocode?promocode_id=5
```

auth-api:
```
/login - аутентификация
/user_registration - регистрация
/logout - выход
/refresh_token - обновление рефреш токена
/delete - удаление из системы
```
